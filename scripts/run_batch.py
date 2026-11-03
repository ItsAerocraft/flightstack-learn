from sim.sim_trial import run_trial
from analysis.analysis_metrics import compute_metrics
from configs.config_paths import SUMMARY_CSV

import os, csv
import numpy as np
import asyncio

SEEDS = list(range(3, 203)) # do not use test seeds 1 and 2

async def main():
    fieldnames = [
        "seed", 
        "wind_speed", "wind_dir", 
        "mass_factor", "inertia_factor",
        "surge_period", "direction_swing_period",
        "status", "clean", "runtime", "path",
        "rms_m"
        ]
    
    if not os.path.exists(SUMMARY_CSV):
        os.makedirs(os.path.dirname(SUMMARY_CSV), exist_ok=True)
        with open(SUMMARY_CSV, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

    finished_seeds = set()
    if os.path.exists(SUMMARY_CSV):
        with open(SUMMARY_CSV, mode="r", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("seed"):
                    finished_seeds.add(int(row["seed"]))
    
    for seed in SEEDS:
        if seed in finished_seeds:
            print(f"Skipping seed {seed}: already exists in summary.csv")
            continue
    
        result = await run_trial(seed)

        if result["status"] == "ok":
            save_path_npz = result["path"]
            result["rms_m"] = compute_metrics(save_path_npz)["horizontal_rms"]

        else:
            result["rms_m"] = np.nan

        with open(SUMMARY_CSV, mode="a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writerow(result)

if __name__ == "__main__":
    asyncio.run(main())