import os
import numpy as np
import matplotlib.pyplot as plt

from configs.config_paths import TRAJ_LOG, FIG_DIR
from analysis.analysis_metrics import compute_metrics

data_path = TRAJ_LOG

data_path_rms_output = compute_metrics(data_path)

horizontal_rms = data_path_rms_output["horizontal_rms"]
max_horizontal_error = data_path_rms_output["max_horizontal_error"]
vertical_rms = data_path_rms_output["vertical_rms"]
lateness = data_path_rms_output["lateness"]
nan_rows = data_path_rms_output["nan_rows"]
pos_des = data_path_rms_output["pos_des"]
pos_act = data_path_rms_output["pos_act"]

print("=== Flight Trajectory Analysis ===")
print(f"Horizontal RMS (Masked):     {horizontal_rms:.4f} m")
print(f"Max Horizontal Error (Masked):{max_horizontal_error:.4f} m")
print(f"Vertical RMS:                 {vertical_rms:.4f} m")
print(f"Lateness Mean:                {np.mean(lateness) * 1000:.2f} ms")
print(f"Lateness Max:                 {np.max(lateness) * 1000:.2f} ms")
print(f"Number of NaN rows in pos_act: {nan_rows} (Expected: 0)")

plt.figure(figsize=(6, 6))

plt.plot(pos_des[:, 1], pos_des[:, 0], 'r--', label="Desired Path")
plt.plot(pos_act[:, 1], pos_act[:, 0], 'b-', label="Actual Path")

plt.xlabel("East (m)")
plt.ylabel("North (m)")
plt.title(f"Top-Down Path Profile\nHorizontal RMS: {horizontal_rms:.3f}m")
plt.gca().set_aspect('equal')
plt.grid(True, linestyle=":")
plt.legend()

plt.tight_layout()

os.makedirs(FIG_DIR, exist_ok=True)
fig_output_path = FIG_DIR / "fig1_path.png"
plt.savefig(fig_output_path, dpi=200)
print(f"\n[V] Visual metrics charts exported to: {fig_output_path}")
