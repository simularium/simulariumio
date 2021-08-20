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
from ..constants import V1_SPATIAL_BUFFER_STRUCT, VIZ_TYPE

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
    def _get_frame_buffer_size(
        time_index: int,
        agent_data: AgentData,
    ) -> int:
        """
        Get the required size for a buffer to hold the given frame of AgentData
        """
        n_agents = int(agent_data.n_agents[time_index])
        buffer_size = (V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT - 1) * n_agents
        for agent_index in range(n_agents):
            n_subpoints = int(agent_data.n_subpoints[time_index][agent_index])
            if n_subpoints > 0:
                buffer_size += 3 * n_subpoints
                if agent_data.draw_fiber_points:
                    buffer_size += (
                        V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT - 1
                    ) * max(math.ceil(n_subpoints / 2.0), 1)
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
            if n_subpoints > 0:
                # add subpoints to fiber agent
                subpoints = [3 * n_subpoints]
                for p in range(n_subpoints):
                    for d in range(3):
                        subpoints.append(
                            agent_data.subpoints[time_index][agent_index][p][d]
                        )
                result[
                    i
                    + V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX : i
                    + V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                    + 1
                    + 3 * n_subpoints
                ] = subpoints
                i += (V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT - 1) + 3 * n_subpoints
                # optionally draw spheres at points
                if agent_data.draw_fiber_points:
                    for p in range(n_subpoints):
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
                        result[
                            i
                            + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX : i
                            + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX
                            + 3
                        ] = agent_data.subpoints[time_index][agent_index][p]
                        result[i + V1_SPATIAL_BUFFER_STRUCT.R_INDEX] = 0.5
                        i += V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT - 1
            else:
                i += V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT - 1
        return result.tolist(), uids, used_unique_IDs
