from configs.config_params import draw_params

from sim.sim_model import write_model
from sim.sim_world import write_world, set_wind
from sim.sim_launch import start_sim, stop_sim

from flight.flight_figure8 import fly_figure8

from configs.config_paths import TRAJ_DIR

import subprocess
import asyncio
import time

from dataclasses import asdict

RUN_TIMEOUT = 180

async def run_trial(seed, timeout = RUN_TIMEOUT):

    start_time = time.monotonic()

    params = draw_params(seed)
    write_model(params.mass_factor, params.inertia_factor)
    write_world(0.0, 0.0) # no wind on startup

    # kill stale running tasks to stop hang and interrupting overnight/afk runs (AI)
    subprocess.run(["taskkill", "/F", "/IM", "mavsdk_server.exe"], capture_output=True) 

    proc = start_sim(log_name=f"seed_{seed:03d}")

    try:
        save_path = TRAJ_DIR / f"seed_{seed:03d}.npz"

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
