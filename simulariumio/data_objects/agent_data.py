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
    radii: np.ndarray
    n_subpoints: np.ndarray = None
    subpoints: np.ndarray = None
    draw_fiber_points: bool = False
    type_ids: np.ndarray
    type_mapping: Dict[str, Any]

    def __init__(
        self,
        times: np.ndarray,
        n_agents: np.ndarray,
        viz_types: np.ndarray,
        unique_ids: np.ndarray,
        types: List[List[str]],
        positions: np.ndarray,
        radii: np.ndarray,
        n_subpoints: np.ndarray = None,
        subpoints: np.ndarray = None,
        draw_fiber_points: bool = False,
        type_ids: np.ndarray = None,
    ):
        """
        This object contains custom simulation trajectory outputs
        and plot data

        Parameters
        ----------
        times : np.ndarray (shape = [timesteps])
            A numpy ndarray containing the elapsed simulated time
            in seconds at each timestep
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
            for each agent at each timestep
        radii : np.ndarray (shape = [timesteps, agents])
            A numpy ndarray containing the radius
            for each agent at each timestep
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
        self.n_subpoints = n_subpoints
        self.subpoints = subpoints
        self.draw_fiber_points = draw_fiber_points
        self.type_ids = type_ids

    @staticmethod
    def _get_data_dimensions(data: Dict[str, Any]) -> Tuple[int]:
        """"""
        bundleData = data["spatialData"]["bundleData"]
        total_steps = len(bundleData)
        max_n_agents = 0
        max_n_subpoints = 0
        for t in range(total_steps):
            data = bundleData[t]["data"]
            i = 0
            n_agents = 0
            while i < len(data):
                # a new agent should start at this index
                n_agents += 1
                i += V1_SPATIAL_BUFFER_STRUCT.index("NSP")
                # get the number of subpoints
                n_sp = math.floor(data[i] / 3.0)
                if n_sp > max_n_subpoints:
                    max_n_subpoints = n_sp
                i += int(
                    data[i]
                    + (
                        len(V1_SPATIAL_BUFFER_STRUCT)
                        - V1_SPATIAL_BUFFER_STRUCT.index("NSP")
                        - 1
                    )
                )
            if n_agents > max_n_agents:
                max_n_agents = n_agents
        return total_steps, max_n_agents, max_n_subpoints

    def get_type_mapping(self) -> Dict[str, Any]:
        """
        Generate the type mapping using the types list,
        set the type_ids list if it hasn't been
        """
        type_ids = np.zeros_like(self.viz_types)
        type_name_mapping = {}
        type_id_mapping = {}
        last_tid = 0
        for t in range(self.times.size):
            for n in range(int(self.n_agents[t])):
                type_name = self.types[t][n]
                if type_name not in type_name_mapping:
                    if self.type_ids is not None:
                        tid = int(self.type_ids[t][n])
                    else:
                        tid = last_tid
                        last_tid += 1
                    type_id_mapping[type_name] = tid
                    type_name_mapping[str(tid)] = {"name": type_name}
                type_ids[t][n] = type_id_mapping[type_name]
        if self.type_ids is None:
            self.type_ids = type_ids
        return type_name_mapping

    @classmethod
    def from_simularium_data(cls, data: Dict[str, Any]):
        """
        """
        bundleData = data["spatialData"]["bundleData"]
        total_steps, max_agents, max_subpoints = AgentData._get_data_dimensions(data)
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
            times[t] = bundleData[t]["time"]
            frame_data = bundleData[t]["data"]
            n = 0
            i = 0
            while i + V1_SPATIAL_BUFFER_STRUCT.index("NSP") < len(frame_data):
                # a new agent should start at this index
                viz_types[t][n] = frame_data[
                    i + V1_SPATIAL_BUFFER_STRUCT.index("VIZ_TYPE")
                ]
                unique_ids[t][n] = frame_data[i + V1_SPATIAL_BUFFER_STRUCT.index("UID")]
                type_ids[t][n] = frame_data[i + V1_SPATIAL_BUFFER_STRUCT.index("TID")]
                positions[t][n] = [
                    frame_data[i + V1_SPATIAL_BUFFER_STRUCT.index("POSX")],
                    frame_data[i + V1_SPATIAL_BUFFER_STRUCT.index("POSY")],
                    frame_data[i + V1_SPATIAL_BUFFER_STRUCT.index("POSZ")],
                ]
                radii[t][n] = frame_data[i + V1_SPATIAL_BUFFER_STRUCT.index("R")]
                i += V1_SPATIAL_BUFFER_STRUCT.index("NSP")
                # get the subpoints
                if max_subpoints < 1:
                    i += int(
                        V1_SPATIAL_BUFFER_STRUCT.index("SP")
                        - V1_SPATIAL_BUFFER_STRUCT.index("NSP")
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
                        V1_SPATIAL_BUFFER_STRUCT.index("SP")
                        - V1_SPATIAL_BUFFER_STRUCT.index("NSP")
                    )
                )
                n += 1
            n_agents[t] = n
        # get type names
        type_mapping = data["trajectoryInfo"]["typeMapping"]
        types = []
        for t in range(total_steps):
            types.append([])
            for n in range(int(n_agents[t])):
                types[t].append(type_mapping[str(int(type_ids[t][n]))]["name"])
        return cls(
            times=times,
            n_agents=n_agents,
            viz_types=viz_types,
            unique_ids=unique_ids,
            types=types,
            positions=positions,
            radii=radii,
            n_subpoints=n_subpoints,
            subpoints=subpoints,
            draw_fiber_points=False,
            type_ids=type_ids,
        )
