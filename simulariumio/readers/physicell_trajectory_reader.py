#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List, Tuple

import numpy as np

from ..dep.pyMCDS import pyMCDS

from .trajectory_reader import TrajectoryReader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class PhysiCellTrajectoryReader(TrajectoryReader):
    def __init__(self):
        self.ids = {}
        self.last_id = 0
        self.type_mapping = {}
        print("did physicell init")

    def _load_data(self, path_to_xml_files) -> np.ndarray:
        """ 
        Load simulation data from PhysiCell MultiCellDS XML files 
        """
        sorted_files = sorted(Path(path_to_xml_files).glob("output*.xml"))
        data = []
        for file in sorted_files:
            data.append(pyMCDS(file.name, False, path_to_xml_files))
        return np.array(data)

    def _get_agent_type(
        self, cell_type: int, cell_phase: int, type_names: Dict[int, Dict[int, str]]
    ) -> int:
        """ 
        Get a unique agent type ID for a specific cell type and phase combination 
        """
        if cell_type not in self.ids:
            self.ids[cell_type] = {}
        if cell_phase not in self.ids[cell_type]:
            self.ids[cell_type][cell_phase] = self.last_id
            if cell_type < len(type_names) and cell_phase < len(type_names[cell_type]):
                self.type_mapping[str(self.last_id)] = {
                    "name": type_names[cell_type][cell_phase]
                }
            else:
                self.type_mapping[str(self.last_id)] = {
                    "name": f"cell{cell_type}#{cell_phase}"
                }
            self.last_id += 1
        return self.ids[cell_type][cell_phase]

    def _get_trajectory_data(
        self, data: Dict[str, Any], scale_factor: float
    ) -> Dict[str, Any]:
        """ 
        Get data from one time step in Simularium format 
        """
        physicell_data = self._load_data(data["path_to_xml_files"])
        # get data dimensions
        totalSteps = len(physicell_data)
        max_agents = 0
        discrete_cells = []
        for t in range(totalSteps):
            discrete_cells.append(physicell_data[t].get_cell_df())
            n = len(discrete_cells[t]["position_x"])
            if n > max_agents:
                max_agents = n
        result = {
            "times": float(data["timestep"]) * np.arange(totalSteps),
            "n_agents": np.zeros(totalSteps),
            "viz_types": 1000.0 * np.ones(shape=(totalSteps, max_agents)),
            "unique_ids": np.zeros((totalSteps, max_agents)),
            "type_ids": np.zeros((totalSteps, max_agents)),
            "positions": np.zeros((totalSteps, max_agents, 3)),
            "radii": np.ones((totalSteps, max_agents))
        }
        # get data
        type_names = data["types"] if "types" in data else []
        for t in range(totalSteps):
            result["n_agents"][t] = len(discrete_cells[t]["position_x"])
            i = 0
            for n in range(result["n_agents"][t]):
                result["unique_ids"][t][i] = i
                result["type_ids"][t][i] = float(
                    self._get_agent_type(
                        int(discrete_cells[t]["cell_type"][n]),
                        int(discrete_cells[t]["current_phase"][n]),
                        type_names,
                    )
                )
                result["positions"][t][i] = scale * [
                    discrete_cells[t]["position_x"][n], 
                    discrete_cells[t]["position_y"][n], 
                    discrete_cells[t]["position_z"][n]
                ]
                result["radii"][t][i] = np.cbrt(
                    3.0 / 4.0 * discrete_cells[t]["total_volume"][n] / np.pi)
                i += 1
        return result

    def read(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """
        # load the data from PhysiCell MultiCellDS XML files
        scale = float(data["scale_factor"]) if "scale_factor" in data else 1.0
        agent_data = self._get_trajectory_data(data, scale)
        # shape data
        simularium_data = {}
        # trajectory info
        totalSteps = agent_data["n_agents"].shape[0]
        simularium_data["trajectoryInfo"] = {
            "version": 1,
            "timeStepSize": float(data["timestep"]),
            "totalSteps": totalSteps,
            "size": {
                "x": scale * float(data["box_size"][0]),
                "y": scale * float(data["box_size"][1]),
                "z": scale * float(data["box_size"][2]),
            },
            "typeMapping": self.type_mapping,
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
            "data": data["plots"] if "plots" in data else [],
        }
        return simularium_data
