def smoothstep(t: float, r: float) -> float:
    if t <= 0.0:
        return 0.0
    if t >= r:
        return 1.0
    
    tau = t / r
    return 3.0 * (tau ** 2) - 2.0 * (tau ** 3)

def smoothstep_rate(t: float, r: float) -> float:
    if t <= 0.0 or t >= r:
        return 0.0
    
    tau = t / r
    # rate of change of smoothstep ramp, in s^-1
    return (6.0 * tau * (1 - tau)) / r


def warped_time(t: float, r: float) -> float:
    if t <= 0.0:
        return 0.0
        
    if t >= r:
        # After the ramp, time advances normally, offset by the ramp's delay
        return t - (r * 0.5)
    
    tau = t / r
    # return time --> intregral of s curve * time
    progress_integral = (tau ** 3) - (0.5 * (tau ** 4))
    return progress_integral * r