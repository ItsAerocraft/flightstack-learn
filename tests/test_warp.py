import numpy as np

import pytest

from flight.flight_figure8 import RAMP_DURATION, TRAJ
from flight.flight_warp import smoothstep, smoothstep_rate, warped_time

TEST_TIMES = [0.5, 1.5, 2.5, 4.0]

def _central_difference(fn, t, h=1e-6):
    return (fn(t + h) - fn(t - h)) / (2 * h)

@pytest.mark.parametrize("t", TEST_TIMES)
def test_smoothstep_rate_matches_numerical_derivative_of_smoothstep(t):
    num = _central_difference(lambda t_val: smoothstep(t_val, RAMP_DURATION), t)
    ana = smoothstep_rate(t, RAMP_DURATION)
    np.testing.assert_allclose(ana, num, atol=1e-5, rtol=1e-5)

@pytest.mark.parametrize("t", TEST_TIMES)
def test_numerical_derivative_of_warped_time_matches_smoothstep(t):
    num = _central_difference(lambda t_val: warped_time(t_val, RAMP_DURATION), t)
    ana = smoothstep(t, RAMP_DURATION)
    np.testing.assert_allclose(ana, num, atol=1e-5, rtol=1e-5)

@pytest.mark.parametrize("t", TEST_TIMES)
def test_numerical_derivative_of_warped_position_matches_warped_velocity(t):
    def pos(t_val):
        return TRAJ.position(warped_time(t_val, RAMP_DURATION))

    num = _central_difference(pos, t)
    ana = TRAJ.velocity(warped_time(t, RAMP_DURATION)) * smoothstep(t, RAMP_DURATION)
    np.testing.assert_allclose(ana, num, atol=1e-5, rtol=1e-5)

@pytest.mark.parametrize("t", TEST_TIMES)
def test_numerical_derivative_of_warped_velocity_matches_true_acceleration(t):
    def vel(t_val): 
        return TRAJ.velocity(warped_time(t_val, RAMP_DURATION)) * smoothstep(t_val, RAMP_DURATION)

    num = _central_difference(vel, t)

    term1 = TRAJ.acceleration(warped_time(t, RAMP_DURATION)) * (smoothstep(t, RAMP_DURATION) ** 2) 
    term2 = TRAJ.velocity(warped_time(t, RAMP_DURATION)) * smoothstep_rate(t, RAMP_DURATION)
    ana = term1 + term2

    np.testing.assert_allclose(ana, num, atol=1e-5, rtol=1e-5)