#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import logging
from typing import Any, Dict, List

import numpy as np

from .agent_data import AgentData
from .unit_data import UnitData
from .meta_data import MetaData
from .display_data import DisplayData
from .model_meta_data import ModelMetaData
from .camera_data import CameraData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class TrajectoryData:
    meta_data: MetaData
    agent_data: AgentData
    time_units: UnitData
    spatial_units: UnitData
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        meta_data: MetaData,
        agent_data: AgentData,
        time_units: UnitData = None,
        spatial_units: UnitData = None,
        plots: List[Dict[str, Any]] = None,
    ):
        """
        This object holds simulation trajectory outputs
        and plot data

        Parameters
        ----------
        meta_data : MetaData
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        agent_data : AgentData
            An object containing data for each agent
            at each timestep
        time_units: UnitData (optional)
            multiplier and unit name for time values
            Default: 1.0 second
        spatial_units: UnitData (optional)
            multiplier and unit name for spatial values
            Default: 1.0 meter
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.meta_data = meta_data
        self.agent_data = agent_data
        self.time_units = time_units if time_units is not None else UnitData("s")
        self.spatial_units = (
            spatial_units if spatial_units is not None else UnitData("m")
        )
        self.plots = plots if plots is not None else []

    @classmethod
    def from_buffer_data(
        cls, buffer_data: Dict[str, Any], display_data: Dict[int, DisplayData] = None
    ):
        """
        Create TrajectoryData from a simularium JSON dict containing buffers
        """
        if display_data is None:
            display_data = {}
        return cls(
            meta_data=MetaData.from_dict(buffer_data["trajectoryInfo"]),
            agent_data=AgentData.from_buffer_data(buffer_data, display_data),
            time_units=UnitData.from_dict(
                buffer_data["trajectoryInfo"]["timeUnits"], default_mag=1.0
            ),
            spatial_units=UnitData.from_dict(
                buffer_data["trajectoryInfo"]["spatialUnits"], default_mag=1.0
            ),
            plots=buffer_data["plotData"]["data"],
        )

    def append_agents(self, new_agents: AgentData):
        """
        Concatenate the new AgentData with the current data,
        generate new unique IDs and type IDs as needed
        """
        # create appropriate length buffer with current agents
        current_dimensions = self.agent_data.get_dimensions()
        added_dimensions = new_agents.get_dimensions()
        new_dimensions = current_dimensions.add(added_dimensions, axis=1)
        result = self.agent_data.check_increase_buffer_size(
            new_dimensions.max_agents - 1, axis=1
        )
        # add new agents
        result.n_agents = np.add(result.n_agents, new_agents.n_agents)
        start_i = current_dimensions.max_agents
        end_i = start_i + added_dimensions.max_agents
        result.viz_types[:, start_i:end_i] = new_agents.viz_types[:]
        result.positions[:, start_i:end_i] = new_agents.positions[:]
        result.radii[:, start_i:end_i] = new_agents.radii[:]
        result.rotations[:, start_i:end_i] = new_agents.rotations[:]
        result.n_subpoints[:, start_i:end_i] = new_agents.n_subpoints[:]
        if len(new_agents.subpoints.shape) > 2:
            result.subpoints[:, start_i:end_i] = new_agents.subpoints[:]
        # generate new unique IDs and type IDs so they don't overlap
        used_uids = list(np.unique(self.agent_data.unique_ids))
        new_uids = {}
        for time_index in range(new_dimensions.total_steps):
            new_agent_index = self.agent_data.n_agents[time_index]
            n_a = int(new_agents.n_agents[time_index])
            for agent_index in range(n_a):
                raw_uid = new_agents.unique_ids[time_index][agent_index]
                if raw_uid not in new_uids:
                    uid = raw_uid
                    while uid in used_uids:
                        uid += 1
                    new_uids[raw_uid] = uid
                    used_uids.append(uid)
                result.unique_ids[time_index][new_agent_index] = new_uids[raw_uid]
                result.types[time_index].append(
                    new_agents.types[time_index][agent_index]
                )
                new_agent_index += 1
        self.agent_data = result

    def update_agent_data(
        self,
        times: np.ndarray = None,
        n_agents: np.ndarray = None,
        viz_types: np.ndarray = None,
        unique_ids: np.ndarray = None,
        types: List = None,
        positions: np.ndarray = None,
        radii: np.ndarray = None,
        rotations: np.ndarray = None,
        n_subpoints: np.ndarray = None,
        subpoints: np.ndarray = None,
        display_data: Dict[str, DisplayData] = None,
    ):
        """
        Update AgentData, overwriting original values with those
        provided as parameters. Parameters that are not provided
        will retain their previous value.
        """
        new_agent_data = AgentData(
            times=times if times is not None else self.agent_data.times,
            n_agents=(n_agents if n_agents is not None else self.agent_data.n_agents),
            viz_types=(
                viz_types if viz_types is not None else self.agent_data.viz_types
            ),
            unique_ids=(
                unique_ids if unique_ids is not None else self.agent_data.unique_ids
            ),
            types=types if types is not None else self.agent_data.types,
            positions=(
                positions if positions is not None else self.agent_data.positions
            ),
            radii=radii if radii is not None else self.agent_data.radii,
            rotations=(
                rotations if rotations is not None else self.agent_data.rotations
            ),
            n_subpoints=(
                n_subpoints if n_subpoints is not None else self.agent_data.n_subpoints
            ),
            subpoints=(
                subpoints if subpoints is not None else self.agent_data.subpoints
            ),
            display_data=(
                display_data
                if display_data is not None
                else self.agent_data.display_data
            ),
        )
        self.agent_data = new_agent_data

    def add_display_data(self, display_data: Dict[str, DisplayData]):
        """
        Add DisplayData objects to the current display_data dict,
        overwriting entries of the same agent type name, while
        preserving all other previous entries
        """
        self.agent_data.display_data.update(display_data)

    def update_meta_data(
        self,
        box_size: np.ndarray = None,
        camera_position: np.ndarray = None,
        camera_look_at_position: np.ndarray = None,
        camera_up_vector: np.ndarray = None,
        camera_fov_degrees: float = None,
        scale_factor: float = None,
        trajectory_title: str = None,
        title: str = None,
        version: str = None,
        authors: str = None,
        description: str = None,
        source_code_url: str = None,
        input_data_url: str = None,
        raw_output_data_url: str = None,
    ):
        """
        Update MetaData, overwriting original values with those
        provided as parameters. Parameters that are not provided
        will retain their previous value.
        """
        new_camera_defaults = CameraData(
            position=(
                camera_position
                if camera_position is not None
                else self.meta_data.camera_defaults.position
            ),
            look_at_position=(
                camera_look_at_position
                if camera_look_at_position is not None
                else self.meta_data.camera_defaults.look_at_position
            ),
            up_vector=(
                camera_up_vector
                if camera_up_vector is not None
                else self.meta_data.camera_defaults.up_vector
            ),
            fov_degrees=(
                camera_fov_degrees
                if camera_fov_degrees is not None
                else self.meta_data.camera_defaults.fov_degrees
            ),
        )
        new_model_metadata = ModelMetaData(
            title=(
                title if title is not None else self.meta_data.model_meta_data.title
            ),
            version=(
                version
                if version is not None
                else self.meta_data.model_meta_data.version
            ),
            authors=(
                authors
                if authors is not None
                else self.meta_data.model_meta_data.authors
            ),
            description=(
                description
                if description is not None
                else self.meta_data.model_meta_data.description
            ),
            source_code_url=(
                source_code_url
                if source_code_url is not None
                else self.meta_data.model_meta_data.source_code_url
            ),
            input_data_url=(
                input_data_url
                if input_data_url is not None
                else self.meta_data.model_meta_data.input_data_url
            ),
            raw_output_data_url=(
                raw_output_data_url
                if raw_output_data_url is not None
                else self.meta_data.model_meta_data.raw_output_data_url
            ),
        )
        new_metadata = MetaData(
            box_size=(box_size if box_size is not None else self.meta_data.box_size),
            camera_defaults=new_camera_defaults,
            scale_factor=(
                scale_factor
                if scale_factor is not None
                else self.meta_data.scale_factor
            ),
            trajectory_title=(
                trajectory_title
                if trajectory_title is not None
                else self.meta_data.trajectory_title
            ),
            model_meta_data=new_model_metadata,
        )
        self.meta_data = new_metadata

    def update_time_units(
        self,
        name: str = None,
        magnitude: float = None,
    ):
        """
        Update the time_units UnitData object, overwriting original
        values with those provided as parameters. Parameters that are
        not provided will retain their previous value.
        """
        new_time_units = UnitData(
            name=name if name is not None else self.time_units.name,
            magnitude=(
                magnitude if magnitude is not None else self.time_units.magnitude
            ),
        )
        self.time_units = new_time_units

    def update_spatial_units(
        self,
        name: str = None,
        magnitude: float = None,
    ):
        """
        Update the spatial_units UnitData object, overwriting original
        values with those provided as parameters. Parameters that are
        not provided will retain their previous value.
        """
        new_spatial_units = UnitData(
            name=name if name is not None else self.spatial_units.name,
            magnitude=(
                magnitude if magnitude is not None else self.spatial_units.magnitude
            ),
        )
        self.spatial_units = new_spatial_units

    def __deepcopy__(self, memo):
        result = type(self)(
            meta_data=copy.deepcopy(self.meta_data, memo),
            agent_data=copy.deepcopy(self.agent_data, memo),
            time_units=copy.copy(self.time_units),
            spatial_units=copy.copy(self.spatial_units),
            plots=copy.deepcopy(self.plots, memo),
        )
        return result

    def __eq__(self, other):
        if isinstance(other, TrajectoryData):
            return (
                self.meta_data == other.meta_data
                and self.agent_data == other.agent_data
                and self.time_units == other.time_units
                and self.spatial_units == other.spatial_units
                and self.plots == other.plots
            )
