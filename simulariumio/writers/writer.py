#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod
from typing import Any, List, Dict, Tuple
import math

import numpy as np

from ..data_objects import (
    TrajectoryData,
    AgentData,
)
from ..constants import (
    V1_SPATIAL_BUFFER_STRUCT,
    VIZ_TYPE,
    DISPLAY_TYPE,
    CURRENT_VERSION,
)

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class Writer(ABC):
    @staticmethod
    @abstractmethod
    def format_trajectory_data(self, trajectory_data: TrajectoryData) -> Any:
        pass

    @staticmethod
    @abstractmethod
    def save(self, trajectory_data: TrajectoryData) -> None:
        pass

    @staticmethod
    def _format_timestep(number: float) -> float:
        return float("%.4g" % number)

    @staticmethod
    def _get_trajectory_info(
        trajectory_data: TrajectoryData, total_steps: int, type_mapping: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Get the trajectoryInfo block for the trajectory
        """
        result = {
            "version": CURRENT_VERSION.TRAJECTORY_INFO,
            "timeUnits": {
                "magnitude": trajectory_data.time_units.magnitude,
                "name": trajectory_data.time_units.name,
            },
            "timeStepSize": Writer._format_timestep(
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
        if trajectory_data.meta_data.trajectory_title:
            result["trajectoryTitle"] = trajectory_data.meta_data.trajectory_title
        if not trajectory_data.meta_data.model_meta_data.is_default():
            result["modelInfo"] = dict(trajectory_data.meta_data.model_meta_data)
        return result

    @staticmethod
    def _get_frame_buffer_size(
        time_index: int,
        agent_data: AgentData,
    ) -> int:
        """
        Get the required size for a buffer to hold the given frame of AgentData
        """
        n_agents = int(agent_data.n_agents[time_index])
        buffer_size = (V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT) * n_agents
        for agent_index in range(n_agents):
            n_subpoints = int(agent_data.n_subpoints[time_index][agent_index])
            if n_subpoints > 0:
                buffer_size += n_subpoints
                if agent_data.draw_fiber_points:
                    buffer_size += (V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT) * max(
                        math.ceil(n_subpoints / 6.0), 1
                    )
        return buffer_size

    @staticmethod
    def _get_frame_buffer(
        time_index: int,
        agent_data: AgentData,
        type_ids: np.ndarray,
        buffer_size: int = -1,
        uids: Dict[int, int] = None,
        used_unique_IDs: List[int] = None,
    ) -> Tuple[List[float], Dict[int, int], List[int]]:
        """
        Get a float buffer for one frame of AgentData
        """
        if buffer_size < 0:
            buffer_size = Writer._get_frame_buffer_size(time_index, agent_data)
        if uids is None:
            uids = {}
        if used_unique_IDs is None:
            used_unique_IDs = []
        result = np.zeros(buffer_size)
        n_agents = int(agent_data.n_agents[time_index])
        i = 0
        for agent_index in range(n_agents):
            # add agent
            result[i + V1_SPATIAL_BUFFER_STRUCT.VIZ_TYPE_INDEX] = agent_data.viz_types[
                time_index, agent_index
            ]
            result[i + V1_SPATIAL_BUFFER_STRUCT.UID_INDEX] = agent_data.unique_ids[
                time_index, agent_index
            ]
            result[i + V1_SPATIAL_BUFFER_STRUCT.TID_INDEX] = type_ids[
                time_index, agent_index
            ]
            result[
                i
                + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX : i
                + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX
                + 3
            ] = agent_data.positions[time_index, agent_index]
            result[
                i
                + V1_SPATIAL_BUFFER_STRUCT.ROTX_INDEX : i
                + V1_SPATIAL_BUFFER_STRUCT.ROTX_INDEX
                + 3
            ] = agent_data.rotations[time_index, agent_index]
            result[i + V1_SPATIAL_BUFFER_STRUCT.R_INDEX] = agent_data.radii[
                time_index, agent_index
            ]
            n_subpoints = int(agent_data.n_subpoints[time_index][agent_index])
            result[i + V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX] = n_subpoints
            if n_subpoints > 0:
                # add subpoints
                sp_start_index = i + V1_SPATIAL_BUFFER_STRUCT.SP_INDEX
                result[
                    sp_start_index : sp_start_index + n_subpoints
                ] = agent_data.subpoints[time_index][agent_index][:n_subpoints]
                i += (V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT) + n_subpoints
                # optionally draw spheres at points
                if agent_data.draw_fiber_points:
                    type_name = agent_data.types[time_index][agent_index]
                    if type_name not in agent_data.display_data:
                        continue
                    display_type = agent_data.display_data[type_name].display_type
                    if display_type != DISPLAY_TYPE.FIBER:
                        continue
                    n_fiber_points = math.floor(n_subpoints / 3.0)
                    for p in range(n_fiber_points):
                        # every other fiber point
                        if p % 2 != 0:
                            continue
                        # unique instance ID
                        raw_uid = (
                            100 * (agent_data.unique_ids[time_index, agent_index] + 1)
                            + p
                        )
                        if raw_uid not in uids:
                            uid = raw_uid
                            while uid in used_unique_IDs:
                                uid += 100
                            uids[raw_uid] = uid
                            used_unique_IDs.append(uid)
                        # add sphere
                        result[
                            i + V1_SPATIAL_BUFFER_STRUCT.VIZ_TYPE_INDEX
                        ] = VIZ_TYPE.DEFAULT
                        result[i + V1_SPATIAL_BUFFER_STRUCT.UID_INDEX] = uids[raw_uid]
                        result[i + V1_SPATIAL_BUFFER_STRUCT.TID_INDEX] = type_ids[
                            time_index, agent_index
                        ]
                        first_subpoint_index = 3 * p
                        result[
                            i
                            + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX : i
                            + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX
                            + 3
                        ] = agent_data.subpoints[time_index][agent_index][
                            first_subpoint_index : first_subpoint_index + 3
                        ]
                        result[i + V1_SPATIAL_BUFFER_STRUCT.R_INDEX] = 0.5
                        i += V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT
            else:
                i += V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT
        return result.tolist(), uids, used_unique_IDs

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
                            + 1
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