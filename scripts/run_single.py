from sim.sim_model import write_model
from sim.sim_world import write_world
from sim.sim_launch import start_sim, stop_sim

from flight.flight_figure8 import fly_figure8

import asyncio

MASS_FACTOR = 1.0
INERTIA_FACTOR = 1.0
WIND_SPEED = 3.0
WIND_DIRECTION = 90.0

async def main():
    model = write_model(MASS_FACTOR, INERTIA_FACTOR)
    world = write_world(WIND_SPEED, WIND_DIRECTION)

    print("Launching PX4 and Gazebo...")

    proc = start_sim(model=model, world=world, headless=False)

    try:
        print("Starting flight control loop...")
        asyncio.run(await fly_figure8())

    finally:
        print("Shutting down PX4 simulation and cleaning up...")
        cleaned_up_bool = stop_sim(proc)
        print(f"Cleanup verification status: {cleaned_up_bool}")


if __name__ == "__main__":
    asyncio.run(main())