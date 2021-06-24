#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from simulariumio.data_objects.dimension_data import DimensionData
from typing import Dict, Tuple
from pathlib import Path

import numpy as np
from .dep.pyMCDS import pyMCDS

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, UnitData, MetaData
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
        self._ids = {}
        self._last_id = 0
        self._type_mapping = {}
        self._data = self._read(input_data)

    def _load_data(self, path_to_output_dir) -> np.ndarray:
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

    def _get_agent_type(
        self, cell_type: int, cell_phase: int, type_names: Dict[int, Dict[int, str]]
    ) -> int:
        """
        Get a unique agent type ID for a specific cell type and phase combination
        """
        if cell_type not in self._ids:
            self._ids[cell_type] = {}
        if cell_phase not in self._ids[cell_type]:
            self._ids[cell_type][cell_phase] = self._last_id
            type_name = ""
            if (
                type_names is not None
                and cell_type in type_names
                and "name" in type_names[cell_type]
            ):
                type_name = type_names[cell_type]["name"]
            else:
                type_name = f"cell {cell_type}"
            if (
                type_names is not None
                and cell_type in type_names
                and cell_phase in type_names[cell_type]
            ):
                type_name += "#" + type_names[cell_type][cell_phase]
            else:
                type_name += f"#phase {cell_phase}"
            self._type_mapping[self._last_id] = type_name
            self._last_id += 1
        return self._ids[cell_type][cell_phase]

    def _get_trajectory_data(
        self, input_data: PhysicellData
    ) -> Tuple[AgentData, UnitData]:
        """
        Get data from one time step in Simularium format
        """
        physicell_data = self._load_data(input_data.path_to_output_dir)
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
            result = result.check_increase_buffer_size(time_index, axis=0)
            n_agents = int(len(discrete_cells[time_index]["position_x"]))
            result.n_agents[time_index] = n_agents
            for agent_index in range(n_agents):
                result = result.check_increase_buffer_size(agent_index, axis=1)
                result.unique_ids[time_index][agent_index] = agent_index
                tid = self._get_agent_type(
                    cell_type=int(discrete_cells[time_index]["cell_type"][agent_index]),
                    cell_phase=int(
                        discrete_cells[time_index]["current_phase"][agent_index]
                    ),
                    type_names=input_data.types,
                )
                result.types[time_index].append(self._type_mapping[tid])
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
                ] = input_data.meta_data.scale_factor * np.cbrt(
                    3.0
                    / 4.0
                    * discrete_cells[time_index]["total_volume"][agent_index]
                    / np.pi
                )
        spatial_units = UnitData(
            physicell_data[0].data["metadata"]["spatial_units"],
            1.0 / input_data.meta_data.scale_factor,
        )
        result.n_timesteps = total_steps
        return result, spatial_units

    def _read(self, input_data: PhysicellData) -> TrajectoryData:
        """
        Return a TrajectoryData object containing the PhysiCell data
        """
        print("Reading PhysiCell Data -------------")
        agent_data, spatial_units = self._get_trajectory_data(input_data)
        return TrajectoryData(
            meta_data=MetaData(
                box_size=input_data.meta_data.scale_factor
                * input_data.meta_data.box_size,
                camera_defaults=input_data.meta_data.camera_defaults,
            ),
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=spatial_units,
            plots=input_data.plots,
        )
