# AI use log

Code written by AI is listed here. Everything not listed I wrote myself; where I got hints or debugging help from AI, I still wrote the code.

| Step | File | What the AI did | What I did |
|------|------|-----------------|------------|
| 3.2 | `sim/sim_model.py` (`write_model`) | Wrote the function and explained how it works. I asked for help because I didn't know how to change the drone's parameters locally from Python. | Wrote the tests, ran the flight check, integrated it into the harness. |
| 3.3 | `sim/sim_world.py` (`write_world`), `enable_wind` in `sim/sim_model.py` | Told me where in the world file the wind goes and how to turn wind on for the drone in the XML (`<enable_wind>`). Reviewed my code with hints. | Learned ElementTree myself from the Python docs and wrote `write_world`, the `enable_wind` change and the tests. |
| 3.4 | `sim/sim_launch.py` (`start_sim`, `stop_sim`, `sim_is_running`) | Wrote the module, tested it with 3 launch/shutdown cycles, and explained how it works. I asked for help because starting and stopping PX4 + Gazebo inside WSL from Windows Python was new to me. | Wrote the flight script that uses it and ran the wind flight check. |
| 3.6 | `sim/sim_world.py` (`set_wind`) | Diagnosed why windy runs never took off (Gazebo's wind drag on the landed drone), tested turning wind on after takeoff, and wrote `set_wind` at my request. | Wrote the batch runner and wired `set_wind` into the run (calm takeoff, wind on after the climb). |
| 3.8 | `sim/sim_world.py` (gust plugins in `write_world`) | Found that a world naming any `<plugin>` loses PX4's default plugins, and told me to copy them from `server.config` (skipping its bare WindEffects) and which WindEffects sub-elements to add for gusts. Reviewed my code with hints. | Wrote the plugin copying, the configured WindEffects block, gust noise scaled with wind speed, and the plugin test. |
| 3.9 | `sim/sim_trial.py`, `sim/sim_launch.py`, `scripts/run_noise_floor.py`, `configs/config_params.py` | Wrote three lines for me directly: the `run_name` fallback, the ×100 m→cm conversion and `ddof=1`. Diagnosed that gusts repeated between runs: found the `PX4_GZ_SIM_RENDER_ENGINE` hook for passing `--seed` to Gazebo, then showed from the traces that the fixed sine periods (not the noise) drove the error, and suggested drawing the periods per seed. | Wrote the rest of the noise-floor script, the `gz_seed` plumbing, the per-seed surge and swing periods, and the period tests. |

AI used: Claude (Anthropic), Oct 2026.
