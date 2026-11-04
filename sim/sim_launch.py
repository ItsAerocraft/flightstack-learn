# start_sim() / stop_sim() written with AI assistance (Claude, Anthropic), Oct 2026.
# I asked for help because starting and stopping PX4 + Gazebo inside WSL from
# Windows Python (subprocess, process cleanup) was new to me.

import subprocess
import time
from configs.config_paths import LOG_DIR

WSL = ["wsl.exe", "-d", "Ubuntu-24.04", "--", "bash", "-c"]
PX4_DIR = "~/PX4-Autopilot"
PX4_BIN = "./build/px4_sitl_default/bin/px4"
AIRFRAME = 4001  # stock x500 tuning in PX4, whatever model Gazebo spawns

# pkill/pgrep patterns: -x px4 matches only processes named exactly px4, and
# '[g]z sim' matches "gz sim" but not its own command line (see Step 3.4 notes)
GZ_PATTERN = "'[g]z sim'"


def wsl_run(cmd, timeout=15):
    '''
    Runs one short command inside the WSL Ubuntu instance and waits for it to finish.

    Args:
        [cmd]: shell command string to run inside WSL via `bash -c`.
        [timeout]: maximum time to wait for the command to complete (s).

    Returns:
        subprocess.CompletedProcess with captured stdout/stderr and returncode.
    '''
    return subprocess.run(WSL + [cmd], capture_output=True, text=True, timeout=timeout)


def sim_is_running():
    '''
    Checks whether PX4 or Gazebo is still running inside WSL.

    Returns:
        True if any px4 or `gz sim` process is still alive, False otherwise.
    '''
    result = wsl_run(f"pgrep -x px4; pgrep -f {GZ_PATTERN}")
    return result.stdout.strip() != ""


def start_sim(model="x500_mc", world="flightstack", headless=True, log_name="px4", gz_seed=None):
    '''
    Starts PX4 and Gazebo inside WSL in the background and returns immediately.

    Args:
        [model]: Gazebo model name to spawn (matches the name written by write_model).
        [world]: Gazebo world name to load (matches the name written by write_world).
        [headless]: if True, runs Gazebo without a GUI.
        [log_name]: filename (without extension) to write PX4's console output to.
        [gz_seed]: optional seed for Gazebo's render engine, for reproducible gusts.

    Returns:
        subprocess.Popen handle for the WSL wrapper process, with a .log_file
        attribute for the open PX4 log file.

    Clears any leftover px4/Gazebo processes from a crashed prior run before
    launching; does not wait for PX4 to be flight-ready, connect() does that.
    '''
    if sim_is_running():
        stop_sim(None)  # leftovers from a crashed run would clash with this one

    env = f"PX4_SYS_AUTOSTART={AIRFRAME} PX4_SIM_MODEL=gz_{model} PX4_GZ_WORLD={world}"

    if gz_seed is not None:
        env += f" PX4_GZ_SIM_RENDER_ENGINE='ogre2 --seed {gz_seed}'"

    if headless:
        env = "HEADLESS=1 " + env
    # -d: no interactive pxh> shell, since nobody is typing into it
    cmd = f"cd {PX4_DIR} && {env} exec {PX4_BIN} -d"

    # PX4 prints a lot; send it to a file so a full pipe can never block it
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = open(LOG_DIR / f"{log_name}.log", "w")
    proc = subprocess.Popen(WSL + [cmd], stdout=log_file, stderr=subprocess.STDOUT)
    proc.log_file = log_file
    return proc


def stop_sim(proc, wait_s=10):
    '''
    Stops PX4 and Gazebo inside WSL, escalating from a clean shutdown to a forced kill.

    Args:
        [proc]: Popen handle returned by start_sim, or None to skip the
            Windows-side wait/kill.
        [wait_s]: time to wait for proc to exit after SIGTERM before killing it (s).

    Returns:
        True if no px4 or Gazebo processes remain afterward, False otherwise.

    Sends SIGTERM first so PX4 can shut down cleanly, waits for the wsl.exe
    wrapper to exit (killing it if it doesn't), then SIGKILLs anything still
    alive in Linux as a backstop.
    '''
    # 1. terminate: SIGTERM inside Linux, so PX4 gets to shut down cleanly
    wsl_run(f"pkill -TERM -x px4; pkill -TERM -f {GZ_PATTERN}")

    # 2. wait for the wsl.exe wrapper to exit, 3. kill it if it doesn't
    if proc is not None:
        try:
            proc.wait(timeout=wait_s)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        proc.log_file.close()

    # 4. backstop: anything still alive in Linux gets SIGKILL
    if sim_is_running():
        wsl_run(f"pkill -KILL -x px4; pkill -KILL -f {GZ_PATTERN}")
        time.sleep(1)

    return not sim_is_running()
