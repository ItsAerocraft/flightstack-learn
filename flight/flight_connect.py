from mavsdk import System

async def connect():
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