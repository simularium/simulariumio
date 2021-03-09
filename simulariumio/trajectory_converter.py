#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from typing import Any, Dict, List
import math

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
    UnitData,
)
from .filters import Filter
from .exceptions import UnsupportedPlotTypeError
from .constants import V1_SPATIAL_BUFFER_STRUCT, VIZ_TYPE

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
        print("Reading Trajectory Data -------------")
        simularium_data = {}
        # trajectory info
        totalSteps = input_data.agent_data.times.size
        type_ids, type_name_mapping = AgentData.get_type_ids_and_mapping(
            input_data.agent_data.types, input_data.agent_data.type_ids
        )
        if input_data.agent_data.type_ids is None:
            input_data.agent_data.type_ids = type_ids
        if input_data.agent_data.type_mapping is None:
            input_data.agent_data.type_mapping = type_name_mapping
        traj_info = {
            "version": 2,
            "timeUnits": {
                "magnitude": input_data.time_units.magnitude,
                "name": input_data.time_units.name,
            },
            "timeStepSize": TrajectoryConverter._format_timestep(
                float(input_data.agent_data.times[1] - input_data.agent_data.times[0])
                if totalSteps > 1
                else 0.0
            ),
            "totalSteps": totalSteps,
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
                    "x": float(input_data.meta_data.default_camera_position[0]),
                    "y": float(input_data.meta_data.default_camera_position[1]),
                    "z": float(input_data.meta_data.default_camera_position[2]),
                },
                "rotation": {
                    "x": float(input_data.meta_data.default_camera_rotation[0]),
                    "y": float(input_data.meta_data.default_camera_rotation[1]),
                    "z": float(input_data.meta_data.default_camera_rotation[2]),
                },
            },
            "typeMapping": input_data.agent_data.type_mapping,
        }
        simularium_data["trajectoryInfo"] = traj_info
        # spatial data
        spatialData = {
            "version": 1,
            "msgType": 1,
            "bundleStart": 0,
            "bundleSize": totalSteps,
        }
        if input_data.agent_data.subpoints is not None:
            spatialData[
                "bundleData"
            ] = TrajectoryConverter._get_spatial_bundle_data_subpoints(
                input_data.agent_data
            )
        else:
            spatialData[
                "bundleData"
            ] = TrajectoryConverter._get_spatial_bundle_data_no_subpoints(
                input_data.agent_data
            )
        simularium_data["spatialData"] = spatialData
        # plot data
        simularium_data["plotData"] = {
            "version": 1,
            "data": input_data.plots,
        }
        return simularium_data

    @staticmethod
    def _get_spatial_bundle_data_subpoints(
        agent_data: AgentData,
    ) -> List[Dict[str, Any]]:
        """
        Return the spatialData's bundleData for a simulation
        of agents with subpoints, packing buffer with jagged data is slower
        """
        bundle_data: List[Dict[str, Any]] = []
        uids = {}
        used_unique_IDs = list(np.unique(agent_data.unique_ids))
        for t in range(len(agent_data.times)):
            # timestep
            frame_data = {}
            frame_data["frameNumber"] = t
            frame_data["time"] = float(agent_data.times[t])
            n_agents = int(agent_data.n_agents[t])
            i = 0
            buffer_size = (V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT - 1) * n_agents
            for n in range(n_agents):
                s = int(agent_data.n_subpoints[t][n])
                if s > 0:
                    buffer_size += 3 * s
                    if agent_data.draw_fiber_points:
                        buffer_size += (
                            V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT - 1
                        ) * max(math.ceil(s / 2.0), 1)
            local_buf = np.zeros(buffer_size)
            for n in range(n_agents):
                # add agent
                local_buf[
                    i + V1_SPATIAL_BUFFER_STRUCT.VIZ_TYPE_INDEX
                ] = agent_data.viz_types[t, n]
                local_buf[
                    i + V1_SPATIAL_BUFFER_STRUCT.UID_INDEX
                ] = agent_data.unique_ids[t, n]
                local_buf[i + V1_SPATIAL_BUFFER_STRUCT.TID_INDEX] = agent_data.type_ids[
                    t, n
                ]
                local_buf[
                    i
                    + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX : i
                    + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX
                    + 3
                ] = agent_data.positions[t, n]
                local_buf[i + V1_SPATIAL_BUFFER_STRUCT.R_INDEX] = agent_data.radii[t, n]
                n_subpoints = int(agent_data.n_subpoints[t][n])
                if n_subpoints > 0:
                    # add subpoints to fiber agent
                    subpoints = [3 * n_subpoints]
                    for p in range(n_subpoints):
                        for d in range(3):
                            subpoints.append(agent_data.subpoints[t][n][p][d])
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
                            raw_uid = 100 * (agent_data.unique_ids[t, n] + 1) + p
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
                            ] = agent_data.type_ids[t, n]
                            local_buf[
                                i
                                + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX : i
                                + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX
                                + 3
                            ] = agent_data.subpoints[t][n][p]
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
    ) -> List[Dict[str, Any]]:
        """
        Return the spatialData's bundleData for a simulation
        of agents without subpoints, using list slicing for speed
        """
        bundle_data: List[Dict[str, Any]] = []
        max_n_agents = int(np.amax(agent_data.n_agents, 0))
        ix_positions = np.empty((3 * max_n_agents,), dtype=int)
        buffer_struct = V1_SPATIAL_BUFFER_STRUCT
        for i in range(max_n_agents):
            ix_positions[3 * i : 3 * i + 3] = np.arange(
                i * (buffer_struct.VALUES_PER_AGENT - 1) + buffer_struct.POSX_INDEX,
                i * (buffer_struct.VALUES_PER_AGENT - 1) + buffer_struct.POSX_INDEX + 3,
            )
        frame_buf = np.zeros((buffer_struct.VALUES_PER_AGENT - 1) * max_n_agents)
        for t in range(len(agent_data.times)):
            frame_data = {}
            frame_data["frameNumber"] = t
            frame_data["time"] = float(agent_data.times[t])
            n = int(agent_data.n_agents[t])
            local_buf = frame_buf[: (buffer_struct.VALUES_PER_AGENT - 1) * n]
            local_buf[
                buffer_struct.VIZ_TYPE_INDEX :: buffer_struct.VALUES_PER_AGENT - 1
            ] = agent_data.viz_types[t, :n]
            local_buf[
                buffer_struct.UID_INDEX :: buffer_struct.VALUES_PER_AGENT - 1
            ] = agent_data.unique_ids[t, :n]
            local_buf[
                buffer_struct.TID_INDEX :: buffer_struct.VALUES_PER_AGENT - 1
            ] = agent_data.type_ids[t, :n]
            local_buf[ix_positions[: 3 * n]] = agent_data.positions[t, :n].flatten()
            local_buf[
                buffer_struct.R_INDEX :: buffer_struct.VALUES_PER_AGENT - 1
            ] = agent_data.radii[t, :n]
            frame_data["data"] = local_buf.tolist()
            bundle_data.append(frame_data)
        return bundle_data

    @staticmethod
    def _check_agent_ids_are_unique_per_frame(buffer_data: Dict[str, Any]) -> bool:
        """
        For each frame, check that none of the unique agent IDs overlap
        """
        bundle_data = buffer_data["spatialData"]["bundleData"]
        for t in range(len(bundle_data)):
            data = bundle_data[t]["data"]
            i = 1
            uids = []
            get_n_subpoints = False
            while i < len(data):
                # get the number of subpoints
                # in order to correctly increment index
                if get_n_subpoints:
                    i += int(
                        data[i]
                        + (
                            V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT
                            - V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                        )
                    )
                    get_n_subpoints = False
                    continue
                # there should be a unique ID at this index, check for duplicate
                uid = data[i]
                if uid in uids:
                    raise Exception(
                        f"found duplicate ID {uid} in frame {t} at index {i}"
                    )
                uids.append(uid)
                i += V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX - 1
                get_n_subpoints = True
        return True

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
        agent_data: AgentData = None,
        plot_title: str = "Number of agents over time",
        yaxis_title: str = "Number of agents",
        time_units: UnitData = UnitData("s"),
    ):
        """
        Add a scatterplot of the number of each type of agent over time

        Parameters
        ----------
        agent_data: AgentData
            The data shaped as an AgentData object
            Default: None (use the currently loaded data)
        """
        if agent_data is None:
            agent_data = self._data.agent_data
        n_agents = {}
        type_mapping = agent_data.get_type_mapping()
        for t in range(agent_data.times.size):
            for n in range(int(agent_data.n_agents[t])):
                type_name = type_mapping[str(int(agent_data.type_ids[t][n]))]["name"]
                if "#" in type_name:
                    type_name = type_name.split("#")[0]
                if type_name not in n_agents:
                    n_agents[type_name] = np.zeros_like(agent_data.times)
                n_agents[type_name][t] += 1
        self.add_plot(
            ScatterPlotData(
                title=plot_title,
                xaxis_title=f"Time ({time_units.to_string()})",
                yaxis_title=yaxis_title,
                xtrace=agent_data.times,
                ytraces=n_agents,
                render_mode="lines",
            )
        )

    def filter_data(self, filters: List[Filter]) -> TrajectoryData:
        """
        Return the simularium data with the given filter applied
        """
        filtered_data = self._data
        for f in filters:
            filtered_data = f.apply(filtered_data)
        return filtered_data

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
