#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Tuple, Dict, Any
import math

import numpy as np

from ..constants import V1_SPATIAL_BUFFER_STRUCT

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class AgentData:
    times: np.ndarray
    n_agents: np.ndarray
    viz_types: np.ndarray
    unique_ids: np.ndarray
    types: List[List[str]]
    positions: np.ndarray
    rotations: np.ndarray
    radii: np.ndarray
    n_subpoints: np.ndarray = None
    subpoints: np.ndarray = None
    draw_fiber_points: bool = False
    type_ids: np.ndarray

    def __init__(
        self,
        times: np.ndarray,
        n_agents: np.ndarray,
        viz_types: np.ndarray,
        unique_ids: np.ndarray,
        types: List[List[str]],
        positions: np.ndarray,
        radii: np.ndarray,
        rotations: np.ndarray = None,
        n_subpoints: np.ndarray = None,
        subpoints: np.ndarray = None,
        draw_fiber_points: bool = False,
        type_ids: np.ndarray = None,
    ):
        """
        This object contains spatial simulation data

        Parameters
        ----------
        times : np.ndarray (shape = [timesteps])
            A numpy ndarray containing the elapsed simulated time
            at each timestep (in the units specified by
            TrajectoryData.time_units)
        n_agents : np.ndarray (shape = [timesteps])
            A numpy ndarray containing the number of agents
            that exist at each timestep
        viz_types : np.ndarray (shape = [timesteps, agents])
            A numpy ndarray containing the viz type
            for each agent at each timestep. Current options:
                1000 : default,
                1001 : fiber (which will require subpoints)
        unique_ids : np.ndarray (shape = [timesteps, agents])
            A numpy ndarray containing the unique ID
            for each agent at each timestep
        types : List[List[str]] (list of shape [timesteps, agents])
            A list containing timesteps, for each a list of
            the string name for the type of each agent
        positions : np.ndarray (shape = [timesteps, agents, 3])
            A numpy ndarray containing the XYZ position
            for each agent at each timestep (in the units
            specified by TrajectoryData.spatial_units)
        radii : np.ndarray (shape = [timesteps, agents])
            A numpy ndarray containing the radius
            for each agent at each timestep
        rotations: np.ndarray (shape = [timesteps, agents, 3]) (optional)
            A numpy ndarray containing the XYZ rotation
            for each particle at each timestep
        n_subpoints : np.ndarray (shape = [timesteps, agents]) (optional)
            A numpy ndarray containing the number of subpoints
            belonging to each agent at each timestep. Required if
            subpoints are provided
            Default: None
        subpoints : np.ndarray
        (shape = [timesteps, agents, subpoints, 3]) (optional)
            A numpy ndarray containing a list of subpoint position data
            for each agent at each timestep. These values are
            currently only used for fiber agents
            Default: None
        draw_fiber_points: bool (optional)
            Draw spheres at every other fiber point for fibers?
            Default: False
        """
        self.times = times
        self.n_agents = n_agents
        self.viz_types = viz_types
        self.unique_ids = unique_ids
        self.types = types
        self.positions = positions
        self.radii = radii
        self.rotations = rotations
        self.n_subpoints = n_subpoints
        self.subpoints = subpoints
        self.draw_fiber_points = draw_fiber_points
        self.type_ids = type_ids

    @staticmethod
    def _get_buffer_data_dimensions(buffer_data: Dict[str, Any]) -> Tuple[int]:
        """"""
        bundle_data = buffer_data["spatialData"]["bundleData"]
        total_steps = len(bundle_data)
        max_n_agents = 0
        max_n_subpoints = 0
        for t in range(total_steps):
            data = bundle_data[t]["data"]
            i = 0
            n_agents = 0
            while i < len(data):
                # a new agent should start at this index
                n_agents += 1
                i += V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                # get the number of subpoints
                n_sp = math.floor(data[i] / 3.0)
                if n_sp > max_n_subpoints:
                    max_n_subpoints = n_sp
                i += int(
                    data[i]
                    + (
                        V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT
                        - V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                        - 1
                    )
                )
            if n_agents > max_n_agents:
                max_n_agents = n_agents
        return total_steps, max_n_agents, max_n_subpoints

    @staticmethod
    def get_type_ids_and_mapping(
        type_names: List[List[str]], type_ids: np.ndarray = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Generate the type_ids array from the type_names list
        """
        total_steps = len(type_names)
        max_agents = 0
        for t in range(len(type_names)):
            n = len(type_names[t])
            if n > max_agents:
                max_agents = n
        use_existing_ids = True
        if type_ids is None:
            type_ids = np.zeros((len(type_names), max_agents))
            use_existing_ids = False
        type_name_mapping = {}
        type_id_mapping = {}
        last_tid = 0
        for t in range(total_steps):
            for n in range(len(type_names[t])):
                if type_names[t][n] not in type_id_mapping:
                    if use_existing_ids:
                        tid = int(type_ids[t][n])
                    else:
                        tid = last_tid
                        last_tid += 1
                    type_id_mapping[type_names[t][n]] = tid
                    type_name_mapping[str(tid)] = {"name": type_names[t][n]}
                if not use_existing_ids:
                    type_ids[t][n] = type_id_mapping[type_names[t][n]]
        return type_ids, type_name_mapping

    @staticmethod
    def get_type_names(
        type_ids: np.ndarray, type_mapping: Dict[str, Any]
    ) -> List[List[str]]:
        """
        Generate the type_names list from the type_ids array
        """
        result = []
        for t in range(type_ids.shape[0]):
            result.append([])
            for n in range(int(len(type_ids[t]))):
                result[t].append(type_mapping[str(int(type_ids[t][n]))]["name"])
        return result

    @classmethod
    def from_buffer_data(cls, buffer_data: Dict[str, Any]):
        """"""
        bundle_data = buffer_data["spatialData"]["bundleData"]
        total_steps, max_agents, max_subpoints = AgentData._get_buffer_data_dimensions(
            buffer_data
        )
        print(
            f"original dim = {total_steps} timesteps X "
            f"{max_agents} agents X {max_subpoints} subpoints"
        )
        times = np.zeros(total_steps)
        n_agents = np.zeros(total_steps)
        viz_types = np.zeros((total_steps, max_agents))
        unique_ids = np.zeros((total_steps, max_agents))
        type_ids = np.zeros((total_steps, max_agents))
        positions = np.zeros((total_steps, max_agents, 3))
        radii = np.ones((total_steps, max_agents))
        n_subpoints = np.zeros((total_steps, max_agents))
        subpoints = np.zeros((total_steps, max_agents, max_subpoints, 3))
        for t in range(total_steps):
            times[t] = bundle_data[t]["time"]
            frame_data = bundle_data[t]["data"]
            n = 0
            i = 0
            while i + V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX < len(frame_data):
                # a new agent should start at this index
                viz_types[t][n] = frame_data[
                    i + V1_SPATIAL_BUFFER_STRUCT.VIZ_TYPE_INDEX
                ]
                unique_ids[t][n] = frame_data[i + V1_SPATIAL_BUFFER_STRUCT.UID_INDEX]
                type_ids[t][n] = frame_data[i + V1_SPATIAL_BUFFER_STRUCT.TID_INDEX]
                positions[t][n] = [
                    frame_data[i + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX],
                    frame_data[i + V1_SPATIAL_BUFFER_STRUCT.POSY_INDEX],
                    frame_data[i + V1_SPATIAL_BUFFER_STRUCT.POSZ_INDEX],
                ]
                radii[t][n] = frame_data[i + V1_SPATIAL_BUFFER_STRUCT.R_INDEX]
                i += V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                # get the subpoints
                if max_subpoints < 1:
                    i += int(
                        V1_SPATIAL_BUFFER_STRUCT.SP_INDEX
                        - V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                    )
                    n += 1
                    continue
                n_subpoints[t][n] = int(frame_data[i] / 3.0)
                p = 0
                d = 0
                for j in range(int(frame_data[i])):
                    subpoints[t][n][p][d] = frame_data[i + 1 + j]
                    d += 1
                    if d > 2:
                        d = 0
                        p += 1
                i += int(
                    frame_data[i]
                    + (
                        V1_SPATIAL_BUFFER_STRUCT.SP_INDEX
                        - V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                    )
                )
                n += 1
            n_agents[t] = n
        type_names = AgentData.get_type_names(
            type_ids, buffer_data["trajectoryInfo"]["typeMapping"]
        )
        return cls(
            times=times,
            n_agents=n_agents,
            viz_types=viz_types,
            unique_ids=unique_ids,
            types=type_names,
            positions=positions,
            radii=radii,
            n_subpoints=n_subpoints,
            subpoints=subpoints,
            draw_fiber_points=False,
            type_ids=type_ids,
        )
