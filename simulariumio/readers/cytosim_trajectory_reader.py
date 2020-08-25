#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, List, Any

import numpy as np

from .trajectory_reader import TrajectoryReader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CytosimTrajectoryReader(TrajectoryReader):
    def parse_fibers(self, fiber_points_path):
        """
        Parse a Cytosim fiber_points.txt output file to get fiber agents
        """
        with open(fiber_points_path, 'r') as myfile:
            data = myfile.read()
        lines = data.split("\n")

        result = {
            "times" : np.array([]),
            "n_agents" : np.array([]),
            "viz_types" : np.array([]),
            "positions" : np.array([]),
            "type_ids" : [],
            "radii" : np.array([]),
            "subpoints" : np.array([])
        }
        t = -1
        i = -1
        for line in lines:
            
            if len(line) < 1:
                continue

            if "%" in line:
                if "frame" in line:
                    if t >= 0:
                        n = len(subpoints[t])
                        result["n_agents"].append(n)
                        result["viz_types"].append(n * [1001.0])
                        result["positions"].append(np.zeros(shape=(n, 3)))
                        result["type_ids"].append(n * [0])
                        result["radii"].append(np.zeros(shape=(n)))
                    result["subpoints"].append([])
                    t += 1
                    i = -1
                    logging.warning(f"time = {t}")
                elif "time" in line:
                    result["times"].append(float(line.split()[2]))
                elif "fiber" in line:
                    result["subpoints"][t].append([])
                    i += 1
                    logging.warning(f"fiber = {i}")
                continue
                
            logging.warning(f"position for t = {t}, fiber = {i}")
            columns = line.split()
            result["subpoints"][t][i].append(1e3 * np.array(
                [float(columns[2]), float(columns[3]), float(columns[4])]))

        return result

    def read(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """
        simularium_data = {}

        agent_data = self.parse_fibers(data["fiber_points_path"])

        # trajectory info
        totalSteps = len(agent_data["times"])
        simularium_data["trajectoryInfo"] = {
            "version": 1,
            "timeStepSize": (
                float(agent_data["times"][1] - agent_data["times"][0]) if totalSteps > 1 else 0.0
            ),
            "totalSteps": totalSteps,
            "size": {
                "x": float(data["box_size"][0]),
                "y": float(data["box_size"][1]),
                "z": float(data["box_size"][2]),
            },
            "nAgentTypes": 1,
            "0" : {"name": "fiber"}
        }

        # spatial data
        simularium_data["spatialData"] = {
            "version": 1,
            "msgType": 1,
            "bundleStart": 0,
            "bundleSize": totalSteps,
            "bundleData": self._get_spatial_bundle_data_subpoints(
                agent_data
            )
        }

        # plot data
        simularium_data["plotData"] = {
            "version": 1,
            "data": data["plots"] if "plots" in data else [],
        }

        return simularium_data
