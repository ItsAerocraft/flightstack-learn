import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from pathlib import Path
from configs.config_paths import FIG_DIR, SUMMARY_CSV
from analysis.analysis_metrics import compute_metrics


def plot_fig1(report=False):
    if not os.path.exists(SUMMARY_CSV):
            raise FileNotFoundError(
                f"Could not find {SUMMARY_CSV}. Make sure to run your batch simulation script first."
            )

    df = pd.read_csv(SUMMARY_CSV)
    
    seed_row = df[df["seed"] == 4]
    
    if seed_row.empty:
        raise ValueError("Seed 4 was not found in summary.csv tracking rows.")
        

    data_path = Path(seed_row.iloc[0]["path"])
    wind_speed = seed_row.iloc[0]["wind_speed"]
    mass_factor = seed_row.iloc[0]["mass_factor"]

    data_path_rms_output = compute_metrics(data_path)

    horizontal_rms = data_path_rms_output["horizontal_rms"]
    max_horizontal_error = data_path_rms_output["max_horizontal_error"]
    vertical_rms = data_path_rms_output["vertical_rms"]
    lateness = data_path_rms_output["lateness"]
    nan_rows = data_path_rms_output["nan_rows"]
    pos_des = data_path_rms_output["pos_des"]
    pos_act = data_path_rms_output["pos_act"]

    if not report:
        print("=== Flight Trajectory Analysis ===")
        print(f"Horizontal RMS (Masked):     {horizontal_rms:.4f} m")
        print(f"Max Horizontal Error (Masked):{max_horizontal_error:.4f} m")
        print(f"Vertical RMS:                 {vertical_rms:.4f} m")
        print(f"Lateness Mean:                {np.mean(lateness) * 1000:.2f} ms")
        print(f"Lateness Max:                 {np.max(lateness) * 1000:.2f} ms")
        print(f"Number of NaN rows in pos_act: {nan_rows} (Expected: 0)")

    plt.figure(figsize=(8, 6))

    plt.plot(pos_des[:, 1], pos_des[:, 0], 'r--', label="Desired Path")
    plt.plot(pos_act[:, 1], pos_act[:, 0], 'b-', label="Actual Path")

    plt.xlabel("East / m")
    plt.ylabel("North / m")

    plt.title(
        f"Top-Down Path Profile (Seed 4)\nWind Speed: {wind_speed:.1f} m s$^{{-1}}$ | Mass Factor: {mass_factor:.2f}\nHorizontal RMS: {horizontal_rms:.2f} m"
    )
    plt.gca().set_aspect('equal')
    plt.grid(True, linestyle=":")
    
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    plt.tight_layout()

    os.makedirs(FIG_DIR, exist_ok=True)

    png_output_path = Path(FIG_DIR) / "fig1_ex_run_path.png"
    pdf_output_path = Path(FIG_DIR) / "fig1_ex_run_path.pdf"

    if not report:
        plt.savefig(png_output_path, dpi=200, bbox_inches="tight")

    plt.savefig(pdf_output_path, bbox_inches="tight")
    plt.close()

    if not report:
        print(f"[V] Plot(s) successfully saved to:")
        print(f"  - {png_output_path}")
        print(f"  - {pdf_output_path}")

    return pdf_output_path

if __name__ == "__main__":
    plot_fig1()