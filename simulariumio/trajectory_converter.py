#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from typing import Any, Dict, List
import math
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
    AgentData,
    TrajectoryData,
    DisplayData,
)
from .filters import Filter
from .exceptions import UnsupportedPlotTypeError, DataError
from .constants import V1_SPATIAL_BUFFER_STRUCT, VIZ_TYPE, DISPLAY_TYPE, CURRENT_VERSION

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
    def _read_trajectory_data(input_data: TrajectoryData) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """
        print("Converting Trajectory Data -------------")
        inconsistent_type = TrajectoryConverter._check_types_match_subpoints(input_data)
        if inconsistent_type:
            raise DataError(inconsistent_type)
        simularium_data = {}
        # trajectory info
        total_steps = (
            input_data.agent_data.n_timesteps
            if input_data.agent_data.n_timesteps >= 0
            else len(input_data.agent_data.times)
        )
        type_ids, type_mapping = input_data.agent_data.get_type_ids_and_mapping()
        traj_info = {
            "version": CURRENT_VERSION.TRAJECTORY_INFO,
            "timeUnits": {
                "magnitude": input_data.time_units.magnitude,
                "name": input_data.time_units.name,
            },
            "timeStepSize": TrajectoryConverter._format_timestep(
                float(input_data.agent_data.times[1] - input_data.agent_data.times[0])
                if total_steps > 1
                else 0.0
            ),
            "totalSteps": total_steps,
            "spatialUnits": {
                "magnitude": input_data.spatial_units.magnitude,
                "name": input_data.spatial_units.name,
            },
            "size": {
                "x": float(input_data.meta_data.box_size[0]),
                "y": float(input_data.meta_data.box_size[1]),
                "z": float(input_data.meta_data.box_size[2]),
            },
            "cameraDefault": {
                "position": {
                    "x": float(input_data.meta_data.camera_defaults.position[0]),
                    "y": float(input_data.meta_data.camera_defaults.position[1]),
                    "z": float(input_data.meta_data.camera_defaults.position[2]),
                },
                "lookAtPosition": {
                    "x": float(
                        input_data.meta_data.camera_defaults.look_at_position[0]
                    ),
                    "y": float(
                        input_data.meta_data.camera_defaults.look_at_position[1]
                    ),
                    "z": float(
                        input_data.meta_data.camera_defaults.look_at_position[2]
                    ),
                },
                "upVector": {
                    "x": float(input_data.meta_data.camera_defaults.up_vector[0]),
                    "y": float(input_data.meta_data.camera_defaults.up_vector[1]),
                    "z": float(input_data.meta_data.camera_defaults.up_vector[2]),
                },
                "fovDegrees": float(input_data.meta_data.camera_defaults.fov_degrees),
            },
            "typeMapping": type_mapping,
        }
        # add any paper metadata
        if input_data.meta_data.trajectory_title:
            traj_info["trajectoryTitle"] = input_data.meta_data.trajectory_title
        if not input_data.meta_data.model_meta_data.is_default():
            traj_info["modelInfo"] = dict(input_data.meta_data.model_meta_data)
        simularium_data["trajectoryInfo"] = traj_info
        # spatial data
        spatialData = {
            "version": CURRENT_VERSION.SPATIAL_DATA,
            "msgType": 1,
            "bundleStart": 0,
            "bundleSize": total_steps,
        }
        if input_data.agent_data.subpoints is not None:
            spatialData[
                "bundleData"
            ] = TrajectoryConverter._get_spatial_bundle_data_subpoints(
                input_data.agent_data, type_ids
            )
        else:
            spatialData[
                "bundleData"
            ] = TrajectoryConverter._get_spatial_bundle_data_no_subpoints(
                input_data.agent_data, type_ids
            )
        simularium_data["spatialData"] = spatialData
        # plot data
        simularium_data["plotData"] = {
            "version": CURRENT_VERSION.PLOT_DATA,
            "data": input_data.plots,
        }
        return simularium_data

    @staticmethod
    def _get_spatial_bundle_data_subpoints(
        agent_data: AgentData,
        type_ids: np.ndarray,
    ) -> List[Dict[str, Any]]:
        """
        Return the spatialData's bundleData for a simulation
        of agents with subpoints, packing buffer with jagged data is slower
        """
        bundle_data = []
        uids = {}
        used_unique_IDs = list(np.unique(agent_data.unique_ids))
        total_steps = (
            agent_data.n_timesteps
            if agent_data.n_timesteps >= 0
            else len(agent_data.times)
        )
        for time_index in range(total_steps):
            # timestep
            frame_data = {}
            frame_data["frameNumber"] = time_index
            frame_data["time"] = float(agent_data.times[time_index])
            n_agents = int(agent_data.n_agents[time_index])
            i = 0
            buffer_size = (V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT - 1) * n_agents
            for agent_index in range(n_agents):
                n_subpoints = int(agent_data.n_subpoints[time_index][agent_index])
                if n_subpoints > 0:
                    buffer_size += 3 * n_subpoints
                    if agent_data.draw_fiber_points:
                        buffer_size += (
                            V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT - 1
                        ) * max(math.ceil(n_subpoints / 2.0), 1)
            local_buf = np.zeros(buffer_size)
            for agent_index in range(n_agents):
                # add agent
                local_buf[
                    i + V1_SPATIAL_BUFFER_STRUCT.VIZ_TYPE_INDEX
                ] = agent_data.viz_types[time_index, agent_index]
                local_buf[
                    i + V1_SPATIAL_BUFFER_STRUCT.UID_INDEX
                ] = agent_data.unique_ids[time_index, agent_index]
                local_buf[i + V1_SPATIAL_BUFFER_STRUCT.TID_INDEX] = type_ids[
                    time_index, agent_index
                ]
                local_buf[
                    i
                    + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX : i
                    + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX
                    + 3
                ] = agent_data.positions[time_index, agent_index]
                local_buf[
                    i
                    + V1_SPATIAL_BUFFER_STRUCT.ROTX_INDEX : i
                    + V1_SPATIAL_BUFFER_STRUCT.ROTX_INDEX
                    + 3
                ] = agent_data.rotations[time_index, agent_index]
                local_buf[i + V1_SPATIAL_BUFFER_STRUCT.R_INDEX] = agent_data.radii[
                    time_index, agent_index
                ]
                n_subpoints = int(agent_data.n_subpoints[time_index][agent_index])
                if n_subpoints > 0:
                    # add subpoints to fiber agent
                    subpoints = [3 * n_subpoints]
                    for p in range(n_subpoints):
                        for d in range(3):
                            subpoints.append(
                                agent_data.subpoints[time_index][agent_index][p][d]
                            )
                    local_buf[
                        i
                        + V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX : i
                        + V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                        + 1
                        + 3 * n_subpoints
                    ] = subpoints
                    i += (
                        V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT - 1
                    ) + 3 * n_subpoints
                    # optionally draw spheres at points
                    if agent_data.draw_fiber_points:
                        for p in range(n_subpoints):
                            # every other fiber point
                            if p % 2 != 0:
                                continue
                            # unique instance ID
                            raw_uid = (
                                100
                                * (agent_data.unique_ids[time_index, agent_index] + 1)
                                + p
                            )
                            if raw_uid not in uids:
                                uid = raw_uid
                                while uid in used_unique_IDs:
                                    uid += 100
                                uids[raw_uid] = uid
                                used_unique_IDs.append(uid)
                            # add sphere
                            local_buf[
                                i + V1_SPATIAL_BUFFER_STRUCT.VIZ_TYPE_INDEX
                            ] = VIZ_TYPE.DEFAULT
                            local_buf[i + V1_SPATIAL_BUFFER_STRUCT.UID_INDEX] = uids[
                                raw_uid
                            ]
                            local_buf[
                                i + V1_SPATIAL_BUFFER_STRUCT.TID_INDEX
                            ] = type_ids[time_index, agent_index]
                            local_buf[
                                i
                                + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX : i
                                + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX
                                + 3
                            ] = agent_data.subpoints[time_index][agent_index][p]
                            local_buf[i + V1_SPATIAL_BUFFER_STRUCT.R_INDEX] = 0.5
                            i += V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT - 1
                else:
                    i += V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT - 1
            frame_data["data"] = local_buf.tolist()
            bundle_data.append(frame_data)
        return bundle_data

    @staticmethod
    def _get_spatial_bundle_data_no_subpoints(
        agent_data: AgentData,
        type_ids: np.ndarray,
    ) -> List[Dict[str, Any]]:
        """
        Return the spatialData's bundleData for a simulation
        of agents without subpoints, using list slicing for speed
        """
        bundle_data = []
        max_n_agents = int(np.amax(agent_data.n_agents, 0))
        ix_positions = np.empty((3 * max_n_agents,), dtype=int)
        ix_rotations = np.empty((3 * max_n_agents,), dtype=int)
        buffer_struct = V1_SPATIAL_BUFFER_STRUCT
        for i in range(max_n_agents):
            ix_positions[3 * i : 3 * i + 3] = np.arange(
                i * (buffer_struct.VALUES_PER_AGENT - 1) + buffer_struct.POSX_INDEX,
                i * (buffer_struct.VALUES_PER_AGENT - 1) + buffer_struct.POSX_INDEX + 3,
            )
            ix_rotations[3 * i : 3 * i + 3] = np.arange(
                i * (buffer_struct.VALUES_PER_AGENT - 1) + buffer_struct.ROTX_INDEX,
                i * (buffer_struct.VALUES_PER_AGENT - 1) + buffer_struct.ROTX_INDEX + 3,
            )
        frame_buf = np.zeros((buffer_struct.VALUES_PER_AGENT - 1) * max_n_agents)
        total_steps = (
            agent_data.n_timesteps
            if agent_data.n_timesteps >= 0
            else len(agent_data.times)
        )
        for time_index in range(total_steps):
            frame_data = {}
            frame_data["frameNumber"] = time_index
            frame_data["time"] = float(agent_data.times[time_index])
            n_agents = int(agent_data.n_agents[time_index])
            local_buf = frame_buf[: (buffer_struct.VALUES_PER_AGENT - 1) * n_agents]
            local_buf[
                buffer_struct.VIZ_TYPE_INDEX :: buffer_struct.VALUES_PER_AGENT - 1
            ] = agent_data.viz_types[time_index, :n_agents]
            local_buf[
                buffer_struct.UID_INDEX :: buffer_struct.VALUES_PER_AGENT - 1
            ] = agent_data.unique_ids[time_index, :n_agents]
            local_buf[
                buffer_struct.TID_INDEX :: buffer_struct.VALUES_PER_AGENT - 1
            ] = type_ids[time_index, :n_agents]
            local_buf[ix_positions[: 3 * n_agents]] = agent_data.positions[
                time_index, :n_agents
            ].flatten()
            local_buf[ix_rotations[: 3 * n_agents]] = agent_data.rotations[
                time_index, :n_agents
            ].flatten()
            local_buf[
                buffer_struct.R_INDEX :: buffer_struct.VALUES_PER_AGENT - 1
            ] = agent_data.radii[time_index, :n_agents]
            frame_data["data"] = local_buf.tolist()
            bundle_data.append(frame_data)
        return bundle_data

    @staticmethod
    def _check_agent_ids_are_unique_per_frame(buffer_data: Dict[str, Any]) -> bool:
        """
        For each frame, check that none of the unique agent IDs overlap
        """
        bundle_data = buffer_data["spatialData"]["bundleData"]
        for time_index in range(len(bundle_data)):
            data = bundle_data[time_index]["data"]
            agent_index = 1
            uids = []
            get_n_subpoints = False
            while agent_index < len(data):
                # get the number of subpoints
                # in order to correctly increment index
                if get_n_subpoints:
                    agent_index += int(
                        data[agent_index]
                        + (
                            V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT
                            - V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                        )
                    )
                    get_n_subpoints = False
                    continue
                # there should be a unique ID at this index, check for duplicate
                uid = data[agent_index]
                if uid in uids:
                    raise Exception(
                        f"found duplicate ID {uid} in frame {time_index} "
                        f"at index {agent_index}"
                    )
                uids.append(uid)
                agent_index += V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX - 1
                get_n_subpoints = True
        return True

    @staticmethod
    def _check_type_matches_subpoints(
        type_name: str,
        n_subpoints: int,
        viz_type: float,
        display_data: DisplayData,
        debug_name: str = "",
    ) -> str:
        """
        If the agent has subpoints, check that it
        also has a display_type of "FIBER" and viz type of "FIBER", and vice versa.
        return a message saying what is inconsistent
        """
        has_subpoints = n_subpoints > 0
        msg = (
            f"Agent {debug_name}: Type {type_name} "
            + ("has" if has_subpoints else "does not have")
            + " subpoints and "
        )
        if has_subpoints != (viz_type == VIZ_TYPE.FIBER):
            return msg + f"viz type is {viz_type}"
        if type_name in display_data:
            display_type = display_data[type_name].display_type
            if display_type is not DISPLAY_TYPE.NONE and has_subpoints != (
                display_type == DISPLAY_TYPE.FIBER
            ):
                return msg + f"display type is {display_type}"
        return ""

    @staticmethod
    def _check_types_match_subpoints(trajectory_data: TrajectoryData) -> str:
        """
        For each frame, check that agents that have subpoints
        also have a display_type of "FIBER" and viz type of "FIBER", and vice versa.
        return a message with the type name of the first agent that is inconsistent
        """
        n_subpoints = trajectory_data.agent_data.n_subpoints
        display_data = trajectory_data.agent_data.display_data
        for time_index in range(n_subpoints.shape[0]):
            for agent_index in range(
                int(trajectory_data.agent_data.n_agents[time_index])
            ):
                inconsistent_type = TrajectoryConverter._check_type_matches_subpoints(
                    trajectory_data.agent_data.types[time_index][agent_index],
                    n_subpoints[time_index][agent_index],
                    trajectory_data.agent_data.viz_types[time_index][agent_index],
                    display_data,
                    f"at index Time = {time_index}, Agent = {agent_index}",
                )
                if inconsistent_type:
                    return inconsistent_type
        return ""

    @staticmethod
    def _format_timestep(number: float) -> float:
        return float("%.4g" % number)

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
        data: [ScatterPlotData or HistogramPlotData] = {},
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
        agent_data: AgentData
            The data shaped as an AgentData object
            Default: None (use the currently loaded data)
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
                xaxis_title=f"Time ({self._data.time_units.to_string()})",
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
        buffer_data = TrajectoryConverter._read_trajectory_data(self._data)
        return json.dumps(buffer_data)

    def write_JSON(self, output_path: str):
        """
        Save the current simularium data in .simularium JSON format
        at the output path

        Parameters
        ----------
        output_path: str
            where to save the file
        """
        print("Writing JSON -------------")
        buffer_data = TrajectoryConverter._read_trajectory_data(self._data)
        with open(f"{output_path}.simularium", "w+") as outfile:
            json.dump(buffer_data, outfile)
        print(f"saved to {output_path}.simularium")

    @staticmethod
    def write_external_JSON(external_data: TrajectoryData, output_path: str):
        """
        Save the given data in .simularium JSON format
        at the output path

        Parameters
        ----------
        external_data: TrajectoryData
            the data to save
        output_path: str
            where to save the file
        """
        print("Writing JSON (external)-------------")
        buffer_data = TrajectoryConverter._read_trajectory_data(external_data)
        with open(f"{output_path}.simularium", "w+") as outfile:
            json.dump(buffer_data, outfile)
        print(f"saved to {output_path}.simularium")
