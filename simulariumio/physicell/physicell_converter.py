#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Tuple
from pathlib import Path

import numpy as np
from .dep.pyMCDS import pyMCDS

from ..custom_converter import CustomConverter
from ..data_objects import CustomData, AgentData, UnitData
from ..exceptions import MissingDataError
from ..constants import VIZ_TYPE
from .physicell_data import PhysicellData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class PhysicellConverter(CustomConverter):
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
        totalSteps = len(physicell_data)
        max_agents = 0
        discrete_cells = []
        for t in range(totalSteps):
            discrete_cells.append(physicell_data[t].get_cell_df())
            n = len(discrete_cells[t]["position_x"])
            if n > max_agents:
                max_agents = n
        if totalSteps < 1 or max_agents < 1:
            raise MissingDataError(
                "no timesteps or no agents found "
                "in PhysiCell data, is the path_to_output_dir "
                "pointing to an output directory?"
            )
        result = AgentData(
            times=input_data.timestep * np.arange(totalSteps),
            n_agents=np.zeros(totalSteps),
            viz_types=VIZ_TYPE.DEFAULT * np.ones(shape=(totalSteps, max_agents)),
            unique_ids=np.zeros((totalSteps, max_agents)),
            types=[[] for t in range(totalSteps)],
            positions=np.zeros((totalSteps, max_agents, 3)),
            radii=np.ones((totalSteps, max_agents)),
        )
        result.type_ids = np.zeros((totalSteps, max_agents))
        # get data
        for t in range(totalSteps):
            n_agents = int(len(discrete_cells[t]["position_x"]))
            result.n_agents[t] = n_agents
            i = 0
            for n in range(n_agents):
                result.unique_ids[t][i] = i
                tid = self._get_agent_type(
                    cell_type=int(discrete_cells[t]["cell_type"][n]),
                    cell_phase=int(discrete_cells[t]["current_phase"][n]),
                    type_names=input_data.types,
                )
                result.type_ids[t][i] = tid
                while i >= len(result.types[t]):
                    result.types[t].append("")
                result.types[t][i] = self._type_mapping[tid]
                result.positions[t][i] = input_data.scale_factor * np.array(
                    [
                        discrete_cells[t]["position_x"][n],
                        discrete_cells[t]["position_y"][n],
                        discrete_cells[t]["position_z"][n],
                    ]
                )
                result.radii[t][i] = input_data.scale_factor * np.cbrt(
                    3.0 / 4.0 * discrete_cells[t]["total_volume"][n] / np.pi
                )
                i += 1
        spatial_units = UnitData(
            physicell_data[0].data["metadata"]["spatial_units"],
            1.0 / input_data.scale_factor,
        )
        return result, spatial_units

    def _read(self, input_data: PhysicellData) -> CustomData:
        """
        Return a CustomData object containing the PhysiCell data
        """
        print("Reading PhysiCell Data -------------")
        agent_data, spatial_units = self._get_trajectory_data(input_data)
        return CustomData(
            box_size=input_data.scale_factor * input_data.box_size,
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=spatial_units,
            plots=input_data.plots,
        )
