from sim.sim_trial import run_trial
from analysis.analysis_metrics import compute_metrics

import numpy as np
import asyncio

TEST_SEED = 4

#  58.6 ± 0.729 cm

async def main():
    rms_array = []
    dropped = 0

    for i in range(5):
        result = await run_trial(TEST_SEED, run_name=f"noise_{TEST_SEED:03d}_r{i}", gz_seed=(i + 100))
        
        if result["status"] == "ok":
            save_path_npz = result["path"]
            rms_val = 100 * compute_metrics(save_path_npz)["horizontal_rms"]

            rms_array.append(rms_val)

        else:
            dropped += 1

    average = np.mean(rms_array)
    std = np.std(rms_array, ddof=1)

    print(f"Completed 5 runs of seed {TEST_SEED}, dropped {dropped} runs.")
    print(f"Final rms mean = {average:.3g} ± {std:.3g} cm")


if __name__ == "__main__":
    asyncio.run(main())
