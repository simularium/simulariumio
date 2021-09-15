#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import copy
import logging
from typing import List, Tuple, Dict, Any
import math

import numpy as np
import pandas as pd

from ..constants import (
    V1_SPATIAL_BUFFER_STRUCT,
    VIZ_TYPE,
    BUFFER_SIZE_INC,
)
from .dimension_data import DimensionData
from .display_data import DisplayData

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
    n_subpoints: np.ndarray
    subpoints: np.ndarray
    display_data: Dict[str, DisplayData]
    draw_fiber_points: bool

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
        display_data: Dict[str, DisplayData] = None,
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
        display_data: Dict[str,DisplayData] (optional)
            A dictionary mapping agent type name to DisplayData
            to use for that type
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
        self.subpoints = subpoints if subpoints is not None else np.zeros((3, 3, 0, 3))
        self.display_data = display_data if display_data is not None else {}
        self.draw_fiber_points = draw_fiber_points
        self.n_timesteps = n_timesteps

    @staticmethod
    def _get_buffer_data_dimensions(buffer_data: Dict[str, Any]) -> DimensionData:
        """
        Get dimensions of a simularium JSON dict containing buffers
        """
        bundle_data = buffer_data["spatialData"]["bundleData"]
        result = DimensionData(total_steps=len(bundle_data), max_agents=0)
        for time_index in range(result.total_steps):
            # buffer = packed agent data as a list of numbers
            buffer = bundle_data[time_index]["data"]
            buffer_index = 0
            agents = 0
            while buffer_index < len(buffer):
                # a new agent should start at this index
                agents += 1
                buffer_index += V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                # get the number of subpoints
                subpoints = math.floor(buffer[buffer_index] / 3.0)
                if subpoints > result.max_subpoints:
                    result.max_subpoints = subpoints
                buffer_index += int(
                    buffer[buffer_index]
                    + (
                        V1_SPATIAL_BUFFER_STRUCT.VALUES_PER_AGENT
                        - V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                        - 1
                    )
                )
            if agents > result.max_agents:
                result.max_agents = agents
        return result

    def get_type_ids_and_mapping(self) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Generate a type_ids array from the type_names list
        """
        total_steps = len(self.types)
        max_agents = 0
        for time_index in range(len(self.types)):
            agent_index = len(self.types[time_index])
            if agent_index > max_agents:
                max_agents = agent_index
        type_ids = np.zeros((len(self.types), max_agents))
        type_name_mapping = {}
        type_id_mapping = {}
        last_tid = 0
        for time_index in range(total_steps):
            for agent_index in range(len(self.types[time_index])):
                tn = self.types[time_index][agent_index]
                if len(tn) == 0:
                    continue
                if tn not in type_id_mapping:
                    tid = last_tid
                    last_tid += 1
                    type_id_mapping[tn] = tid
                    type_name_mapping[str(tid)] = {"name": tn}
                    if (
                        tn in self.display_data
                        and not self.display_data[tn].is_default()
                    ):
                        type_name_mapping[str(tid)]["geometry"] = dict(
                            self.display_data[tn]
                        )
                type_ids[time_index][agent_index] = type_id_mapping[tn]
        return type_ids, type_name_mapping

    @staticmethod
    def get_type_names(
        type_ids: np.ndarray, type_mapping: Dict[str, Any]
    ) -> List[List[str]]:
        """
        Generate the type_names list from a type_ids array and a type_mapping
        """
        result = []
        for time_index in range(type_ids.shape[0]):
            result.append([])
            for agent_index in range(int(len(type_ids[time_index]))):
                result[time_index].append(
                    type_mapping[str(int(type_ids[time_index][agent_index]))]["name"]
                )
        return result

    @staticmethod
    def get_display_data(type_mapping: Dict[str, Any]) -> Dict[str, DisplayData]:
        """
        Generate the display_data mapping using a type_mapping
        from a simularium JSON dict containing buffers
        """
        result = {}
        for type_id in type_mapping:
            type_info = type_mapping[type_id]
            if "geometry" not in type_info:
                continue
            result[type_info["name"]] = DisplayData(
                display_type=type_info["geometry"]["displayType"],
                url=type_info["geometry"]["url"]
                if "url" in type_info["geometry"]
                else None,
                color=type_info["geometry"]["color"]
                if "color" in type_info["geometry"]
                else None,
            )
        return result

    @classmethod
    def from_buffer_data(cls, buffer_data: Dict[str, Any]):
        """
        Create AgentData from a simularium JSON dict containing buffers
        """
        bundle_data = buffer_data["spatialData"]["bundleData"]
        dimensions = AgentData._get_buffer_data_dimensions(buffer_data)
        print(f"original dim = {dimensions.to_string()}")
        agent_data = AgentData.from_dimensions(dimensions)
        type_ids = np.zeros((dimensions.total_steps, dimensions.max_agents))
        for time_index in range(dimensions.total_steps):
            agent_data.times[time_index] = bundle_data[time_index]["time"]
            frame_data = bundle_data[time_index]["data"]
            agent_index = 0
            buffer_index = 0
            while buffer_index + V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX < len(frame_data):
                # a new agent should start at this index
                agent_data.viz_types[time_index][agent_index] = frame_data[
                    buffer_index + V1_SPATIAL_BUFFER_STRUCT.VIZ_TYPE_INDEX
                ]
                agent_data.unique_ids[time_index][agent_index] = frame_data[
                    buffer_index + V1_SPATIAL_BUFFER_STRUCT.UID_INDEX
                ]
                type_ids[time_index][agent_index] = frame_data[
                    buffer_index + V1_SPATIAL_BUFFER_STRUCT.TID_INDEX
                ]
                agent_data.positions[time_index][agent_index] = [
                    frame_data[buffer_index + V1_SPATIAL_BUFFER_STRUCT.POSX_INDEX],
                    frame_data[buffer_index + V1_SPATIAL_BUFFER_STRUCT.POSY_INDEX],
                    frame_data[buffer_index + V1_SPATIAL_BUFFER_STRUCT.POSZ_INDEX],
                ]
                agent_data.rotations[time_index][agent_index] = [
                    frame_data[buffer_index + V1_SPATIAL_BUFFER_STRUCT.ROTX_INDEX],
                    frame_data[buffer_index + V1_SPATIAL_BUFFER_STRUCT.ROTY_INDEX],
                    frame_data[buffer_index + V1_SPATIAL_BUFFER_STRUCT.ROTZ_INDEX],
                ]
                agent_data.radii[time_index][agent_index] = frame_data[
                    buffer_index + V1_SPATIAL_BUFFER_STRUCT.R_INDEX
                ]
                buffer_index += V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                # get the subpoints
                if dimensions.max_subpoints < 1:
                    buffer_index += int(
                        V1_SPATIAL_BUFFER_STRUCT.SP_INDEX
                        - V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                    )
                    agent_index += 1
                    continue
                agent_data.n_subpoints[time_index][agent_index] = int(
                    frame_data[buffer_index] / 3.0
                )
                subpoint_index = 0
                dim = 0
                for i in range(int(frame_data[buffer_index])):
                    agent_data.subpoints[time_index][agent_index][subpoint_index][
                        dim
                    ] = frame_data[buffer_index + 1 + i]
                    dim += 1
                    if dim > 2:
                        dim = 0
                        subpoint_index += 1
                buffer_index += int(
                    frame_data[buffer_index]
                    + (
                        V1_SPATIAL_BUFFER_STRUCT.SP_INDEX
                        - V1_SPATIAL_BUFFER_STRUCT.NSP_INDEX
                    )
                )
                agent_index += 1
            agent_data.n_agents[time_index] = agent_index
        type_names = AgentData.get_type_names(
            type_ids, buffer_data["trajectoryInfo"]["typeMapping"]
        )
        display_data = AgentData.get_display_data(
            buffer_data["trajectoryInfo"]["typeMapping"]
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
            display_data=display_data,
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
            max_subpoints=self.subpoints.shape[2]
            if len(self.subpoints.shape) > 2
            else 0,
        )

    def get_copy_with_increased_buffer_size(
        self, added_dimensions: DimensionData, axis: int = 1
    ) -> AgentData:
        """
        Create a copy of this object with the size of the numpy arrays increased
        by the given added_dimensions
        """
        print(f"increase buffer {axis}")
        current_dimensions = self.get_dimensions()
        # raise Exception(added_dimensions.to_string())
        new_dimensions = added_dimensions.add(current_dimensions, axis)
        current_types = copy.deepcopy(self.types)
        result = AgentData.from_dimensions(new_dimensions)
        result.times[0 : current_dimensions.total_steps] = self.times[:]
        result.n_agents[0 : current_dimensions.total_steps] = self.n_agents[:]
        result.viz_types[
            0 : current_dimensions.total_steps, 0 : current_dimensions.max_agents
        ] = self.viz_types[:]
        result.unique_ids[
            0 : current_dimensions.total_steps, 0 : current_dimensions.max_agents
        ] = self.unique_ids[:]
        for time_index in range(current_dimensions.total_steps):
            n_a = int(self.n_agents[time_index])
            for agent_index in range(n_a):
                result.types[time_index].append(current_types[time_index][agent_index])
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
        if self.subpoints.shape[2] > 0:
            result.subpoints[
                0 : current_dimensions.total_steps,
                0 : current_dimensions.max_agents,
                0 : current_dimensions.max_subpoints,
            ] = self.subpoints[:]
        result.display_data = copy.deepcopy(self.display_data)
        result.draw_fiber_points = self.draw_fiber_points
        return result

    def check_increase_buffer_size(
        self,
        next_index: int,
        axis: int = 1,
        buffer_size_inc: DimensionData = BUFFER_SIZE_INC,
    ) -> AgentData:
        """
        If needed for the next_index to fit in the arrays, create a copy of this object
        with the size of the numpy arrays increased by the buffer_size_inc
        """
        result = self
        if axis == 0:  # time dimension
            while next_index >= result.get_dimensions().total_steps:
                result = result.get_copy_with_increased_buffer_size(
                    DimensionData(
                        total_steps=buffer_size_inc.total_steps,
                        max_agents=0,
                    ),
                    axis,
                )
        elif axis == 1:  # agents dimension
            while next_index >= result.get_dimensions().max_agents:
                result = result.get_copy_with_increased_buffer_size(
                    DimensionData(
                        total_steps=0,
                        max_agents=buffer_size_inc.max_agents,
                    ),
                    axis,
                )
        elif axis == 2:  # subpoints dimension
            while next_index >= result.get_dimensions().max_subpoints:
                result = result.get_copy_with_increased_buffer_size(
                    DimensionData(
                        total_steps=0,
                        max_agents=0,
                        max_subpoints=buffer_size_inc.max_subpoints,
                    ),
                    axis,
                )
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
            display_data=copy.deepcopy(self.display_data, memo),
            draw_fiber_points=self.draw_fiber_points,
        )
        return result

    def __eq__(self, other):
        return (
            self.n_timesteps == other.n_timesteps
            and False not in np.isclose(self.times, other.times)
            and False not in np.isclose(self.n_agents, other.n_agents)
            and False not in np.isclose(self.viz_types, other.viz_types)
            and False not in np.isclose(self.unique_ids, other.unique_ids)
            and self.types == other.types
            and False not in np.isclose(self.positions, other.positions)
            and False not in np.isclose(self.radii, other.radii)
            and False not in np.isclose(self.rotations, other.rotations)
            and False not in np.isclose(self.n_subpoints, other.n_subpoints)
            and False not in np.isclose(self.subpoints, other.subpoints)
            and self.display_data == other.display_data
            and self.draw_fiber_points == other.draw_fiber_points
        )
