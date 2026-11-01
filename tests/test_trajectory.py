import numpy as np
import pytest
from flight.flight_trajectory import Figure8

TRAJ = Figure8(A=1.0, omega=1.0, h=2.0)

TEST_TIMES = [0.0, 0.3, 1.7, 5.0, 12.34]

def _central_difference(fn, t, h=1e-6):
    return (fn(t + h) - fn(t - h)) / (2 * h)

@pytest.mark.parametrize("t", TEST_TIMES)
def test_velocity_matches_numerical_derivative_of_position(t):
    num = _central_difference(TRAJ.position, t)
    ana = TRAJ.velocity(t)
    np.testing.assert_allclose(ana, num, atol = 1e-5, rtol = 1e-5)

@pytest.mark.parametrize("t", TEST_TIMES)
def test_acceleration_matches_numerical_derivative_of_velocity(t):
    num = _central_difference(TRAJ.velocity, t)
    ana = TRAJ.acceleration(t)
    np.testing.assert_allclose(ana, num, atol = 1e-5, rtol = 1e-5)

@pytest.mark.parametrize("t", TEST_TIMES)
def test_jerk_matches_numerical_derivative_of_acceleration(t):
    num = _central_difference(TRAJ.acceleration, t)
    ana = TRAJ.jerk(t)
    np.testing.assert_allclose(ana, num, atol = 1e-5, rtol = 1e-5)

def test_shapes_are_3_vectors():
    for t in np.linspace(0, 10, 50):
        assert TRAJ.position(t).shape == (3,)
        assert TRAJ.velocity(t).shape == (3,)
        assert TRAJ.acceleration(t).shape == (3,)
        assert TRAJ.jerk(t).shape == (3,)

def test_altitude_is_constant():
    for t in np.linspace(0, 10, 50):
        assert TRAJ.position(t)[2] == pytest.approx(-TRAJ.h)

def test_peak_acceleration_matches_2Aw2():
    # peak |a| should approach 2 * A*omega ** 2
    t_vals = np.linspace(0, 2*np.pi/TRAJ.omega, 2000)
    peak = max(np.linalg.norm(TRAJ.acceleration(t)) for t in t_vals)
    assert peak == pytest.approx(2 * TRAJ.A * TRAJ.omega**2, rel = 1e-1)