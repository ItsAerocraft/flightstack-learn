import numpy as np
from dataclasses import dataclass

# 2. Define range constraints as module constants
WIND_SPEED_MIN = 0.0
WIND_SPEED_MAX = 6.0              # (m/s) [Maximum wind magnitude limit]

WIND_DIR_MIN = 0.0
WIND_DIR_MAX = 360.0              # (deg) [Wind direction measured 0 deg along east, pointing towards east]

MASS_FACTOR_MIN = 0.8
MASS_FACTOR_MAX = 1.2             # Scaling bounds for aircraft dry mass variance

INERTIA_FACTOR_MIN = 0.8
INERTIA_FACTOR_MAX = 1.2          # Scaling bounds for inertial tensors

SURGE_PERIOD_MIN = 5 
SURGE_PERIOD_MAX = 12             # (s) [gust wind surge time]

DIRECTION_SWING_PERIOD_MIN = 4
DIRECTION_SWING_PERIOD_MAX = 10   # (s) [gust wind direction swing time]

GUST_INTENSITY = 0.15             # fraction of mean wind

@dataclass(frozen=True)
class RunParams:
    seed: int
    wind_speed: float
    wind_dir: float
    mass_factor: float
    inertia_factor: float
    surge_period: float
    direction_swing_period: float

def draw_params(seed: int) -> RunParams:
    '''
    Draws one set of randomized trial parameters from the configured ranges,
    reproducibly from seed.

    Args:
        [seed]: integer seed for the random number generator.

    Returns:
        RunParams with wind_speed, wind_dir, mass_factor, inertia_factor,
        surge_period, and direction_swing_period drawn uniformly from their
        respective MIN/MAX module constants.

    Using a fresh np.random.default_rng(seed) per call means the same seed
    always reproduces the same drawn parameters.
    '''
    rng = np.random.default_rng(seed)
    
    wind_speed = float(rng.uniform(WIND_SPEED_MIN, WIND_SPEED_MAX))
    wind_dir = float(rng.uniform(WIND_DIR_MIN, WIND_DIR_MAX))
    mass_factor = float(rng.uniform(MASS_FACTOR_MIN, MASS_FACTOR_MAX))
    inertia_factor = float(rng.uniform(INERTIA_FACTOR_MIN, INERTIA_FACTOR_MAX))

    surge_period = rng.uniform(SURGE_PERIOD_MIN, SURGE_PERIOD_MAX)
    direction_swing_period = rng.uniform(DIRECTION_SWING_PERIOD_MIN, DIRECTION_SWING_PERIOD_MAX)
    
    return RunParams(
        seed=seed,
        wind_speed=wind_speed,
        wind_dir=wind_dir,
        mass_factor=mass_factor,
        inertia_factor=inertia_factor,
        surge_period=surge_period,
        direction_swing_period=direction_swing_period
    )
