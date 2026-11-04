import os
import numpy as np
import pandas as pd

from configs.config_paths import SUMMARY_CSV, BOOTSTRAP_CSV


OUTPUT_CSV = BOOTSTRAP_CSV

def run_bootstrapping(n_iterations=10000, seed=62):
    '''
    Bootstraps confidence intervals for the wind/mass/swing-period effects on
    horizontal RMS error and for mean RMS within each wind-speed bin, from the
    successful trials in summary.csv.

    Args:
        [n_iterations]: number of bootstrap resamples to draw (~).
        [seed]: seed for the random number generator, for reproducible resampling.

    Writes a summary table (point estimate plus 95% CI per statistic) to
    BOOTSTRAP_CSV and prints it.

    Each resample refits RMS vs. wind speed by linear regression, removes
    that wind trend from the residuals, then fits mass factor and
    direction-swing period against the residuals, so each reported effect is
    estimated after controlling for wind speed.
    '''
    if not os.path.exists(SUMMARY_CSV):
        raise FileNotFoundError(
            f"Could not find {SUMMARY_CSV}. Run the batch script first."
        )

    # filter out failed trials
    df = pd.read_csv(SUMMARY_CSV)
    df_ok = df[df["status"] == "ok"].reset_index(drop=True)
    n_rows = len(df_ok)

    if n_rows == 0:
        raise ValueError("No successful trials ('ok') found to resample.")

    # initialize a fixed random number generator for reproducibility
    rng = np.random.default_rng(seed)

    # extract numpy arrays
    wind_speed = df_ok["wind_speed"].to_numpy()
    mass_factor = df_ok["mass_factor"].to_numpy()
    dir_period = df_ok["direction_swing_period"].to_numpy()
    rms_m = df_ok["rms_m"].to_numpy()

    orig_slope_w, orig_intercept_w = np.polyfit(wind_speed, rms_m, 1)
    orig_residuals = rms_m - (orig_slope_w * wind_speed + orig_intercept_w)
    orig_slope_m, _ = np.polyfit(mass_factor, orig_residuals, 1)
    orig_slope_s, _ = np.polyfit(dir_period, orig_residuals, 1)

    # use dictionary arrays to store true point estimates
    true_estimates = {
        "wind_slope": orig_slope_w * 100.0,
        "mass_effect": orig_slope_m * 10.0,
        "swing_effect": orig_slope_s * 100.0,
        "bin_0_1": np.nanmean(rms_m[(wind_speed >= 0) & (wind_speed < 1)]) * 100.0,
        "bin_1_2": np.nanmean(rms_m[(wind_speed >= 1) & (wind_speed < 2)]) * 100.0,
        "bin_2_3": np.nanmean(rms_m[(wind_speed >= 2) & (wind_speed < 3)]) * 100.0,
        "bin_3_4": np.nanmean(rms_m[(wind_speed >= 3) & (wind_speed < 4)]) * 100.0,
        "bin_4_5": np.nanmean(rms_m[(wind_speed >= 4) & (wind_speed < 5)]) * 100.0,
        "bin_5_6": np.nanmean(rms_m[(wind_speed >= 5) & (wind_speed <= 6)]) * 100.0,
    }

    # use dictionary arrays to store computed metrics for each iteration
    boot_results = {
        "wind_slope": np.zeros(n_iterations),
        "mass_effect": np.zeros(n_iterations),
        "swing_effect": np.zeros(n_iterations),
        "bin_0_1": np.zeros(n_iterations),
        "bin_1_2": np.zeros(n_iterations),
        "bin_2_3": np.zeros(n_iterations),
        "bin_3_4": np.zeros(n_iterations),
        "bin_4_5": np.zeros(n_iterations),
        "bin_5_6": np.zeros(n_iterations)
    }

    print(f"Running {n_iterations:,} bootstrap resamples...")

    for i in range(n_iterations):
        indices = rng.integers(0, n_rows, size=n_rows)

        w_res = wind_speed[indices]
        m_res = mass_factor[indices]
        p_res = dir_period[indices]
        rms_res = rms_m[indices]

        # RMS vs wind slope
        # np.polyfit(x, y, 1)[0] returns the slope
        slope_w, intercept_w = np.polyfit(w_res, rms_res, 1)
        # Unit conversion rule: Convert meters to cm per m/s
        boot_results["wind_slope"][i] = slope_w * 100.0

        # Remove the dominant wind profile first inside the loop
        residuals = rms_res - (slope_w * w_res + intercept_w)

        # mass effect
        slope_m, _ = np.polyfit(m_res, residuals, 1)
        # convert to cm
        boot_results["mass_effect"][i] = slope_m * 10.0

        # swing period effect
        slope_s, _ = np.polyfit(p_res, residuals, 1)
        # convert to cm as well
        boot_results["swing_effect"][i] = slope_s * 100.0

        # -mean RMS per wind speed bin in cm
        boot_results["bin_0_1"][i] = (
            np.mean(rms_res[(w_res >= 0) & (w_res < 1)]) * 100.0
        )
        boot_results["bin_1_2"][i] = (
            np.mean(rms_res[(w_res >= 1) & (w_res < 2)]) * 100.0
        )
        boot_results["bin_2_3"][i] = (
            np.mean(rms_res[(w_res >= 2) & (w_res < 3)]) * 100.0
        )
        boot_results["bin_3_4"][i] = (
            np.mean(rms_res[(w_res >= 3) & (w_res < 4)]) * 100.0
        )
        boot_results["bin_4_5"][i] = (
            np.mean(rms_res[(w_res >= 4) & (w_res < 5)]) * 100.0
        )
        boot_results["bin_5_6"][i] = (
            np.mean(rms_res[(w_res >= 5) & (w_res <= 6)]) * 100.0
        )
    # use 2.5% and 97.5% quantiles for 95% CI
    metrics_summary = []
    labels = {
        "wind_slope": "RMS vs Wind Slope / cm s m^-1",
        "bin_0_1":      "Mean RMS [0-1 m s^-1] / cm",
        "bin_1_2":      "Mean RMS [1-2 m s^-1] / cm",
        "bin_2_3":      "Mean RMS [2-3 m s^-1] / cm",
        "bin_3_4":      "Mean RMS [3-4 m s^-1] / cm",
        "bin_4_5":      "Mean RMS [4-5 m s^-1] / cm",
        "bin_5_6":      "Mean RMS [5-6 m s^-1] / cm",
        "mass_effect":  "Mass Effect / (cm per +10% mass)",
        "swing_effect": "Swing-Period Effect / cm s^-1"
    }

    for key, label in labels.items():
        arr = boot_results[key]
        # drop any empty slices from narrow wind bins
        arr = arr[~np.isnan(arr)]

        point_estimate = true_estimates[key]
        ci_lower = np.percentile(arr, 2.5)
        ci_upper = np.percentile(arr, 97.5)

        metrics_summary.append(
            {
                "Statistic": label,
                "Estimate": round(point_estimate, 1),
                "95% CI Lower": round(ci_lower, 1),
                "95% CI Upper": round(ci_upper, 1),
            }
        )

    summary_df = pd.DataFrame(metrics_summary)

    print("\n" + "=" * 32 + " BOOTSTRAP RESULTS " + "=" * 32)
    print(summary_df.to_string(index=False))
    print("=" * 83 + "\n")

    summary_df.to_csv(OUTPUT_CSV, index=False)
    print(f"[V] Table successfully written directly to: {OUTPUT_CSV}")


if __name__ == "__main__":
    run_bootstrapping()
