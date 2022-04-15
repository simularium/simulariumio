#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from typing import List
import copy

import numpy as np

from .plot_readers import (
    HistogramPlotReader,
    ScatterPlotReader,
    PlotReader,
)
from .data_objects import (
    HistogramPlotData,
    ScatterPlotData,
    TrajectoryData,
)
from .filters import Filter
from .exceptions import UnsupportedPlotTypeError
from .writers import JsonWriter, BinaryWriter

###############################################################################

log = logging.getLogger(__name__)

###############################################################################

SUPPORTED_PLOT_READERS = {
    "scatter": ScatterPlotReader,
    "histogram": HistogramPlotReader,
}

###############################################################################


class TrajectoryConverter:
    _data: TrajectoryData

    def __init__(self, input_data: TrajectoryData):
        """
        This object reads simulation trajectory outputs
        and plot data and writes them in the JSON format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : TrajectoryData
            An object containing simulation trajectory outputs
            and plot data
        """
        self._data = input_data

    @staticmethod
    def _determine_plot_reader(plot_type: str = "scatter") -> [PlotReader]:
        """
        Return the plot reader to match the requested plot type
        """
        if plot_type in SUPPORTED_PLOT_READERS:
            return SUPPORTED_PLOT_READERS[plot_type]

        raise UnsupportedPlotTypeError(plot_type)

    def add_plot(
        self,
        data: [ScatterPlotData or HistogramPlotData],
        plot_type: str = "scatter",
    ):
        """
        Add data to be rendered in a plot

        Parameters
        ----------
        data: ScatterPlotData or HistogramPlotData
            Loaded data for a plot.
        plot_type: str
            A string specifying which type of plot to render.
            Current options:
                'scatter' : a scatterplot with y-trace(s) dependent
                    on an x-trace
                'histogram' : a histogram with bars drawn at intervals
                    over the range(s) of the data, with their height
                    corresponding to the number of values in each interval
            Default: 'scatter'
        """
        plot_reader_class = self._determine_plot_reader(plot_type)
        self._data.plots.append(plot_reader_class().read(data))

    def add_number_of_agents_plot(
        self,
        plot_title: str = "Number of agents over time",
        yaxis_title: str = "Number of agents",
    ):
        """
        Add a scatterplot of the number of each type of agent over time

        Parameters
        ----------
        plot_title: str
            The title for the plot
            Default: "Number of agents over time"
        yaxis_title: str
            The title for the y-axis of the plot
            Default: "Number of agents"
        """
        n_agents = {}
        for time_index in range(self._data.agent_data.times.size):
            for agent_index in range(int(self._data.agent_data.n_agents[time_index])):
                type_name = self._data.agent_data.types[time_index][agent_index]
                if "#" in type_name:
                    type_name = type_name.split("#")[0]
                if type_name not in n_agents:
                    n_agents[type_name] = np.zeros_like(self._data.agent_data.times)
                n_agents[type_name][time_index] += 1
        self.add_plot(
            ScatterPlotData(
                title=plot_title,
                xaxis_title=f"Time ({self._data.time_units})",
                yaxis_title=yaxis_title,
                xtrace=self._data.agent_data.times,
                ytraces=n_agents,
                render_mode="lines",
            )
        )

    def filter_data(self, filters: List[Filter]) -> TrajectoryData:
        """
        Return the simularium data with the given filter applied
        """
        filtered_data = copy.deepcopy(self._data)
        for f in filters:
            filtered_data = f.apply(filtered_data)
        return filtered_data

    def to_JSON(self):
        """
        Return the current simularium data in JSON format

        """
        buffer_data = JsonWriter.format_trajectory_data(self._data)
        return json.dumps(buffer_data)

    def save_plot_data(self, output_path: str):
        """
        Save the current plot data in JSON format
        at the output path

        Parameters
        ----------
        output_path: str
            where to save the file
        """
        JsonWriter.save_plot_data(self._data.plots, output_path)

    def save(self, output_path: str, binary: bool = True):
        """
        Save the current simularium data in .simularium JSON format
        at the output path

        Parameters
        ----------
        output_path: str
            where to save the file
        binary: bool (optional)
            save in binary format? otherwise use JSON
            Default: True
        """
        if binary:
            BinaryWriter.save(self._data, output_path)
        else:
            JsonWriter.save(self._data, output_path)
