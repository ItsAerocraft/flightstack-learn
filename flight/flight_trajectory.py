import numpy as np

from dataclasses import dataclass

@dataclass(frozen = True) # each run has an unchanging path
class Figure8:
    # for passing TRAJ, drone requies r, v, a (and sometimes j) inputs

    A: float # (m) [amplitude of lemniscate]
    omega: float # (rad s^-1) [angular rate]
    h: float # (m) [altitude, with z = -h]

    def position(self, t: float) -> np.ndarray:
        x = self.A * np.sin(self.omega * t)
        y = 0.5 * self.A * np.sin(2.0 * self.omega * t)
        z = - self.h

        return np.array([x, y, z])

    def velocity(self, t:float) -> np.ndarray:
        vx = self.A * self.omega * np.cos(self.omega * t)
        vy = self.A * self.omega * np.cos(2.0 * self.omega * t)
        vz = 0.0

        return np.array([vx, vy, vz])

    def acceleration(self, t:float) -> np.ndarray:
        ax = -self.A * (self.omega ** 2) * np.sin(self.omega * t)
        ay = - 2.0 * self.A * (self.omega ** 2) * np.sin(2.0 * self.omega * t)
        az = 0

        return np.array([ax, ay, az])

    def jerk(self, t:float) -> np.ndarray:
        jx = -(self.A * (self.omega ** 3)) * np.cos(self.omega * t)
        jy = -(4.0 * self.A * (self.omega ** 3)) * np.cos(2.0 * self.omega * t)
        jz = 0.0

        return np.array([jx, jy, jz])

    def yaw(self, t: float) -> float:
        return 0.0