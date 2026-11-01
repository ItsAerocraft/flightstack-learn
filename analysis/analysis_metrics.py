import os
import numpy as np


def compute_metrics(npz_path):
    if not os.path.exists(npz_path):
        raise FileNotFoundError(f"Could not find {npz_path}. Ensure your flight controller loop ran successfully.")

    data = np.load(npz_path)

    t = data["t"]
    pos_des = data["pos_des"]  # [North, East, Down]
    pos_act = data["pos_act"]  # [North, East, Down]
    lateness = data["lateness"]
    ramp_duration = float(data["ramp_duration"])

    # e is shape (N, 3) representing [e_north, e_east, e_down]
    e = pos_des - pos_act

    # Horizontal error vector norm per tick: sqrt(e_north^2 + e_east^2)
    e_h = np.linalg.norm(e[:, :2], axis=1)

    # Vertical error vector: e_down
    e_v = e[:, 2]

    # boolean array filter mask, filter out those before ramp ends
    mask = t > ramp_duration

    e_h_masked = e_h[mask]
    e_v_masked = e_v[mask]

    horizontal_rms = np.sqrt(np.mean(e_h_masked ** 2))
    max_horizontal_error = np.max(e_h_masked)
    vertical_rms = np.sqrt(np.mean(e_v_masked ** 2))

    # Find any row where any position actual is NaN
    nan_rows = np.isnan(pos_act).any(axis=1).sum()

    output_dict = {}
    output_dict.update({
        'horizontal_rms': horizontal_rms,
        'max_horizontal_error': max_horizontal_error,
        'vertical_rms': vertical_rms,
        'nan_rows': nan_rows,
        'lateness': lateness,
        'pos_des': pos_des,
        'pos_act': pos_act

    })

    return output_dict
