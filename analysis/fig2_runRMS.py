import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from configs.config_paths import FIG_DIR, SUMMARY_CSV


def main():
    if not os.path.exists(SUMMARY_CSV):
        raise FileNotFoundError(
            f"Could not find {SUMMARY_CSV}. Make sure to run your batch simulation script first."
        )

    df = pd.read_csv(SUMMARY_CSV)
    total_trials = len(df)

    # filter out failed trials and report dropped rows
    df_ok = df[df["status"] == "ok"]
    successful_trials = len(df_ok)
    dropped_trials = total_trials - successful_trials

    print(f"=== Filtering Simulation Results ===")
    print(f"Total trials found:         {total_trials}")
    print(f"Successful trials retained: {successful_trials}")
    print(f"Dropped trials:             {dropped_trials}\n")

    plt.figure(figsize=(7, 5))

    x = df_ok["wind_speed"]
    y = df_ok["rms_m"]

    plt.scatter(x, y, color="blue", alpha=0.7, edgecolors="none", label="Trials")

    plt.xlabel("Wind speed / m s^-1")
    plt.ylabel("Horizontal RMS error / m")

    plt.ylim(bottom=0)

    plt.title(
        f"Horizontal RMS Error vs. Wind Speed\n(n = {successful_trials} successful trials)"
    )
    plt.grid(True, linestyle=":", alpha=0.6)

    os.makedirs(FIG_DIR, exist_ok=True)

    png_output_path = Path(FIG_DIR) / "fig2_rms_vs_wind.png"
    pdf_output_path = Path(FIG_DIR) / "fig2_rms_vs_wind.pdf"

    plt.savefig(png_output_path, dpi=200, bbox_inches="tight")
    plt.savefig(pdf_output_path, bbox_inches="tight")
    plt.close()

    print(f"[V] Plot successfully saved to:")
    print(f"  - {png_output_path}")
    print(f"  - {pdf_output_path}")


if __name__ == "__main__":
    main()
