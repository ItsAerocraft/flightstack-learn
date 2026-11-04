import os
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

from configs.config_paths import FIG_DIR, SUMMARY_CSV


def plot_fig3(report=False):
    '''
    Plots horizontal RMS error against mass factor for every successful
    trial in summary.csv, colored by wind speed.

    Args:
        [report]: if True, suppresses console printing and skips the PNG
            copy, producing only the PDF (for batch figure generation).

    Returns:
        Path to the saved PDF figure, or None if no successful trials are
        available to plot.

    Trials whose status is not "ok" are dropped before plotting; the dropped
    count is reported when report is False.
    '''
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

    if successful_trials == 0:
        print("Warning: No successful trials found to plot.")
        return

    plt.figure(figsize=(7, 5))

    x = df_ok["mass_factor"]
    y = df_ok["rms_m"]

    sc = plt.scatter(x, y, c=df_ok["wind_speed"], cmap="viridis", s=15, alpha=0.8, edgecolors="none")

    cbar = plt.colorbar(sc)
    cbar.set_label("Wind Speed / m s$^{-1}$")

    plt.xlabel("Mass factor ($m_{act} / m_{nom}$)")
    plt.ylabel("Horizontal RMS error / m")

    y_max = y.max()
    if pd.notna(y_max) and y_max > 0:
        plt.ylim(0, 1.1 * y_max)

    plt.title(
        f"Horizontal RMS Error vs. Mass Factor\n(n = {successful_trials} successful trials)"
    )
    plt.grid(True, linestyle=":", alpha=0.6)

    os.makedirs(FIG_DIR, exist_ok=True)

    png_output_path = Path(FIG_DIR) / "fig3_rms_vs_mass.png"
    pdf_output_path = Path(FIG_DIR) / "fig3_rms_vs_mass.pdf"

    if not report:
        plt.savefig(png_output_path, dpi=200, bbox_inches="tight")

    plt.savefig(pdf_output_path, bbox_inches="tight")
    plt.close()

    if not report:
        print(f"[V] Plot successfully saved to:")
        print(f"  - {png_output_path}")
        print(f"  - {pdf_output_path}")

    return pdf_output_path

if __name__ == "__main__":
    plot_fig3()
