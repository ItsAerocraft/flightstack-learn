import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from configs.config_paths import FIG_DIR, SUMMARY_CSV


def plot_fig2(report=False):
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

    if not report:
        print(f"=== Filtering Simulation Results ===")
        print(f"Total trials found:         {total_trials}")
        print(f"Successful trials retained: {successful_trials}")
        print(f"Dropped trials:             {dropped_trials}\n")

    plt.figure(figsize=(7, 5))

    x = df_ok["wind_speed"]
    y = df_ok["rms_m"]

    sc = plt.scatter(x, y, c=df_ok["direction_swing_period"], cmap="viridis", s=15, alpha=0.8, edgecolors="none")

    cbar = plt.colorbar(sc)
    cbar.set_label("Direction Swing Period / s")

    plt.xlabel("Wind speed / m s$^{-1}$")
    plt.ylabel("Horizontal RMS error / m")

    plt.ylim(0, 1.1 * y.max())

    plt.title(
        f"Horizontal RMS Error vs. Wind Speed\n(n = {successful_trials} successful trials)"
    )
    plt.grid(True, linestyle=":", alpha=0.6)

    os.makedirs(FIG_DIR, exist_ok=True)

    png_output_path = Path(FIG_DIR) / "fig2_rms_vs_wind.png"
    pdf_output_path = Path(FIG_DIR) / "fig2_rms_vs_wind.pdf"

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
    plot_fig2()
