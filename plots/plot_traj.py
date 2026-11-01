import numpy as np
import matplotlib.pyplot as plt
from flight.flight_trajectory import Figure8

traj = Figure8(A = 1.0, omega = 1.0, h = 2.0)

t_vals = np.linspace(0, 2 * np.pi / traj.omega, 200)
positions = np.array([traj.position(t) for t in t_vals])

plt.figure(figsize=(8, 6))
plt.plot(positions[:, 0], positions[:, 1], label="Figure-8 Path")
plt.plot(0, 0, 'ro', label="Start (t = 0)")
plt.xlabel("X (North) / m")
plt.ylabel("Y (East) / m")
plt.axis('equal')
plt.grid(True)
plt.legend()
plt.title("Figure-8 Trajectory (Lemniscate of Gerono)")
plt.show()