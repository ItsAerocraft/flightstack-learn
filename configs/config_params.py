import numpy as np
from dataclasses import dataclass

# 2. Define range constraints as module constants
WIND_SPEED_MIN = 0.0
WIND_SPEED_MAX = 6.0      # (m/s) [Maximum wind magnitude limit]

WIND_DIR_MIN = 0.0
WIND_DIR_MAX = 360.0       # (deg) [Wind direction measured 0 deg along east, pointing towards east]

MASS_FACTOR_MIN = 0.8
MASS_FACTOR_MAX = 1.2      # Scaling bounds for aircraft dry mass variance

INERTIA_FACTOR_MIN = 0.8
INERTIA_FACTOR_MAX = 1.2   # Scaling bounds for inertial tensors

@dataclass(frozen=True)
class RunParams:
    seed: int
    wind_speed: float
    wind_dir: float
    mass_factor: float
    inertia_factor: float

def draw_params(seed: int) -> RunParams:
    rng = np.random.default_rng(seed)
    
    wind_speed = float(rng.uniform(WIND_SPEED_MIN, WIND_SPEED_MAX))
    wind_dir = float(rng.uniform(WIND_DIR_MIN, WIND_DIR_MAX))
    mass_factor = float(rng.uniform(MASS_FACTOR_MIN, MASS_FACTOR_MAX))
    inertia_factor = float(rng.uniform(INERTIA_FACTOR_MIN, INERTIA_FACTOR_MAX))
    
    return RunParams(
        seed=seed,
        wind_speed=wind_speed,
        wind_dir=wind_dir,
        mass_factor=mass_factor,
        inertia_factor=inertia_factor
    )
