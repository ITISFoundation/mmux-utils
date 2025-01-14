import pandas
import matplotlib.pyplot as plt
import pathlib
import copy


opt_dir_name = (
    pathlib.Path(r"e:\S4L_Projects\OptiStim\pulse-optimization\runs")
    / "dakota_20241106.16052306_opt_GP"
)

opt_dir = pathlib.Path(opt_dir_name)

## check for descriptors in dakota file
dakota_file = opt_dir / "dakota_sumo_opt.in"
# parse text in dakota
with open(dakota_file, "r") as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if "descriptors" in l and "variables" in lines[i - 1]:
        variables = l.split()[1:]
        variables = [v[1:-1] for v in variables]  # remove quotes
        # append all elements (space-separated) after "descriptors"
    if "descriptors" in l and "responses" in lines[i - 1]:
        responses = l.split()[1:]
        responses = [r[1:-1] for r in responses]  # remove quotes

fig1, axes = plt.subplots(len(responses), 1)
fig2, axes_rms = plt.subplots(len(responses), 1)
mae = {r: [] for r in responses}
rms = {r: [] for r in responses}
std = {r: [] for r in responses}

for iteration in range(1, 1000000):
    finaldata_path = opt_dir / f"finaldata{iteration}.dat"
    finaltruthdata_path = opt_dir / f"finaldatatruth{iteration}.dat"

    if not finaltruthdata_path.exists():
        break

    data = pandas.read_csv(
        finaldata_path,
        delim_whitespace=True,
        header=None,
        names=variables + responses,
    )
    data_truth = pandas.read_csv(
        finaltruthdata_path,
        delim_whitespace=True,
        header=None,
        names=variables + [r + "_truth" for r in responses],
    )
    merged = pandas.merge(data, data_truth, how="left", on=variables)

    for ax, r in zip(axes, responses):
        mae[r].append((merged[r] - merged[r + "_truth"]).abs().mean())
        rms[r].append(((merged[r] - merged[r + "_truth"]) ** 2).mean() ** 0.5)
        std[r].append(((merged[r] - merged[r + "_truth"]) ** 2).std() ** 0.5)
import numpy as np

fig2, axes_rms = plt.subplots(len(responses), 1, sharex=True)
for ax, r in zip(axes_rms, responses):
    ax.plot(
        range(len(rms[r])),
        np.array(rms[r]),
        ".-",
        label="RMSE",
    )
    ax.plot(
        range(len(rms[r])),
        np.array(std[r]),
        ".-",
        label="STD",
    )
    ax.legend()
    ax.set_title(f"RMS vs STD - Error & Variance Comparison - {r}")
    ax.set_ylabel(f"Absolute Error")
    ax.set_yscale("log")
ax.set_xlabel("iteration")
plt.tight_layout()
plt.savefig(opt_dir / "avg_rms_std.png")


fig3, axes_mae = plt.subplots(len(responses), 1, sharex=True)
for ax, r in zip(axes_mae, responses):
    ax.plot(
        range(len(mae[r])),
        np.array(mae[r]),
        ".-",
        label="MAE",
    )
    ax.plot(
        range(len(std[r])),
        np.array(std[r]),
        ".-",
        label="STD",
    )
    ax.legend()
    ax.set_title(f"MAE vs STD - Error & Variance Comparison - {r}")
    ax.set_ylabel(f"Absolute Error & Variance")
    ax.set_yscale("log")
ax.set_xlabel("iteration")
plt.tight_layout()
plt.savefig(opt_dir / "avg_mae_std.png")
