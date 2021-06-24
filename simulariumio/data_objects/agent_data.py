#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import logging
from typing import List, Tuple, Dict, Any
import math

import numpy as np
import pandas as pd

from ..constants import V1_SPATIAL_BUFFER_STRUCT, VIZ_TYPE, BUFFER_SIZE_INC
from .dimension_data import DimensionData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class AgentData:
    n_timesteps: int
    times: np.ndarray
    n_agents: np.ndarray
    viz_types: np.ndarray
    unique_ids: np.ndarray
    types: List[List[str]]
    positions: np.ndarray
    radii: np.ndarray
    rotations: np.ndarray
    n_subpoints: np.ndarray = None
    subpoints: np.ndarray = None
    draw_fiber_points: bool = False

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
        n_timesteps: int = -1,
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
        rotations : np.ndarray (shape = [timesteps, agents, 3]) (optional)
            A numpy ndarray containing the XYZ euler angles representing
            the rotation for each agent at each timestep in degrees
            Default: [0, 0, 0] for each agent
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
        n_timesteps : int (optional)
            Use the first n_timesteps frames of data
            Default: -1 (use the full length of the buffer)
        """
        self.times = times
        self.n_agents = n_agents
        self.viz_types = viz_types
        self.unique_ids = unique_ids
        self.types = types
        self.positions = positions
        self.radii = radii
        self.rotations = (
            rotations if rotations is not None else np.zeros_like(positions)
        )
        self.n_subpoints = (
            n_subpoints if n_subpoints is not None else np.zeros_like(radii)
        )
        self.subpoints = subpoints if subpoints is not None else np.zeros_like(radii)
        self.draw_fiber_points = draw_fiber_points
        self.n_timesteps = n_timesteps

    @staticmethod
    def _get_buffer_data_dimensions(buffer_data: Dict[str, Any]) -> DimensionData:
        """
        Get dimensions of a simularium JSON dict containing buffers
        """
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
        return DimensionData(
            total_steps=total_steps,
            max_n_agents=max_n_agents,
            max_n_subpoints=max_n_subpoints,
        )

    @classmethod
    def from_buffer_data(cls, buffer_data: Dict[str, Any]):
        """
        Create AgentData from a simularium JSON dict containing buffers
        """
        bundle_data = buffer_data["spatialData"]["bundleData"]
        dimensions = AgentData._get_buffer_data_dimensions(buffer_data)
        print(
            f"original dim = {dimensions.total_steps} timesteps X "
            f"{dimensions.max_agents} agents X {dimensions.max_subpoints} subpoints"
        )
        agent_data = AgentData.from_dimensions(dimensions)
        type_ids = np.zeros((dimensions.total_steps, dimensions.max_agents))
        for t in range(dimensions.total_steps):
            agent_data.times[t] = bundle_data[t]["time"]
            frame_data = bundle_data[t]["data"]
            n = 0
            i = 0
            while i + V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX < len(frame_data):
                # a new agent should start at this index
                agent_data.viz_types[t][n] = frame_data[
                    i + V1_SPATIAL_BUFFER_STRUCT.VIZ_TYPE_INDEX
                ]
                agent_data.unique_ids[t][n] = frame_data[
                    i + V1_SPATIAL_BUFFER_STRUCT.UID_INDEX
                ]
                type_ids[t][n] = frame_data[i + V1_SPATIAL_BUFFER_STRUCT.TID_INDEX]
                agent_data.positions[t][n] = [
                    frame_data[i + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX],
                    frame_data[i + V1_SPATIAL_BUFFER_STRUCT.POSY_INDEX],
                    frame_data[i + V1_SPATIAL_BUFFER_STRUCT.POSZ_INDEX],
                ]
                agent_data.rotations[t][n] = [
                    frame_data[i + V1_SPATIAL_BUFFER_STRUCT.ROTX_INDEX],
                    frame_data[i + V1_SPATIAL_BUFFER_STRUCT.ROTY_INDEX],
                    frame_data[i + V1_SPATIAL_BUFFER_STRUCT.ROTZ_INDEX],
                ]
                agent_data.radii[t][n] = frame_data[
                    i + V1_SPATIAL_BUFFER_STRUCT.R_INDEX
                ]
                i += V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                # get the subpoints
                if dimensions.max_subpoints < 1:
                    i += int(
                        V1_SPATIAL_BUFFER_STRUCT.SP_INDEX
                        - V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                    )
                    n += 1
                    continue
                agent_data.n_subpoints[t][n] = int(frame_data[i] / 3.0)
                p = 0
                d = 0
                for j in range(int(frame_data[i])):
                    agent_data.subpoints[t][n][p][d] = frame_data[i + 1 + j]
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
            agent_data.n_agents[t] = n
        type_names = AgentData.get_type_names(
            type_ids, buffer_data["trajectoryInfo"]["typeMapping"]
        )
        return cls(
            times=agent_data.times,
            n_agents=agent_data.n_agents,
            viz_types=agent_data.viz_types,
            unique_ids=agent_data.unique_ids,
            types=type_names,
            positions=agent_data.positions,
            radii=agent_data.radii,
            rotations=agent_data.rotations,
            n_subpoints=agent_data.n_subpoints,
            subpoints=agent_data.subpoints,
            draw_fiber_points=False,
        )

    @classmethod
    def from_dataframe(cls, traj: pd.DataFrame):
        """
        Create AgentData from a pandas DataFrame with columns:
        time, unique_id, type, positionX, positionY, positionZ, radius
        (only for default agents, no fibers)
        """
        times = np.unique(traj.loc[0, "time"].to_numpy())
        n_agents = np.squeeze(
            traj.groupby("time").agg(["count"])["unique_id"].to_numpy()
        )
        grouped_traj = (
            traj.set_index(["time", traj.groupby("time").cumcount()])
            .unstack(fill_value=0)
            .stack()
        )
        unique_ids = np.array(
            grouped_traj["unique_id"]
            .groupby(level=0)
            .apply(lambda x: x.values.tolist())
            .tolist()
        )
        positions = np.array(
            grouped_traj[["positionX", "positionY", "positionZ"]]
            .groupby(level=0)
            .apply(lambda x: x.values.tolist())
            .tolist()
        )
        rotations = np.array(
            grouped_traj[["rotationX", "rotationY", "rotationZ"]]
            .groupby(level=0)
            .apply(lambda x: x.values.tolist())
            .tolist()
        )
        radii = np.array(
            grouped_traj["radius"]
            .groupby(level=0)
            .apply(lambda x: x.values.tolist())
            .tolist()
        )
        grouped_traj = (
            traj.set_index(["time", traj.groupby("time").cumcount()])
            .unstack(fill_value="")
            .stack()
        )
        type_names = (
            grouped_traj["type"]
            .groupby(level=0)
            .apply(lambda x: x.values.tolist())
            .tolist()
        )
        return cls(
            times=times,
            n_agents=n_agents,
            viz_types=VIZ_TYPE.DEFAULT * np.ones_like(unique_ids),
            unique_ids=unique_ids,
            types=type_names,
            positions=positions,
            radii=radii,
            rotations=rotations,
        )

    @classmethod
    def from_dimensions(
        cls, dimensions: DimensionData, default_viz_type: float = VIZ_TYPE.DEFAULT
    ):
        """
        Create AgentData with empty numpy arrays of the required dimensions
        """
        return cls(
            times=np.zeros(dimensions.total_steps),
            n_agents=np.zeros(dimensions.total_steps),
            viz_types=default_viz_type
            * np.ones((dimensions.total_steps, dimensions.max_agents)),
            unique_ids=np.zeros((dimensions.total_steps, dimensions.max_agents)),
            types=[[] for t in range(dimensions.total_steps)],
            positions=np.zeros((dimensions.total_steps, dimensions.max_agents, 3)),
            radii=np.ones((dimensions.total_steps, dimensions.max_agents)),
            rotations=np.zeros((dimensions.total_steps, dimensions.max_agents, 3)),
            n_subpoints=np.zeros((dimensions.total_steps, dimensions.max_agents)),
            subpoints=np.zeros(
                (
                    dimensions.total_steps,
                    dimensions.max_agents,
                    dimensions.max_subpoints,
                    3,
                )
            ),
        )

    def get_dimensions(self) -> DimensionData:
        """
        Get the dimensions of this object's numpy arrays
        """
        return DimensionData(
            total_steps=self.times.shape[0],
            max_agents=self.viz_types.shape[1],
            max_subpoints=self.subpoints.shape[2],
        )

    def increase_buffer_size(
        self, added_dimensions: DimensionData, axis: int = 1
    ) -> AgentData:
        """
        Increase the size of this object's numpy arrays by the given dimensions
        """
        current_dimensions = self.get_dimensions()
        new_dimensions = current_dimensions.add(added_dimensions, axis)
        result = AgentData.from_dimensions(new_dimensions)
        result.n_agents = self.n_agents
        result.viz_types[
            0 : current_dimensions.total_steps, 0 : current_dimensions.max_agents
        ] = self.viz_types[:]
        result.unique_ids[
            0 : current_dimensions.total_steps, 0 : current_dimensions.max_agents
        ] = self.unique_ids[:]
        for t in range(current_dimensions.total_steps):
            n_a = int(self.n_agents[t])
            for n in range(n_a):
                result.types[t].append(self.types[t][n])
        result.positions[
            0 : current_dimensions.total_steps, 0 : current_dimensions.max_agents
        ] = self.positions[:]
        result.radii[
            0 : current_dimensions.total_steps, 0 : current_dimensions.max_agents
        ] = self.radii[:]
        result.rotations[
            0 : current_dimensions.total_steps, 0 : current_dimensions.max_agents
        ] = self.rotations[:]
        result.n_subpoints[
            0 : current_dimensions.total_steps, 0 : current_dimensions.max_agents
        ] = self.n_subpoints[:]
        result.subpoints[
            0 : current_dimensions.total_steps, 0 : current_dimensions.max_agents
        ] = self.subpoints[:]
        result.draw_fiber_points = self.draw_fiber_points
        return result

    def check_increase_buffer_size(self, next_index: int, axis: int = 1) -> AgentData:
        """
        Increase the size of this object's numpy arrays as much as needed
        """
        result = self
        if axis == 0:  # time dimension
            while next_index >= result.get_dimensions().total_steps:
                result = result.increase_buffer_size(
                    DimensionData(
                        total_steps=BUFFER_SIZE_INC.TIMESTEPS,
                        max_agents=0,
                    )
                )
        elif axis == 1:  # agents dimension
            while next_index >= result.get_dimensions().max_agents:
                result = result.increase_buffer_size(
                    DimensionData(
                        total_steps=0,
                        max_agents=BUFFER_SIZE_INC.AGENTS,
                    )
                )
        elif axis == 2:  # subpoints dimension
            while next_index >= result.get_dimensions().max_subpoints:
                result = result.increase_buffer_size(
                    DimensionData(
                        total_steps=0,
                        max_agents=0,
                        max_subpoints=BUFFER_SIZE_INC.SUBPOINTS,
                    )
                )
        return result

    def append_agents(self, new_agents: AgentData) -> AgentData:
        """
        Concatenate the new AgentData with the current data,
        generate new unique IDs and type IDs as needed
        """
        # create appropriate length buffer with current agents
        current_dimensions = self.get_dimensions()
        added_dimensions = new_agents.get_dimensions()
        new_dimensions = current_dimensions.add(added_dimensions, axis=0)
        result = self.increase_buffer_size(added_dimensions)
        # add new agents
        result.n_agents = np.add(result.n_agents, new_agents.n_agents)
        result.viz_types[:, current_dimensions.max_agents :] = new_agents.viz_types[:]
        result.positions[:, current_dimensions.max_agents :] = new_agents.positions[:]
        result.radii[:, current_dimensions.max_agents :] = new_agents.radii[:]
        result.rotations[:, current_dimensions.max_agents :] = new_agents.rotations[:]
        result.n_subpoints[:, current_dimensions.max_agents :] = new_agents.n_subpoints[
            :
        ]
        result.subpoints[:, current_dimensions.max_agents :] = new_agents.subpoints[:]
        # generate new unique IDs and type IDs so they don't overlap
        used_uids = list(np.unique(self.unique_ids))
        new_uids = {}
        for t in range(new_dimensions.total_steps):
            i = self.n_agents[t] - 1
            n_a = int(new_agents.n_agents[t])
            for n in range(n_a):
                raw_uid = new_agents.unique_ids[t][n]
                if raw_uid not in new_uids:
                    uid = raw_uid
                    while uid in used_uids:
                        uid += 1
                    new_uids[raw_uid] = uid
                    used_uids.append(uid)
                result.unique_ids[t][i] = new_uids[raw_uid]
                result.types[t].append(new_agents.types[t][n])
                i += 1
        return result

    def get_type_ids_and_mapping(self) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Generate a type_ids array from the type_names list
        """
        total_steps = len(self.types)
        max_agents = 0
        for t in range(len(self.types)):
            n = len(self.types[t])
            if n > max_agents:
                max_agents = n
        type_ids = np.zeros((len(self.types), max_agents))
        type_name_mapping = {}
        type_id_mapping = {}
        last_tid = 0
        for t in range(total_steps):
            for n in range(len(self.types[t])):
                tn = self.types[t][n]
                if len(tn) == 0:
                    continue
                if tn not in type_id_mapping:
                    tid = last_tid
                    last_tid += 1
                    type_id_mapping[tn] = tid
                    type_name_mapping[str(tid)] = {"name": tn}
                type_ids[t][n] = type_id_mapping[tn]
        return type_ids, type_name_mapping

    @staticmethod
    def get_type_names(
        type_ids: np.ndarray, type_mapping: Dict[str, Any]
    ) -> List[List[str]]:
        """
        Generate the type_names list from a type_ids array and a type_mapping
        """
        result = []
        for t in range(type_ids.shape[0]):
            result.append([])
            for n in range(int(len(type_ids[t]))):
                result[t].append(type_mapping[str(int(type_ids[t][n]))]["name"])
        return result

    def __deepcopy__(self, memo):
        result = type(self)(
            times=np.copy(self.times),
            n_agents=np.copy(self.n_agents),
            viz_types=np.copy(self.viz_types),
            unique_ids=np.copy(self.unique_ids),
            types=copy.deepcopy(self.types, memo),
            positions=np.copy(self.positions),
            radii=np.copy(self.radii),
            rotations=np.copy(self.rotations),
            n_subpoints=np.copy(self.n_subpoints),
            subpoints=np.copy(self.subpoints),
            draw_fiber_points=self.draw_fiber_points,
        )
        return result
