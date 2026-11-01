import numpy as np

from dataclasses import dataclass, field

@dataclass(slots=True) # typos raise AttributeError instead of creating a new unwanted attribute
class State:
    # avoid mutable default bugs, so that new instances get a new independent numpy array
    pos: np.ndarray = field(default_factory=lambda: np.full(3, np.nan)) # (m) [NED position of drone]
    vel: np.ndarray = field(default_factory=lambda: np.full(3, np.nan)) # (m s^-1) [NED velocity of drone]
    euler: np.ndarray = field(default_factory=lambda: np.full(3, np.nan)) #(deg) [euler angles of drone attitude]

    t: float = np.nan # (s) [age of the data, so the drone would have moved in this duration by the time message arrives]

    n_updates: int = 0 # (~) [count of position/velocity telemetry messages received from PX4]
