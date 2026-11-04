import asyncio
import os

import numpy as np

from mavsdk.offboard import PositionNedYaw, VelocityNedYaw, OffboardError
from mavsdk.action import ActionError

from flight.flight_telemetry import stream_telemetry
from flight.flight_trajectory import Figure8
from flight.flight_warp import warped_time, smoothstep, smoothstep_rate
from flight.flight_state import State
from flight.flight_connect import connect
from configs.config_paths import TRAJ_DIR, TRAJ_LOG

# Parameters
TRAJ = Figure8(A = 1.0, omega = 0.3, h = 2.0) # size of figure8 is {2 * (A)} m by {A} m, flight at {h} m of altitude (z = -h)

RAMP_DURATION = 3.0 # (s) [ramp speeds up the drone smoothly from 0 to {RAMP_DURATION} seconds]
LOOP_RATE_HZ = 50.0 # (Hz) [frequency of targets sent to PX4 drone]
LOOP_PERIOD = (1.0 / LOOP_RATE_HZ) # (s) period of above loop rate]

LOOP_NUMBER = 3 # (~) [number of loops]
DURATION = (LOOP_NUMBER * 2 * np.pi) / TRAJ.omega + (RAMP_DURATION / 2) # (s) [fly for {duration} seconds, one lap is 2pi / omega s]
SETTLE_TIME = 20 # (s) [time for drone to settle until wind is turned on in gazebo]

async def fly_figure8(save_path=TRAJ_LOG, on_airborne=None):
    '''
    Connects to PX4, arms, climbs to altitude, flies the ramped figure-8
    trajectory in offboard mode, then lands and saves the logged flight data.

    Args:
        [save_path]: filesystem path to write the trajectory log (.npz) to.
        [on_airborne]: optional zero-argument callback invoked once the drone
            reaches cruising altitude (e.g. to turn on wind).

    Returns:
        None. Logs desired/actual position, velocity, acceleration, and loop
        timing arrays to save_path, and lands the drone even if the loop is
        interrupted or raises.

    Loop rate is held at LOOP_RATE_HZ by sleeping out the remaining tick
    period each iteration; a missed deadline is counted and the schedule is
    reset instead of allowed to accumulate drift.
    '''
    state = State()
    
    t_log = []
    t_traj_log = []
    pos_des_log = []
    vel_des_log = []
    acc_des_log = []
    pos_act_log = []
    vel_act_log = []
    lateness_log = []

    drone = await connect()


    # spawn background telemetry worker
    await drone.telemetry.set_rate_position_velocity_ned(LOOP_RATE_HZ)
    bg_telemetry_task = asyncio.create_task(stream_telemetry(drone, state))
    
    # use asyncio sleep to block until receive first update (initial flight coordinates)
    print("Waiting for initial telemetry streaming sync...")
    while state.n_updates == 0:
        await asyncio.sleep(0.1)

    origin = np.array([state.pos[0], state.pos[1], 0.0])
    print(f"Flight reference origin frame locked at: {origin}")

    async for msg in drone.telemetry.attitude_euler(): 
        yaw0 = msg.yaw_deg
        break

    print(f"Heading locked at: {yaw0:1f} deg")

    n_missed = 0
    n_ticks = 0

    try:
        print("Arming drone...")
        await drone.action.arm()

        # place drone at a safe static position target before engaging offboard mode
        print("Seeding initial offboard hover setpoint...")
        await drone.offboard.set_position_velocity_ned(
            PositionNedYaw(origin[0], origin[1], -TRAJ.h, yaw0),
            VelocityNedYaw(0.0, 0.0, 0.0, yaw0)
        )

        try:
            print("Engaging offboard automatic guidance tracking mode...")
            await drone.offboard.start()
        except OffboardError as e:
            print(f"Offboard Mode Initialization Failure: {e}")
            print("Disarming and aborting sequence.")
            await drone.action.disarm()
            return

        # Direct vertical climb processing loop
        print(f"Climbing autonomously to cruising altitude (-{TRAJ.h}m)...")
        while state.pos[2] > -(TRAJ.h - 0.1):
            await asyncio.sleep(0.1)

        if on_airborne is not None:
            on_airborne()
        
        print("Target altitude reached")
        await asyncio.sleep(SETTLE_TIME) # allow drone to settle

        loop = asyncio.get_running_loop()
        t0 = loop.time()
        next_tick = t0

        print(f"Starting {LOOP_RATE_HZ}Hz figure-8 trajectory tracking loop...")
        
        while True:
            lateness = loop.time() - next_tick
            now = loop.time() - t0
            
            if now >= DURATION:
                break
                
            n_ticks += 1
            
            t_traj = warped_time(now, RAMP_DURATION)
            pos = TRAJ.position(t_traj)
            vel = TRAJ.velocity(t_traj)
            acc = TRAJ.acceleration(t_traj)
            
            ramp = smoothstep(now, RAMP_DURATION)
            ramp_rate = smoothstep_rate(now, RAMP_DURATION)
            
            vel_scaled = vel * ramp
            acc_scaled = acc * (ramp ** 2) + vel * ramp_rate
            
            # Shift trajectory tracking to start from the origin, so that no unexpected lurching occurs
            pos_cmd = pos + origin

            await drone.offboard.set_position_velocity_ned(
                PositionNedYaw(pos_cmd[0], pos_cmd[1], pos_cmd[2], yaw0),
                VelocityNedYaw(vel_scaled[0], vel_scaled[1], vel_scaled[2], yaw0)
            )
            

            t_log.append(now)
            t_traj_log.append(t_traj)
            pos_des_log.append(pos_cmd)
            vel_des_log.append(vel_scaled)
            acc_des_log.append(acc_scaled)
            pos_act_log.append(state.pos.copy())
            vel_act_log.append(state.vel.copy())
            lateness_log.append(lateness)
            
            next_tick += LOOP_PERIOD
            delay = next_tick - loop.time()
            if delay < 0:
                n_missed += 1
                next_tick = loop.time()
                
            await asyncio.sleep(max(delay, 0))

    finally:
        print("\nTrajectory loop terminated. Starting safe hardware recovery routines...")
        
        try:
            await drone.offboard.stop()
        except OffboardError:
            pass

        print("Landing drone safely...")

        try:
            await drone.action.land()
        except ActionError as e:
            print(f"Landing error: {e}")

        bg_telemetry_task.cancel()
        try:
            await bg_telemetry_task
        except asyncio.CancelledError:
            pass

        if t_log: # if t_log has contents
            os.makedirs(TRAJ_DIR, exist_ok=True)
            np.savez(
                save_path,
                t=np.array(t_log),
                t_traj=np.array(t_traj_log),
                pos_des=np.array(pos_des_log),
                vel_des=np.array(vel_des_log),
                acc_des=np.array(acc_des_log),
                pos_act=np.array(pos_act_log),
                vel_act=np.array(vel_act_log),
                lateness=np.array(lateness_log),
                ramp_duration=RAMP_DURATION,
                rate_hz=LOOP_RATE_HZ,
                A=TRAJ.A,
                omega=TRAJ.omega,
                h=TRAJ.h

            )
            print(f"Loop finished. Data saved to {save_path}")

        flight_duration = t_log[-1] if (t_log and t_log[-1] != 0) else DURATION
        avg_rate = n_ticks / flight_duration
        
        print(f"--- Execution Summary ---")
        print(f"Total Ticks:     {n_ticks}")
        print(f"Missed Ticks:    {n_missed}")
        print(f"Average Rate:    {avg_rate:.2f} Hz")

if __name__ == "__main__":
    asyncio.run(fly_figure8())

