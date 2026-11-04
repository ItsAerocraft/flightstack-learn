import numpy as np

from dataclasses import dataclass

@dataclass(frozen = True) # each run has an unchanging path
class Figure8:
    # for passing TRAJ, drone requies r, v, a (and sometimes j) inputs

    A: float # (m) [amplitude of lemniscate]
    omega: float # (rad s^-1) [angular rate]
    h: float # (m) [altitude, with z = -h]

    def position(self, t: float) -> np.ndarray:
        '''
        Computes the desired NED position on the figure-8 (lemniscate) path at time t.

        Args:
            [t]: trajectory time (s).

        Returns:
            3-element NED position vector (m), ([x], [y], [z]).

        Derived from a figure-8 (lemniscate of Gerono) parameterization, with x
        completing one cycle per loop and y completing two, at fixed altitude z = -h.
        '''
        x = self.A * np.sin(self.omega * t)
        y = 0.5 * self.A * np.sin(2.0 * self.omega * t)
        z = - self.h

        return np.array([x, y, z])

    def velocity(self, t:float) -> np.ndarray:
        '''
        Computes the desired NED velocity on the figure-8 path at time t.

        Args:
            [t]: trajectory time (s).

        Returns:
            3-element NED velocity vector (m s^-1), ([vx], [vy], [vz]).

        Derived by differentiating the figure-8 position parameterization with
        respect to time; vertical rate is zero since altitude is constant.
        '''
        vx = self.A * self.omega * np.cos(self.omega * t)
        vy = self.A * self.omega * np.cos(2.0 * self.omega * t)
        vz = 0.0

        return np.array([vx, vy, vz])

    def acceleration(self, t:float) -> np.ndarray:
        '''
        Computes the desired NED acceleration on the figure-8 path at time t.

        Args:
            [t]: trajectory time (s).

        Returns:
            3-element NED acceleration vector (m s^-2), ([ax], [ay], [az]).

        Derived by differentiating the figure-8 velocity parameterization with
        respect to time; vertical acceleration is zero since altitude is constant.
        '''
        ax = -self.A * (self.omega ** 2) * np.sin(self.omega * t)
        ay = - 2.0 * self.A * (self.omega ** 2) * np.sin(2.0 * self.omega * t)
        az = 0

        return np.array([ax, ay, az])

    def jerk(self, t:float) -> np.ndarray:
        '''
        Computes the desired NED jerk on the figure-8 path at time t.

        Args:
            [t]: trajectory time (s).

        Returns:
            3-element NED jerk vector (m s^-3), ([jx], [jy], [jz]).

        Derived by differentiating the figure-8 acceleration parameterization
        with respect to time; vertical jerk is zero since altitude is constant.
        '''
        jx = -(self.A * (self.omega ** 3)) * np.cos(self.omega * t)
        jy = -(4.0 * self.A * (self.omega ** 3)) * np.cos(2.0 * self.omega * t)
        jz = 0.0

        return np.array([jx, jy, jz])

    def yaw(self, t: float) -> float:
        '''
        Computes the desired heading on the figure-8 path at time t.

        Args:
            [t]: trajectory time (s).

        Returns:
            Desired yaw angle (deg); always 0.0, since this trajectory does
            not command a yaw change.
        '''
        return 0.0