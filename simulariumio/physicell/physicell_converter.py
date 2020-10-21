#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict
from pathlib import Path

import numpy as np
from .dep.pyMCDS import pyMCDS

from ..converter import Converter
from ..data_objects import AgentData
from ..exceptions import MissingDataError
from ..constants import VIZ_TYPE
from .physicell_data import PhysicellData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class PhysicellConverter(Converter):
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
            self._type_mapping[str(self._last_id)] = {"name": type_name}
            self._last_id += 1
        return self._ids[cell_type][cell_phase]

    def _get_trajectory_data(self, input_data: PhysicellData) -> AgentData:
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
            viz_types=VIZ_TYPE.default * np.ones(shape=(totalSteps, max_agents)),
            unique_ids=np.zeros((totalSteps, max_agents)),
            types=None,
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
                result.type_ids[t][i] = self._get_agent_type(
                    cell_type=int(discrete_cells[t]["cell_type"][n]),
                    cell_phase=int(discrete_cells[t]["current_phase"][n]),
                    type_names=input_data.types,
                )
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
        return result

    def _read(self, input_data: PhysicellData) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """
        # load the data from PhysiCell MultiCellDS XML files
        agent_data = self._get_trajectory_data(input_data)
        # shape data
        simularium_data = {}
        # trajectory info
        totalSteps = agent_data.n_agents.shape[0]
        simularium_data["trajectoryInfo"] = {
            "version": 1,
            "timeStepSize": input_data.timestep,
            "totalSteps": totalSteps,
            "size": {
                "x": input_data.scale_factor * float(input_data.box_size[0]),
                "y": input_data.scale_factor * float(input_data.box_size[1]),
                "z": input_data.scale_factor * float(input_data.box_size[2]),
            },
            "typeMapping": self._type_mapping,
        }
        # spatial data
        simularium_data["spatialData"] = {
            "version": 1,
            "msgType": 1,
            "bundleStart": 0,
            "bundleSize": totalSteps,
            "bundleData": self._get_spatial_bundle_data_no_subpoints(agent_data),
        }
        # plot data
        simularium_data["plotData"] = {
            "version": 1,
            "data": input_data.plots,
        }
        return simularium_data
