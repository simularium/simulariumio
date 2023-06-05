#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from typing import List, Dict, Callable
import copy
import time
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
    DisplayData,
)
from .filters import Filter
from .exceptions import UnsupportedPlotTypeError
from .writers import JsonWriter, BinaryWriter
from .constants import DISPLAY_TYPE, VIEWER_DIMENSION_RANGE

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

    def __init__(
        self,
        input_data: TrajectoryData,
        progress_callback: Callable[[float], None] = None,
        callback_interval: float = 10,
    ):
        """
        This object reads simulation trajectory outputs
        and plot data and writes them in the JSON format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : TrajectoryData
            An object containing simulation trajectory outputs
            and plot data
        progress_callback : Callable[[float], None] (optional)
            Callback function that accepts 1 float argument and returns None
            which will be called at a given progress interval, determined by
            callback_interval requested, providing the current percent progress
            Default: None
        callback_interval : float (optional)
            If a progress_callback was provided, the period between updates
            to be sent to the callback, in seconds
            Default: 10
        """
        self._data = input_data
        self.progress_callback = progress_callback
        self.callback_interval = callback_interval
        self.last_report_time = time.time()

    def check_report_progress(self, percent_complete: float) -> None:
        current_time = time.time()
        if (
            self.progress_callback
            and current_time > self.last_report_time + self.callback_interval
        ):
            self.progress_callback(percent_complete)
            self.last_report_time = current_time

    @staticmethod
    def check_max_min_coordinates(
        max_dimensions: np.array,
        min_dimensions: np.array,
        current_position: np.array,
        radius: float = 0.0,
    ):
        for i in range(len(current_position)):
            curr_val = float(current_position[i])
            if curr_val - radius < min_dimensions[i]:
                min_dimensions[i] = curr_val - radius
            if curr_val + radius > max_dimensions[i]:
                max_dimensions[i] = curr_val + radius

    @staticmethod
    def calculate_scale_factor(
        max_dimensions: np.array,
        min_dimensions: np.array,
    ) -> float:
        """
        Return a scale factor, using the given min and max
        dimensions, so that the final range of agent locations
        is within the dimensions defined by VIEWER_DIMENSION_RANGE
        """
        range = max(max_dimensions - min_dimensions)
        scale_factor = 1
        if range == 0:
            return scale_factor
        if range > VIEWER_DIMENSION_RANGE.MAX:
            scale_factor = VIEWER_DIMENSION_RANGE.MAX / range
        elif range < VIEWER_DIMENSION_RANGE.MIN:
            scale_factor = VIEWER_DIMENSION_RANGE.MIN / range
        return scale_factor

    @staticmethod
    def _get_display_type_name_from_raw(
        raw_type_name: str, display_data: Dict[str, DisplayData]
    ) -> str:
        """
        Get the display type_name from the display data
        given the raw type name from the engine.
        If there is no DisplayData for this type, add it
        using the raw type_name and SPHERE display_type
        """
        agent_display_data = TrajectoryConverter._get_display_data_for_agent(
            raw_type_name, display_data
        )
        if agent_display_data:
            return agent_display_data.name

        display_type_name = raw_type_name
        display_data[display_type_name] = DisplayData(
            name=display_type_name,
            display_type=DISPLAY_TYPE.SPHERE,
        )
        return display_type_name

    @staticmethod
    def _get_display_data_for_agent(
        raw_type_name: str, display_data: Dict[str, DisplayData]
    ) -> DisplayData:
        """
        If the provided raw_type_name matches a key in the display data dict,
        ignoring case, return the corresponding DisplayData for that key.
        Otherwise, return None
        """
        for input_name in display_data:
            if input_name.lower() == raw_type_name.lower():
                return display_data[input_name]
        return None

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

    def save(self, output_path: str, binary: bool = True, validate_ids: bool = True):
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
        validate_ids: bool
            additional validation to check agent ID size?
            Default = True
        """
        if binary:
            BinaryWriter.save(self._data, output_path, validate_ids)
        else:
            JsonWriter.save(self._data, output_path, validate_ids)
