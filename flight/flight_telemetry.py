import numpy as np

import asyncio
import time

from flight.flight_state import State

async def stream_telemetry(drone, state):
    '''
    Continuously updates a shared State object with each new NED position/velocity
    message streamed from PX4.

    Args:
        [drone]: connected mavsdk.System instance to stream telemetry from.
        [state]: State object to update in place with each incoming message.

    Returns:
        None. Updates state.pos, state.vel, state.t, and state.n_updates in
        place; runs forever as a background task until cancelled.
    '''
    async for msg in drone.telemetry.position_velocity_ned():

        state.pos = np.array([
            msg.position.north_m,
            msg.position.east_m,
            msg.position.down_m
        ])

        state.vel = np.array([
            msg.velocity.north_m_s,
            msg.velocity.east_m_s,
            msg.velocity.down_m_s
        ])

        state.t = time.monotonic()

        state.n_updates += 1
