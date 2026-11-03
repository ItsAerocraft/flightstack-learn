from pathlib import Path

RESULTS_DIR = Path("z_results")

TRAJ_DIR = RESULTS_DIR / "trajectories"   # one .npz per flight
FIG_DIR = RESULTS_DIR / "figures"         # report figures
LOG_DIR = RESULTS_DIR / "logs"            # PX4 console output per launch
SUMMARY_CSV = RESULTS_DIR / "summary.csv"
BOOTSTRAP_CSV = RESULTS_DIR / "bootstrap.csv"

TRAJ_LOG = TRAJ_DIR / "trajectory_log.npz"  # single-flight log
