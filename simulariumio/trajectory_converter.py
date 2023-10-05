#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from typing import List, Dict, Callable, Tuple
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
    AgentData,
)
from .filters import Filter
from .exceptions import UnsupportedPlotTypeError
from .writers import JsonWriter, BinaryWriter
from .constants import DISPLAY_TYPE, VIEWER_DIMENSION_RANGE, VALUES_PER_3D_POINT

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

    def _get_valid_agents(data: np.array, n_agents: np.array) -> np.array:
        """
        Given position data (shape = [timesteps, agents, 3]), and
        corresponding n_agents data, indicating agents per timestamp,
        return arrays of X, Y, and Z values from data, skipping values
        that do not correspond with agents, as specified by n_agents.
        """
        x_data = np.array([])
        y_data = np.array([])
        z_data = np.array([])
        x = data[:, :, 0]
        y = data[:, :, 1]
        z = data[:, :, 2]
        for i in range(len(n_agents)):
            x_data = np.append(x_data, x[i][0 : int(n_agents[i])])
            y_data = np.append(y_data, y[i][0 : int(n_agents[i])])
            z_data = np.append(z_data, z[i][0 : int(n_agents[i])])
        return np.array([x_data, y_data, z_data])

    @staticmethod
    def get_xyz_max(data: np.array, n_agents: np.array = None) -> np.array:
        """
        Given AgentData position data (shape = [timesteps, agents, 3]), and
        corresponding n_agents data, indicating agents per timestamp, extract
        all position data, skipping the zeros that represent no data. Provide
        maximum X, Y, and Z values from remaining data
        """
        if n_agents is not None:
            [x_data, y_data, z_data] = TrajectoryConverter._get_valid_agents(
                data, n_agents
            )
        else:
            x_data = data[:, :, 0].flatten()
            y_data = data[:, :, 1].flatten()
            z_data = data[:, :, 2].flatten()
        return np.array([max(x_data), max(y_data), max(z_data)])

    @staticmethod
    def get_xyz_min(data: np.array, n_agents: np.array = None) -> np.array:
        """
        Given AgentData position data (shape = [timesteps, agents, 3]), and
        corresponding n_agents data, indicating agents per timestamp, extract
        all position data, skipping the zeros that represent no data. Provide
        minimum X, Y, and Z values from remaining data
        """
        if n_agents is not None:
            [x_data, y_data, z_data] = TrajectoryConverter._get_valid_agents(
                data, n_agents
            )
        else:
            x_data = data[:, :, 0].flatten()
            y_data = data[:, :, 1].flatten()
            z_data = data[:, :, 2].flatten()

        return np.array([min(x_data), min(y_data), min(z_data)])

    @staticmethod
    def get_subpoints_xyz(subpoints: np.array, n_subpoints: np.array) -> np.array:
        """
        Given AgentData subpoints (shape = [timesteps, agents, subpoints]), and a
        list of n_subpoints per agent per timestep (shape = [timesteps, agents])
        extract all subpoint data, skipping the zeros which represent no data.
        Reshape resulting subpoint data into a 2D array of XYZ coordinate data
        """
        xyz_subpoints = np.array([])
        for timestep in range(len(n_subpoints)):
            for agent in range(len(n_subpoints[timestep])):
                xyz_subpoints = np.append(
                    xyz_subpoints,
                    subpoints[timestep][agent][0 : int(n_subpoints[timestep][agent])],
                )
        return xyz_subpoints.reshape(1, -1, 3)

    @staticmethod
    def translate_positions(data: AgentData, translation: np.ndarray) -> AgentData:
        """
        Translate all spatial data for each frame of simularium trajectory data

        Parameters
        ----------
        data : AgentData
            Trajectory data, containing the spatial data to be traslated
        translation : np.ndarray (shape = [3])
            XYZ translation
        """
        total_steps = data.times.size
        max_subpoints = int(np.amax(data.n_subpoints))
        for time_index in range(total_steps):
            for agent_index in range(int(data.n_agents[time_index])):
                display_type = data.display_type_for_agent(time_index, agent_index)
                has_fiber_subpoints = (
                    max_subpoints > 0 and display_type == DISPLAY_TYPE.FIBER
                )
                if has_fiber_subpoints:
                    # only translate subpoints for fibers, since sphere group
                    # subpoint positions are relative to agent's position, and no
                    # other display types have subpoints currently
                    sp_items = Filter.get_items_from_subpoints(
                        data, time_index, agent_index
                    )
                    if sp_items is None:
                        has_fiber_subpoints = False
                    else:
                        # translate subpoints for fibers
                        n_items = sp_items.shape[0]
                        for item_index in range(n_items):
                            sp_items[item_index][:VALUES_PER_3D_POINT] += translation
                        n_sp = int(data.n_subpoints[time_index][agent_index])
                        data.subpoints[time_index][agent_index][
                            :n_sp
                        ] = sp_items.reshape(n_sp)
                if not has_fiber_subpoints:
                    # agents for fibers don't have their own position data, so only
                    # translate agents without fiber subpoints. eventually, if fiber
                    # subpoints are relative to agent position, we can just translate
                    # the agent position and leave the subpoints as is
                    data.positions[time_index][agent_index] += translation

        return data

    @staticmethod
    def get_min_max_positions(
        agent_data: AgentData,
    ) -> Tuple[np.array, np.array]:
        max_dimensions = TrajectoryConverter.get_xyz_max(
            agent_data.positions + agent_data.radii[:, :, np.newaxis],
            agent_data.n_agents,
        )
        min_dimensions = TrajectoryConverter.get_xyz_min(
            agent_data.positions - agent_data.radii[:, :, np.newaxis],
            agent_data.n_agents,
        )

        if (
            agent_data.subpoints is not None
            and agent_data.n_subpoints is not None
            and agent_data.subpoints.size > 0
        ):
            xyz_subpoints = TrajectoryConverter.get_subpoints_xyz(
                agent_data.subpoints, agent_data.n_subpoints
            )
            max_subpoints = TrajectoryConverter.get_xyz_max(xyz_subpoints)
            min_subpoints = TrajectoryConverter.get_xyz_min(xyz_subpoints)
            max_dimensions = np.amax([max_dimensions, max_subpoints], 0)
            min_dimensions = np.amin([min_dimensions, min_subpoints], 0)
        return (min_dimensions, max_dimensions)

    def _get_scale_factor_with_min_max(
        min_dimensions: np.array,
        max_dimensions: np.array,
    ) -> float:
        range = max(max_dimensions - min_dimensions)
        scale_factor = 1
        if np.isclose(range, 0):
            return scale_factor
        if range > VIEWER_DIMENSION_RANGE.MAX:
            scale_factor = VIEWER_DIMENSION_RANGE.MAX / range
        elif range < VIEWER_DIMENSION_RANGE.MIN:
            scale_factor = VIEWER_DIMENSION_RANGE.MIN / range
        return scale_factor

    @staticmethod
    def calculate_scale_factor(
        agent_data: AgentData,
    ) -> float:
        """
        Return a scale factor, using the given position, radii,
        and subpoints, data from AgentData, so that the final range of agent
        locations is within the dimensions defined by VIEWER_DIMENSION_RANGE.
        """
        min_dimensions, max_dimensions = TrajectoryConverter.get_min_max_positions(
            agent_data
        )
        return TrajectoryConverter._get_scale_factor_with_min_max(
            min_dimensions, max_dimensions
        )

    @staticmethod
    def scale_agent_data(
        agent_data: AgentData,
        input_scale_factor: float = None,
    ) -> Tuple[AgentData, float]:
        """
        Return a scaled AgentData object, either using a provided scale
        factor if input_scale_factor is given, or using a calculated scale
        factor using calculate_scale_factor() with the provided agent data.
        Also returns the scale factor that was used on the AgentData object.
        """
        if input_scale_factor is None:
            # If scale factor wasn't provided, calculate one
            scale_factor = TrajectoryConverter.calculate_scale_factor(agent_data)
        else:
            scale_factor = input_scale_factor
        agent_data.radii *= scale_factor
        agent_data.positions *= scale_factor
        agent_data.subpoints *= scale_factor
        return agent_data, scale_factor

    def center_and_scale_agent_data(
        agent_data: AgentData,
        input_scale_factor: float = None,
    ) -> Tuple[AgentData, float]:
        """
        Center the provided agent_data at the origin, based on the range of
        XYZ position data and subpoint data. In addition, scale position
        and radii data based on the input_scale_factor if provided, otherwise
        calculate the scale factor using calculate_scale_factor(). Returns the
        centered and scaled AgentData, and the scale factor that was applied
        """
        min_dimensions, max_dimensions = TrajectoryConverter.get_min_max_positions(
            agent_data
        )
        translation = -0.5 * (max_dimensions + min_dimensions)

        translated_data = TrajectoryConverter.translate_positions(
            agent_data, translation
        )
        if input_scale_factor is None:
            # If scale factor wasn't provided, calculate one
            scale_factor = TrajectoryConverter._get_scale_factor_with_min_max(
                min_dimensions, max_dimensions
            )
        else:
            scale_factor = input_scale_factor
        return TrajectoryConverter.scale_agent_data(translated_data, scale_factor)

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
