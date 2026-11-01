import numpy as np
import matplotlib.pyplot as plt

from configs.config_paths import TRAJ_LOG

# Read the log
print("Running")
df = np.load(TRAJ_LOG)

plt.figure(figsize=(10, 5))
plt.plot(df["t"], df["vel_des"][ : , 0], label="Vx (North)")
plt.plot(df["t"], df["vel_des"][ : , 1], label="Vy (East)")
plt.axvline(x=df["ramp_duration"], color='r', linestyle='--', label=f"Ramp End ({df["ramp_duration"]} s)")

plt.xlabel("Real Wall-Clock Time / s")
plt.ylabel("Velocity / m s^-1")
plt.title("Velocity Ramp-In (No Jerk)")
plt.legend()
plt.grid(True)
plt.show()