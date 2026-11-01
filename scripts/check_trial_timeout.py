import asyncio

from sim.sim_trial import run_trial

async def main():
    print("--- Starting Simulation Trial 1 (Expects Timeout) ---")
    result_1 = await run_trial(seed=1, timeout=40)
    
    print(f"Run 1 Status: {result_1.get('status')}")
    print(f"Run 1 Clean Shutdown: {result_1.get('clean')}")
    
    print("\n--- Starting Simulation Trial 2 (Expects OK) ---")
    result_2 = await run_trial(seed=2)

    print(f"Run 2 Status: {result_2.get('status')}")
    print(f"Run 2 Clean Shutdown: {result_2.get('clean')}")


if __name__ == "__main__":
    asyncio.run(main())
