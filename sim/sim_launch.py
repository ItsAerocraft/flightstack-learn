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
    """Run one short command inside WSL and wait for it to finish."""
    return subprocess.run(WSL + [cmd], capture_output=True, text=True, timeout=timeout)


def sim_is_running():
    """True if any px4 or Gazebo process is still alive in WSL."""
    result = wsl_run(f"pgrep -x px4; pgrep -f {GZ_PATTERN}")
    return result.stdout.strip() != ""


def start_sim(model="x500_mc", world="flightstack", headless=True, log_name="px4"):
    """Start PX4 + Gazebo in WSL in the background and return the Popen handle.

    Returns as soon as the process starts; connect() is what waits until the
    drone is ready to fly.
    """
    if sim_is_running():
        stop_sim(None)  # leftovers from a crashed run would clash with this one

    env = f"PX4_SYS_AUTOSTART={AIRFRAME} PX4_SIM_MODEL=gz_{model} PX4_GZ_WORLD={world}"
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
    """Stop PX4 + Gazebo: ask nicely, wait, force it, then check nothing is left.

    Returns True if no px4 or Gazebo processes remain.
    """
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
