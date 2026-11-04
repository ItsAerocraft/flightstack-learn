def smoothstep(t: float, r: float) -> float:
    '''
    Computes the smoothstep ramp value at time t, rising smoothly from 0 to 1
    over the ramp duration r.

    Args:
        [t]: elapsed time since the start of the ramp (s).
        [r]: total duration of the ramp (s).

    Returns:
        Ramp progress fraction (unitless), 0 before the ramp starts and 1 once
        it completes.

    Uses the standard cubic Hermite smoothstep polynomial 3*tau^2 - 2*tau^3,
    where tau = t / r, so the ramp starts and ends with zero slope.
    '''
    if t <= 0.0:
        return 0.0
    if t >= r:
        return 1.0
    
    tau = t / r
    return 3.0 * (tau ** 2) - 2.0 * (tau ** 3)

def smoothstep_rate(t: float, r: float) -> float:
    '''
    Computes the time derivative of the smoothstep ramp at time t.

    Args:
        [t]: elapsed time since the start of the ramp (s).
        [r]: total duration of the ramp (s).

    Returns:
        Instantaneous rate of change of the smoothstep ramp (s^-1), zero
        outside the [0, r] ramp window.

    Derived by differentiating the smoothstep polynomial with respect to t.
    '''
    if t <= 0.0 or t >= r:
        return 0.0
    
    tau = t / r
    # rate of change of smoothstep ramp, in s^-1
    return (6.0 * tau * (1 - tau)) / r


def warped_time(t: float, r: float) -> float:
    '''
    Maps real elapsed time to a warped trajectory-time parameter that eases
    the drone into the trajectory instead of snapping to full speed instantly.

    Args:
        [t]: real elapsed time since the trajectory started (s).
        [r]: duration of the ramp-up window (s).

    Returns:
        Warped time to evaluate the trajectory at (s), equal to the integral
        of the smoothstep ramp up to t, offset so it matches real time after
        the ramp ends.

    Derived by integrating the smoothstep velocity profile over the ramp
    window, then shifting subsequent real time by the ramp's time deficit (r/2).
    '''
    if t <= 0.0:
        return 0.0
        
    if t >= r:
        # After the ramp, time advances normally, offset by the ramp's delay
        return t - (r * 0.5)
    
    tau = t / r
    # return time --> intregral of s curve * time
    progress_integral = (tau ** 3) - (0.5 * (tau ** 4))
    return progress_integral * r