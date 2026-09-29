#!/usr/bin/env python3
"""
Plots CSV data.

Assumes the first column of your CSV data is always the x-axis data.

@author: Austin Owens
@date: 7/30/2023
"""

import argparse
import csv
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import yaml


class Plotter:
    """Creates one or more plots/subplots from CSV data as defined in a yaml."""

    def __init__(self, csv_file: str):
        """Initilize Plotter class."""
        self.csv_file = csv_file
        self.data = self._read_csv_data(self.csv_file)

    def _read_csv_data(self, csv_file: str) -> Tuple[list[str], Any]:
        with open(csv_file, newline="") as f:
            reader = csv.reader(f)
            headers = next(reader)  # Get headers (column names)
            data = defaultdict(list)
            for row in reader:  # Assign data to their column names
                for header, value in zip(headers, row):
                    data[header].append(float(value))
        return headers, data

    def plot_data(
        self,
        plot_config: Dict[str, List[Tuple[str, str, List[str]]]],
        marker: Optional[str] = None,
    ) -> None:
        """Plot the data from the CSV file as defined in the yaml file."""
        headers, data = self.data
        for figure_title, subplot_configs in plot_config.items():
            fig, axs = plt.subplots(len(subplot_configs), 1, sharex=True)
            fig.suptitle(figure_title + " ({})".format(self.csv_file))
            if len(subplot_configs) == 1:
                axs = [axs]
            for i, (subplot_title, ylabel, column_names) in enumerate(subplot_configs):
                ax = axs[i]
                ax.set_title(subplot_title)
                ax.set_ylabel(ylabel)
                for column_name in column_names:
                    ax.plot(
                        data[headers[0]],
                        data[column_name],
                        linestyle="solid",
                        marker=marker,
                        label=column_name,
                    )
                ax.legend()
                ax.grid(True)
            axs[-1].set_xlabel(headers[0])  # Only the last subplot gets an x label
        plt.tight_layout()  # Adjust the layout to prevent overlap
        plt.show()


def load_yaml(filename: str) -> Any:
    """Load the yaml file."""
    with open(filename, "r") as file:
        return yaml.safe_load(file)


def main() -> None:
    """Parse yaml file to generate plots from csv.

    This script reads a YAML file containing plot configurations and a CSV file
    and outputs the parsed configuration. The user can define their own plot
    configurations in the following format:

    PLOT_NAME:
      - ["SUBPLOT NAME 1", "Y-AXIS LABEL 1", ["col1_name", "col2_name", ...]]
      - ["SUBPLOT NAME 2", "Y-AXIS LABEL 2", ["col3_name", "col4_name", ...]]
      - [...]

    ANOTHER_PLOT_NAME:
      - ["SUBPLOT NAME 3", "Y-AXIS LABEL 3", ["col5_name", "col6_name", ...]]
      - ["SUBPLOT NAME 4", "Y-AXIS LABEL 4", ["col7_name", "col8_name", ...]]
      - [...]

    Example YAML File:
    ------------------

    Position:
      - ["", "Pos (Pulses)", ["pos_cpr_counts", "pos_estimate_counts", "count_in_cpr"]]
      - ["", "Pos (Revolutions)", ["pos_circular", "pos_estimate"]]

    Velocity:
      - ["", "Vel (Pulses/Sec)", ["vel_estimate_counts"]]
      - ["", "Vel (Revolutions/Sec)", ["vel_estimate"]]

    Note: The "" for the SUBPLOT NAME means there will be no title used

    The script takes two arguments:
    - `config_file`: The path to the YAML configuration file.
    - `csv_file`: The path to the CSV file containing the data.
    """
    parser = argparse.ArgumentParser(description="Plot configuration script")
    parser.add_argument("config_file", type=str, help="YAML configuration file")
    parser.add_argument("csv_file", type=str, help="CSV File")
    args = parser.parse_args()

    plot_config = load_yaml(args.config_file)

    plotter = Plotter(args.csv_file)
    plotter.plot_data(plot_config, marker="*")


if __name__ == "__main__":
    main()
