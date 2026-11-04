from mavsdk import System

async def connect():
    '''
    Connects to a running PX4 instance over MAVSDK and waits until it reports a
    healthy position estimate and is ready to arm.

    Returns:
        Connected mavsdk.System instance, ready for arming and offboard control.

    Blocks on two async health streams in sequence: first for the MAVSDK
    connection itself, then for EKF/GPS/barometer/power checks to clear.
    '''
    drone = System()
    print("Connecting...")
    await drone.connect(system_address="udpin://0.0.0.0:14540")

    print("Waiting for connection...")
    async for connection_state in drone.core.connection_state():
        if connection_state.is_connected:
            print("[V] Connected to PX4!")
            break

    print("Waiting for EKF (position estimate)...")
    async for health in drone.telemetry.health():

       # preflight check booleans
        positions_ok = health.is_global_position_ok and health.is_home_position_ok
        system_ready = health.is_armable

        if positions_ok and system_ready:
            print("[V] All systems clear: EKF, Barometer, Power, and GCS links are OK!")
            break

    return drone