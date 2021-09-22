#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from typing import Any, Dict, List

import numpy as np

from ..data_objects import (
    AgentData,
    TrajectoryData,
)
from ..constants import V1_SPATIAL_BUFFER_STRUCT
from .writer import Writer

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class JsonWriter(Writer):
    @staticmethod
    def _format_timestep(number: float) -> float:
        return float("%.4g" % number)

    @staticmethod
    def _get_spatial_bundle_data_subpoints(
        agent_data: AgentData,
        type_ids: np.ndarray,
    ) -> List[Dict[str, Any]]:
        """
        Return the spatialData's bundleData for a simulation
        of agents with subpoints, packing buffer with jagged data is slower
        """
        bundle_data: List[Dict[str, Any]] = []
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
            frame_data["data"], uids, used_unique_IDs = Writer._get_frame_buffer(
                time_index, agent_data, type_ids, -1, uids, used_unique_IDs
            )
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
        bundle_data: List[Dict[str, Any]] = []
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
    def format_trajectory_data(trajectory_data: TrajectoryData) -> Dict[str, Any]:
        """
        Return the data shaped for Simularium JSON
        Parameters
        ----------
        trajectory_data: TrajectoryData
            the data to format
        """
        print("Converting Trajectory Data to JSON -------------")
        inconsistent_type = Writer._check_types_match_subpoints(input_data)
        if inconsistent_type:
            raise DataError(inconsistent_type)
        simularium_data = {}
        # trajectory info
        total_steps = (
            trajectory_data.agent_data.n_timesteps
            if trajectory_data.agent_data.n_timesteps >= 0
            else len(trajectory_data.agent_data.times)
        )
        type_ids, type_mapping = trajectory_data.agent_data.get_type_ids_and_mapping()
        traj_info = {
            "version": CURRENT_VERSION.TRAJECTORY_INFO,
            "timeUnits": {
                "magnitude": trajectory_data.time_units.magnitude,
                "name": trajectory_data.time_units.name,
            },
            "timeStepSize": JsonWriter._format_timestep(
                float(
                    trajectory_data.agent_data.times[1]
                    - trajectory_data.agent_data.times[0]
                )
                if total_steps > 1
                else 0.0
            ),
            "totalSteps": total_steps,
            "spatialUnits": {
                "magnitude": trajectory_data.spatial_units.magnitude,
                "name": trajectory_data.spatial_units.name,
            },
            "size": {
                "x": float(trajectory_data.meta_data.box_size[0]),
                "y": float(trajectory_data.meta_data.box_size[1]),
                "z": float(trajectory_data.meta_data.box_size[2]),
            },
            "cameraDefault": {
                "position": {
                    "x": float(trajectory_data.meta_data.camera_defaults.position[0]),
                    "y": float(trajectory_data.meta_data.camera_defaults.position[1]),
                    "z": float(trajectory_data.meta_data.camera_defaults.position[2]),
                },
                "lookAtPosition": {
                    "x": float(
                        trajectory_data.meta_data.camera_defaults.look_at_position[0]
                    ),
                    "y": float(
                        trajectory_data.meta_data.camera_defaults.look_at_position[1]
                    ),
                    "z": float(
                        trajectory_data.meta_data.camera_defaults.look_at_position[2]
                    ),
                },
                "upVector": {
                    "x": float(trajectory_data.meta_data.camera_defaults.up_vector[0]),
                    "y": float(trajectory_data.meta_data.camera_defaults.up_vector[1]),
                    "z": float(trajectory_data.meta_data.camera_defaults.up_vector[2]),
                },
                "fovDegrees": float(
                    trajectory_data.meta_data.camera_defaults.fov_degrees
                ),
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
        if trajectory_data.agent_data.subpoints is not None:
            spatialData["bundleData"] = JsonWriter._get_spatial_bundle_data_subpoints(
                trajectory_data.agent_data, type_ids
            )
        else:
            spatialData[
                "bundleData"
            ] = JsonWriter._get_spatial_bundle_data_no_subpoints(
                trajectory_data.agent_data, type_ids
            )
        simularium_data["spatialData"] = spatialData
        # plot data
        simularium_data["plotData"] = {
            "version": CURRENT_VERSION.PLOT_DATA,
            "data": trajectory_data.plots,
        }
        return simularium_data

    @staticmethod
    def save(trajectory_data: TrajectoryData, output_path: str) -> None:
        """
        Save the simularium data in .simularium JSON format
        at the output path
        Parameters
        ----------
        trajectory_data: TrajectoryData
            the data to save
        output_path: str
            where to save the file
        """
        json_data = JsonWriter.format_trajectory_data(trajectory_data)
        print("Writing JSON -------------")
        with open(f"{output_path}.simularium", "w+") as outfile:
            json.dump(json_data, outfile)
        print(f"saved to {output_path}.simularium")

    @staticmethod
    def save_plot_data(plot_data: List[Dict[str, Any]], output_path: str):
        """
        Save the current plot data in JSON format
        at the output path
        Parameters
        ----------
        plot_data: List[Dict[str, Any]]
            the data to save
        output_path: str
            where to save the file
        """
        with open(f"{output_path}_plot-data.json", "w+") as outfile:
            json.dump(
                {
                    "version": 1,
                    "data": plot_data,
                }, 
                outfile
            )