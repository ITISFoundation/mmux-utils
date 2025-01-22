import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib import gridspec
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.patches as patches
import numpy as np
import pandas as pd
from typing import Union, Optional, Tuple, Callable
from pathlib import Path


def is_dominated(point: np.ndarray, other_points: np.ndarray):
    return any(all(point >= other) for other in other_points)


def get_non_dominated_indices(data, sort_by_column="Objective1"):
    data = data.copy()
    non_dominated_indices = []
    for i, point in data.iterrows():
        if not is_dominated(point.values, data.drop(i).values):  # type: ignore
            non_dominated_indices.append(i)

    sorted_indices = (
        data.loc[non_dominated_indices].sort_values(by=sort_by_column).index.values
    )

    return sorted_indices


def load_data_dakota_free_pulse_optimization(
    filename="dakota_tabular.dat", n_parameters=10
):
    data = pd.read_csv(filename, delim_whitespace=True)

    ## Add objective functions with proper names; leave the old ones as columns as well
    data["Activation (%)"] = 100 * (1.0 - data["1-activation"])
    data["Energy"] = data["energy"]
    data["Maximum Amplitude"] = data["maxampout"]
    return data


def plot_objective_space(
    F: Union[pd.DataFrame, np.ndarray],
    ax: Optional[plt.Axes] = None,
    xlim: Tuple[float, float] = (0, 20),
    ylim: Tuple[float, float] = (0, 1e2),
    color: str = "blue",
    xlabel: str = "Relative Energy (au)",
    ylabel: str = "Activation (%)",
    title: str = "Objective Space",
    facecolors: str = "none",
):
    """Plot the objective space of a set of points F."""
    if isinstance(F, pd.DataFrame):
        F = F.values

    if ax is None:
        ax = plt.subplots(figsize=(10, 10))[1]

    plt.scatter(F[:, 1], F[:, 0], s=30, facecolors=facecolors, edgecolors=color)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.xlim(xlim)
    plt.ylim(ylim)

    plt.hlines(0, xmin=0, xmax=2000, color="gray", linestyle="--", alpha=0.5)

    plt.title(title)


def add_inset_pulses(
    pulses_args: tuple,
    errors: tuple,
    pareto_point: Tuple[float, float],
    ax: plt.Axes,
    create_pulses_fun: Callable,
    flip_x_y: bool = True,
    total_size: Tuple[float, float] = (0.5, 0.3),
    partial_size: float = 0.4 * 100,
    ylim: Tuple[float, float] = (-1e3, 1e3),
    x_offset: float = 0.0,
    y_offset: float = 0.0,
):
    """Generate an inset plot with the pulses used to generate the pareto point, within the pareto front plot itself.
    NB: a box is generated around the pareto point (using total_size), and then only the lower right corner of it is used (using partial_size).

    Args:
        pulses_args (tuple): Input used to generate the pulses (ie X[i])
        pareto_point (Tuple[float, float]): Ouput of the evaluation (ie F[i])
        ax (plt.Axes): Main axes in which to create the inset.
        pkg: Package used to generate the pulses (ie where pulse_generation.py is).
        flip_x_y (bool, optional): Whether x and y axis are flipped in the pareto front plot.
            Defaults to True, as normally the activation is the first objective, but we want it in the y axis.
        total_size (Tuple[float, float], optional): This parameter, when multiplied by partial size,
            gives the size of the inset plot (relative to 1). Defaults to (0.5, 0.3).
        partial_size (float, optional): Relative size (within the total size) that the actual inset occupies.
            Any size bigger than 50(%) will result in the pareto point being hidden. Defaults to 40 (%).
        ylim (Tuple[float, float], optional): Limits of the y axis (amplitude) of the inset plot. Defaults to (0, 100).
        x_offset (float, optional): Offset (in the x-axis) for the inset. Between 0 and 1, defaults to 0.
        y_offset (float, optional): Offset (in the x-axis) for the inset. Between 0 and 1, defaults to 0.
    """
    # Create mini-plots for non-dominated solutions
    if flip_x_y:
        ## NOTE: F[0] = activation (in y axis), F[1] = energy (in x axis)
        y, x = pareto_point
    else:
        x, y = pareto_point

    width = ax.get_xlim()[1] - ax.get_xlim()[0]
    height = ax.get_ylim()[1] - ax.get_ylim()[0]
    inset_width = width * total_size[0]
    inset_height = height * total_size[1]
    ## set the inset centered on the point
    x_position = (x - inset_width / 2) / width
    y_position = (y - inset_height / 2) / height
    ## be able to customly move insets around
    x_position += x_offset
    y_position += y_offset
    bbox_to_anchor = [x_position, y_position, total_size[0], total_size[1]]
    # axins = inset_axes(ax, width="40%", height="40%", bbox_to_anchor=bbox_to_anchor, bbox_transform=ax.transAxes)
    axins: plt.Axes = inset_axes(
        ax,
        width=str(partial_size) + "%",
        height=str(partial_size) + "%",
        loc="lower right",  ## must be kept, everything (+- y/x) is relative to this position
        bbox_to_anchor=bbox_to_anchor,
        bbox_transform=ax.transAxes,
    )

    # Plot additional details inside the mini-plot if necessary
    # pulse: nf.neuron.StimulationPulse
    pulse = create_pulses_fun(*pulses_args, stds=errors)
    pulse.plot_pulse(axins)
    axins.set_xlim(pulse.time_list[0], pulse.time_list[-1])
    axins.set_title("")
    # axins.set_xlabel("ms")
    # axins.set_label_position("right")
    ## eliminate axis ticks
    # axins.set_xticks([])
    axins.yaxis.tick_right()
    axins.yaxis.set_label_position("right")
    axins.set_ylabel("Ampl (mA)")

    # axins.set_yticks([])
    axins.legend([], [], frameon=False)
    axins.hlines(
        0,
        pulse.time_list[0],
        pulse.time_list[-1],
        color="gray",
        linestyle="--",
        alpha=0.5,
    )

    ## get the position of the upper right corner of the inset plot
    ## taking into account that it is in the LOC=lower right of the bigger plot centered at (x,y)
    x0 = (((50.0 - partial_size) / 100.0) * total_size[0] + x_offset - 0.01) * width
    y0 = ((50.0 - partial_size) / 100.0 * total_size[1] - y_offset - 0.08) * height

    # Create an arrow from the non-dominated point to the inset plot
    arrow = patches.FancyArrowPatch(
        (x, y),
        (
            (x + x0),
            (y - y0)
            - 0.12 * height,  # for some reason the arrow is always a bit too low
        ),
        color="black",
        mutation_scale=15,
        arrowstyle="->",
        linestyle="--",
        alpha=0.75,
    )
    ax.add_patch(arrow)
