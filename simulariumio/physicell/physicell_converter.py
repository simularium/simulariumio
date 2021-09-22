#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from simulariumio.data_objects.dimension_data import DimensionData
from typing import Dict, Tuple
from pathlib import Path

import numpy as np
from .dep.pyMCDS import pyMCDS

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, UnitData
from ..exceptions import MissingDataError
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
    def _load_data(path_to_output_dir) -> np.ndarray:
        """
        Load simulation data from PhysiCell MultiCellDS XML files
        """
        files = Path(path_to_output_dir).glob("*output*.xml")
        file_mapping = {}
        for f in files:
            index = int(f.name[f.name.index("output") + 6 :].split(".")[0])
            file_mapping[index] = f
        data = []
        for t, xml_file in sorted(file_mapping.items()):
            data.append(pyMCDS(xml_file.name, False, path_to_output_dir))
        return np.array(data)

    @staticmethod
    def _get_default_cell_name(cell_type: int) -> str:
        return f"cell{cell_type}"

    @staticmethod
    def _get_default_phase_name(cell_phase: int) -> str:
        return f"#phase{cell_phase}"

    @staticmethod
    def _get_agent_type(
        cell_type: int,
        cell_phase: int,
        input_data: PhysicellData,
        ids: Dict[int, Dict[int, int]],
        last_id: int,
        type_mapping: Dict[int, str],
    ) -> int:
        """
        Get a unique agent type ID for a specific cell type and phase combination
        """
        if cell_type not in ids:
            ids[cell_type] = {}
        if cell_phase not in ids[cell_type]:
            ids[cell_type][cell_phase] = last_id
            type_name = ""
            if cell_type in input_data.display_data:
                type_name = input_data.display_data[cell_type].name
            else:
                type_name = PhysicellConverter._get_default_cell_name(cell_type)
            if (
                cell_type in input_data.phase_names
                and cell_phase in input_data.phase_names[cell_type]
            ):
                type_name += "#" + input_data.phase_names[cell_type][cell_phase]
            else:
                type_name += PhysicellConverter._get_default_phase_name(cell_phase)
            type_mapping[last_id] = type_name
            last_id += 1
        return ids[cell_type][cell_phase], ids, last_id, type_mapping

    @staticmethod
    def _get_trajectory_data(input_data: PhysicellData) -> Tuple[AgentData, UnitData]:
        """
        Get data from one time step in Simularium format
        """
        ids = {}
        last_id = 0
        type_mapping = {}
        physicell_data = PhysicellConverter._load_data(input_data.path_to_output_dir)
        # get data dimensions
        total_steps = len(physicell_data)
        max_agents = 0
        discrete_cells = []
        for time_index in range(total_steps):
            discrete_cells.append(physicell_data[time_index].get_cell_df())
            n = len(discrete_cells[time_index]["position_x"])
            if n > max_agents:
                max_agents = n
        if total_steps < 1 or max_agents < 1:
            raise MissingDataError(
                "no timesteps or no agents found in PhysiCell data, "
                "is the path_to_output_dir pointing to an output directory?"
            )
        result = AgentData.from_dimensions(
            DimensionData(
                total_steps=total_steps,
                max_agents=max_agents,
            )
        )
        result.times = input_data.timestep * np.arange(total_steps)
        # get data
        for time_index in range(total_steps):
            n_agents = int(len(discrete_cells[time_index]["position_x"]))
            result.n_agents[time_index] = n_agents
            for agent_index in range(n_agents):
                result.unique_ids[time_index][agent_index] = agent_index
                cell_type = int(discrete_cells[time_index]["cell_type"][agent_index])
                cell_phase = int(
                    discrete_cells[time_index]["current_phase"][agent_index]
                )
                tid, ids, last_id, type_mapping = PhysicellConverter._get_agent_type(
                    cell_type=cell_type,
                    cell_phase=cell_phase,
                    input_data=input_data,
                    ids=ids,
                    last_id=last_id,
                    type_mapping=type_mapping,
                )
                result.types[time_index].append(type_mapping[tid])
                result.positions[time_index][
                    agent_index
                ] = input_data.meta_data.scale_factor * np.array(
                    [
                        discrete_cells[time_index]["position_x"][agent_index],
                        discrete_cells[time_index]["position_y"][agent_index],
                        discrete_cells[time_index]["position_z"][agent_index],
                    ]
                )
                result.radii[time_index][
                    agent_index
                ] = input_data.meta_data.scale_factor * (
                    input_data.display_data[cell_type].radius
                    if cell_type in input_data.display_data
                    and input_data.display_data[cell_type].radius is not None
                    else np.cbrt(
                        3.0
                        / 4.0
                        * discrete_cells[time_index]["total_volume"][agent_index]
                        / np.pi
                    )
                )
        spatial_units = UnitData(
            physicell_data[0].data["metadata"]["spatial_units"],
            1.0 / input_data.meta_data.scale_factor,
        )
        result.n_timesteps = total_steps
        return result, spatial_units, ids

    @staticmethod
    def _read(input_data: PhysicellData) -> TrajectoryData:
        """
        Return a TrajectoryData object containing the PhysiCell data
        """
        print("Reading PhysiCell Data -------------")
        agent_data, spatial_units, id_mapping = PhysicellConverter._get_trajectory_data(
            input_data
        )
        # get display data (geometry and color)
        for cell_id in input_data.display_data:
            display_data = input_data.display_data[cell_id]
            if cell_id not in id_mapping:
                print(
                    f"cell type ID {cell_id} provided in display_data does not exist "
                    "in PhysiCell data, skipping its rendering info"
                )
                continue
            type_name = display_data.name
            for phase_id in id_mapping[cell_id]:
                if (
                    cell_id in input_data.phase_names
                    and phase_id in input_data.phase_names[cell_id]
                ):
                    type_name += "#" + input_data.phase_names[cell_id][phase_id]
                else:
                    type_name += PhysicellConverter._get_default_phase_name(phase_id)
                agent_data.display_data[type_name] = display_data
        input_data.meta_data._set_box_size()
        return TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=spatial_units,
            plots=input_data.plots,
        )
