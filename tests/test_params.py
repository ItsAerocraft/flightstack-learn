
from configs.config_params import (
    draw_params,
    WIND_SPEED_MIN, WIND_SPEED_MAX,
    WIND_DIR_MIN, WIND_DIR_MAX,
    MASS_FACTOR_MIN, MASS_FACTOR_MAX,
    INERTIA_FACTOR_MIN, INERTIA_FACTOR_MAX,
    SURGE_PERIOD_MIN, SURGE_PERIOD_MAX,
    DIRECTION_SWING_PERIOD_MIN, DIRECTION_SWING_PERIOD_MAX
)

SEED_1 = 3
SEED_2 = 5

NUM_SEEDS = 200

def test_same_seed_gives_equal_objects():
    object1 = draw_params(SEED_1)
    object2 = draw_params(SEED_1)

    assert object1 == object2

def test_different_seeds_give_different_objects():
    object1 = draw_params(SEED_1)
    object2 = draw_params(SEED_2)

    assert object1 != object2

def test_loop_seeds_values_in_range():
    for seed in range(NUM_SEEDS):
        params = draw_params(seed)
        
        assert params.seed == seed
        assert WIND_SPEED_MIN <= params.wind_speed <= WIND_SPEED_MAX
        assert WIND_DIR_MIN <= params.wind_dir <= WIND_DIR_MAX
        assert MASS_FACTOR_MIN <= params.mass_factor <= MASS_FACTOR_MAX
        assert INERTIA_FACTOR_MIN <= params.inertia_factor <= INERTIA_FACTOR_MAX
        assert SURGE_PERIOD_MIN <= params.surge_period <= SURGE_PERIOD_MAX
        assert DIRECTION_SWING_PERIOD_MIN <= params.direction_swing_period <= DIRECTION_SWING_PERIOD_MAX


        

