#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from simulariumio.data_objects.dimension_data import DimensionData
from typing import Dict, Tuple, List
from pathlib import Path

import numpy as np
import pandas as pd
from .dep.pyMCDS import pyMCDS

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, UnitData, DisplayData
from ..exceptions import MissingDataError, DataError
from ..constants import (
    DISPLAY_TYPE,
    SUBPOINT_VALUES_PER_ITEM,
    DEFAULT_COLORS,
    VALUES_PER_3D_POINT,
)
from .physicell_data import PhysicellData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class PhysicellConverter(TrajectoryConverter):
    def __init__(self, input_data: PhysicellData):
        """
        This object reads simulation trajectory outputs
        from PhysiCell (http://physicell.org/)
        and plot data and writes them in the JSON format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : PhysicellData
            An object containing info for reading
            PhysiCell simulation trajectory outputs and plot data
        """
        self._data = self._read(input_data)

    @staticmethod
    def _load_data(
        path_to_output_dir: str, nth_timestep_to_read: int
    ) -> Tuple[List[pd.DataFrame], str]:
        """
        Load simulation data from PhysiCell MultiCellDS XML files
        """
        files = Path(path_to_output_dir).glob("*output*.xml")
        file_mapping = {}
        for f in files:
            index = int(f.name[f.name.index("output") + 6 :].split(".")[0])
            if index % nth_timestep_to_read == 0:
                file_mapping[index] = f
        data = []
        for t, xml_file in sorted(file_mapping.items()):
            data.append(pyMCDS(xml_file.name, False, path_to_output_dir))
        physicell_data = np.array(data)
        total_steps = len(physicell_data)
        discrete_cells = []
        for time_index in range(total_steps):
            discrete_cells.append(physicell_data[time_index].get_cell_df())
        spatial_units = physicell_data[0].data["metadata"]["spatial_units"]
        return discrete_cells, spatial_units

    @staticmethod
    def _get_default_cell_name(cell_type: int) -> str:
        return f"cell{cell_type}"

    @staticmethod
    def _get_default_phase_name(cell_phase: int) -> str:
        return f"#phase{cell_phase}"

    @staticmethod
    def _get_agent_type(
        cell_type_id: int,
        cell_phase_id: int,
        input_data: PhysicellData,
        type_ids: Dict[int, Dict[int, int]],
        last_id: int,
        type_mapping: Dict[int, str],
    ) -> Tuple[int, Dict[int, Dict[int, int]], int, Dict[int, str]]:
        """
        Get a unique agent type ID for a specific cell type and phase combination
        """
        if cell_type_id not in type_ids:
            type_ids[cell_type_id] = {}
        if cell_phase_id not in type_ids[cell_type_id]:
            type_ids[cell_type_id][cell_phase_id] = last_id
            type_name = ""
            if cell_type_id in input_data.display_data:
                type_name = input_data.display_data[cell_type_id].name
            else:
                type_name = PhysicellConverter._get_default_cell_name(cell_type_id)
            if (
                cell_type_id in input_data.phase_names
                and cell_phase_id in input_data.phase_names[cell_type_id]
            ):
                type_name += "#" + input_data.phase_names[cell_type_id][cell_phase_id]
            else:
                type_name += PhysicellConverter._get_default_phase_name(cell_phase_id)
            type_mapping[last_id] = type_name
            last_id += 1
        return type_ids[cell_type_id][cell_phase_id], type_ids, last_id, type_mapping

    @staticmethod
    def _radius_for_volume(total_volume: float) -> float:
        return np.cbrt(3.0 / 4.0 * total_volume / np.pi)

    @staticmethod
    def _get_dimensions(discrete_cells: List[pd.DataFrame]) -> DimensionData:
        """
        Get dimensions of the PhysiCell data
        """
        total_steps = len(discrete_cells)
        max_agents = 0
        for time_index in range(total_steps):
            n_cells = len(discrete_cells[time_index]["position_x"])
            if n_cells > max_agents:
                max_agents = n_cells
        if total_steps < 1 or max_agents < 1:
            raise MissingDataError(
                "no timesteps or no agents found in PhysiCell data, "
                "is the path_to_output_dir pointing to an output directory?"
            )
        return DimensionData(
            total_steps=total_steps,
            max_agents=max_agents,
        )

    @staticmethod
    def _cell_is_subcell(cell_type_id: int, input_data: PhysicellData) -> bool:
        return (
            input_data.max_owner_cells >= 0
            and cell_type_id >= input_data.max_owner_cells
        )

    @staticmethod
    def _display_owner_number(owner_id: int, input_data: PhysicellData) -> bool:
        result = owner_id
        max_owners = input_data.max_owner_cells
        while result - max_owners > 0:
            result -= max_owners
        return result

    @staticmethod
    def _get_trajectory_data(
        input_data: PhysicellData,
    ) -> Tuple[AgentData, UnitData, Dict[int, Dict[int, int]]]:
        """
        Get data in Simularium format
        """
        type_ids = {}
        last_id = 0
        type_mapping = {}
        discrete_cells, units = PhysicellConverter._load_data(
            input_data.path_to_output_dir, input_data.nth_timestep_to_read
        )
        dimensions = PhysicellConverter._get_dimensions(discrete_cells)
        result = AgentData.from_dimensions(dimensions)
        result.times = (
            input_data.nth_timestep_to_read
            * input_data.timestep
            * np.arange(dimensions.total_steps)
        )
        # get data
        max_subpoints = 0
        values_per_subcell = SUBPOINT_VALUES_PER_ITEM(DISPLAY_TYPE.SPHERE_GROUP)
        n_def_agents = []
        subcells = []
        for time_index in range(dimensions.total_steps):
            n_cells = int(len(discrete_cells[time_index]["position_x"]))
            n_def_agents.append(0)
            subcells.append({})
            for cell_index in range(n_cells):
                cell_type_id = int(discrete_cells[time_index]["cell_type"][cell_index])
                if PhysicellConverter._cell_is_subcell(cell_type_id, input_data):
                    # this is a subcell
                    if cell_type_id not in subcells[time_index]:
                        subcells[time_index][cell_type_id] = []
                    subcells[time_index][cell_type_id].append(cell_index)
                    continue
                # otherwise display as a default agent
                result.unique_ids[time_index][n_def_agents[time_index]] = cell_index
                cell_phase = int(
                    discrete_cells[time_index]["current_phase"][cell_index]
                )
                (
                    tid,
                    type_ids,
                    last_id,
                    type_mapping,
                ) = PhysicellConverter._get_agent_type(
                    cell_type_id=cell_type_id,
                    cell_phase_id=cell_phase,
                    input_data=input_data,
                    type_ids=type_ids,
                    last_id=last_id,
                    type_mapping=type_mapping,
                )
                if type_mapping[tid] not in input_data.display_data:
                    result.display_data[type_mapping[tid]] = DisplayData(
                        name=type_mapping[tid],
                        display_type=DISPLAY_TYPE.SPHERE,
                    )
                result.types[time_index].append(type_mapping[tid])
                result.positions[time_index][
                    n_def_agents[time_index]
                ] = input_data.meta_data.scale_factor * np.array(
                    [
                        discrete_cells[time_index]["position_x"][cell_index],
                        discrete_cells[time_index]["position_y"][cell_index],
                        discrete_cells[time_index]["position_z"][cell_index],
                    ]
                )
                result.radii[time_index][
                    n_def_agents[time_index]
                ] = input_data.meta_data.scale_factor * (
                    input_data.display_data[cell_type_id].radius
                    if cell_type_id in input_data.display_data
                    and input_data.display_data[cell_type_id].radius is not None
                    else PhysicellConverter._radius_for_volume(
                        discrete_cells[time_index]["total_volume"][cell_index]
                    )
                )
                n_def_agents[time_index] += 1
            # update max_subpoints
            for owner_id in subcells[time_index]:
                n_subcells = len(subcells[time_index][owner_id])
                if n_subcells * values_per_subcell > max_subpoints:
                    max_subpoints = n_subcells * values_per_subcell
        # create sphere group agents for owner cells and subcells
        result.subpoints = np.zeros(
            (
                dimensions.total_steps,
                dimensions.max_agents,
                max_subpoints,
            )
        )
        owner_cell_color_indices = {}
        next_color_index = 0
        for time_index in range(dimensions.total_steps):
            agent_index = n_def_agents[time_index]
            for owner_id in subcells[time_index]:
                if owner_id not in owner_cell_color_indices:
                    owner_cell_color_indices[owner_id] = next_color_index
                    next_color_index += 1
                    if next_color_index >= len(DEFAULT_COLORS):
                        next_color_index = 0
                result.unique_ids[time_index][agent_index] = owner_id
                owner_number = PhysicellConverter._display_owner_number(
                    owner_id, input_data
                )
                type_name = f"{input_data.owner_cell_display_name}#{owner_number}"
                result.types[time_index].append(type_name)
                type_ids[owner_id] = {}
                input_data.display_data[owner_id] = DisplayData(
                    name=type_name,
                    display_type=DISPLAY_TYPE.SPHERE_GROUP,
                    color=DEFAULT_COLORS[owner_cell_color_indices[owner_id]],
                )
                n_subcells = len(subcells[time_index][owner_id])
                result.n_subpoints[time_index][agent_index] = (
                    values_per_subcell * n_subcells
                )
                # position
                subcell_positions = []
                for subcell_index in range(n_subcells):
                    cell_index = subcells[time_index][owner_id][subcell_index]
                    subcell_positions.append(
                        input_data.meta_data.scale_factor
                        * np.array(
                            [
                                discrete_cells[time_index]["position_x"][cell_index],
                                discrete_cells[time_index]["position_y"][cell_index],
                                discrete_cells[time_index]["position_z"][cell_index],
                            ]
                        )
                    )
                center = np.mean(np.array(subcell_positions), axis=0)
                result.positions[time_index][agent_index] = center
                # subpoints
                for subcell_index in range(n_subcells):
                    cell_index = subcells[time_index][owner_id][subcell_index]
                    sp_index = values_per_subcell * subcell_index
                    result.subpoints[time_index][agent_index][
                        sp_index : sp_index + VALUES_PER_3D_POINT
                    ] = (subcell_positions[subcell_index] - center)
                    result.subpoints[time_index][agent_index][
                        sp_index + VALUES_PER_3D_POINT
                    ] = (
                        input_data.meta_data.scale_factor
                        * PhysicellConverter._radius_for_volume(
                            discrete_cells[time_index]["total_volume"][cell_index]
                        )
                    )
                agent_index += 1
            result.n_agents[time_index] = agent_index
        spatial_units = UnitData(
            units,
            1.0 / input_data.meta_data.scale_factor,
        )
        result.n_timesteps = dimensions.total_steps
        return result, spatial_units, type_ids

    @staticmethod
    def _read(input_data: PhysicellData) -> TrajectoryData:
        """
        Return a TrajectoryData object containing the PhysiCell data
        """
        print("Reading PhysiCell Data -------------")
        agent_data, spatial_units, type_ids = PhysicellConverter._get_trajectory_data(
            input_data
        )
        # get display data (geometry and color)
        for cell_id in input_data.display_data:
            display_data = input_data.display_data[cell_id]
            if cell_id not in type_ids:
                raise DataError(
                    f"cell type ID {cell_id} provided in display_data "
                    "does not exist in PhysiCell data"
                )
                continue
            type_name = display_data.name
            if len(type_ids[cell_id]) < 1:
                agent_data.display_data[display_data.name] = display_data
            else:
                for phase_id in type_ids[cell_id]:
                    if (
                        cell_id in input_data.phase_names
                        and phase_id in input_data.phase_names[cell_id]
                    ):
                        type_name += "#" + input_data.phase_names[cell_id][phase_id]
                    else:
                        type_name += PhysicellConverter._get_default_phase_name(
                            phase_id
                        )
                    agent_data.display_data[type_name] = display_data
        input_data.meta_data._set_box_size()
        return TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=spatial_units,
            plots=input_data.plots,
        )
