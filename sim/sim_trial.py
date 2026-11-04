from configs.config_params import draw_params

from sim.sim_model import write_model
from sim.sim_world import write_world, set_wind
from sim.sim_launch import start_sim, stop_sim

from flight.flight_figure8 import fly_figure8

from configs.config_paths import TRAJ_DIR
from configs.config_params import GUST_INTENSITY

import subprocess
import asyncio
import time

from dataclasses import asdict

RUN_TIMEOUT = 180

async def run_trial(seed, timeout=RUN_TIMEOUT, run_name=None, gz_seed=None):
    '''
    Runs one complete simulated flight trial: draws randomized parameters,
    writes the scaled model and gusting world, launches the sim, flies the
    figure-8, and tears everything down.

    Args:
        [seed]: seed used to draw RunParams (mass, inertia, wind, gust timing).
        [timeout]: maximum time to allow the flight loop to run before it is
            treated as timed out (s).
        [run_name]: name used for the PX4 log and trajectory .npz file;
            defaults to "seed_<seed>".
        [gz_seed]: seed for Gazebo's render engine; defaults to seed.

    Returns:
        Dict of the drawn RunParams fields plus status ("ok" / "timeout" /
        "error: ..."), clean (bool, whether teardown left no processes
        running), runtime (s), and path to the saved trajectory .npz.

    Wind is held at zero until on_airborne fires (the drone climbs through
    still air), after which the drawn wind_speed/wind_dir is applied; the
    simulation is always torn down in a finally block even if the flight
    loop raises or times out.
    '''
    if run_name is None:
        run_name = f"seed_{seed:03d}"

    if gz_seed is None:
        gz_seed = seed

    start_time = time.monotonic()

    params = draw_params(seed)
    write_model(params.mass_factor, params.inertia_factor)
    write_world(
        0.0, 0.0, 
        gust_scaled=(GUST_INTENSITY * params.wind_speed),
        surge_period=params.surge_period,
        direction_swing_period=params.direction_swing_period
    ) # no wind on startup except for gusting

    # kill stale running tasks to stop hang and interrupting overnight/afk runs (AI)
    subprocess.run(["taskkill", "/F", "/IM", "mavsdk_server.exe"], capture_output=True) 

    proc = start_sim(log_name=run_name, gz_seed=gz_seed)

    try:
        save_path = TRAJ_DIR / f"{run_name}.npz"

        wind_on = lambda: set_wind(params.wind_speed, params.wind_dir)
        await asyncio.wait_for(fly_figure8(save_path=save_path, on_airborne=wind_on), timeout=timeout)
        status = "ok"

    except asyncio.TimeoutError:
        status = "timeout"

    except Exception as e:
        status = f"error: {e!r}"


    finally:
        print("Cleaning up simulation processes...")
        clean = stop_sim(proc)

    end_time = time.monotonic()

    run_time = end_time - start_time

    result_dict = asdict(params)
    result_dict.update({
            "status": status,
            "clean": clean,
            "runtime": run_time,
            "path": str(save_path)
        })

    return result_dict
