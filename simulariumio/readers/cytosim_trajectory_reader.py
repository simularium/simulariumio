#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any, List, Tuple

import numpy as np

from .trajectory_reader import TrajectoryReader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CytosimTrajectoryReader(TrajectoryReader):
    def parse_fiber_data_dimensions(self, fiber_points_lines: List[str]) -> Tuple[int]:
        """
        Parse a Cytosim fiber_points.txt output file to get the total steps,
        maximum agents per timestep, and maximum subpoints per agent 
        """
        totalSteps = 0
        max_agents = 0
        current_agents = 0
        max_subpoints = 0
        current_subpoints = 0
        for line in fiber_points_lines:
            if len(line) <= 0:
                continue
            if line[0] == "%":
                if "frame" in line:
                    totalSteps += 1
                    if current_agents > max_agents:
                        max_agents = current_agents
                    current_agents = 0
                elif "fiber" in line:
                    current_agents += 1
                    if current_subpoints > max_subpoints:
                        max_subpoints = current_subpoints
                    current_subpoints = 0
            else:
                current_subpoints += 1
        if current_agents > max_agents:
            max_agents = current_agents
        if current_subpoints > max_subpoints:
            max_subpoints = current_subpoints
        return (totalSteps, max_agents, max_subpoints)

    def parse_fibers(
        self, fiber_points_path: str, fiber_type_id: int
    ) -> Dict[str, Any]:
        """
        Parse a Cytosim fiber_points.txt output file to get fiber agents
        """
        with open(fiber_points_path, "r") as myfile:
            data = myfile.read()
        lines = data.split("\n")

        (totalSteps, max_agents, max_subpoints) = self.parse_fiber_data_dimensions(
            lines
        )

        result = {
            "times": np.zeros(totalSteps),
            "n_agents": np.zeros(totalSteps),
            "viz_types": np.zeros((totalSteps, max_agents)),
            "positions": np.zeros((totalSteps, max_agents, 3)),
            "type_ids": np.zeros((totalSteps, max_agents)),
            "radii": np.zeros((totalSteps, max_agents)),
            "n_subpoints": np.zeros((totalSteps, max_agents)),
            "subpoints": np.zeros((totalSteps, max_agents, max_subpoints, 3)),
        }

        t = -1
        n = -1
        s = -1
        for line in lines:

            if len(line) < 1 or line[0:7] == "warning":
                continue

            if line[0] == "%":
                if "frame" in line:
                    # start of frame
                    t += 1
                    n = -1
                elif "time" in line:
                    # time metadata
                    result["times"][t] = float(line.split()[2])
                elif "fiber" in line:
                    # start of fiber
                    if s >= 0:
                        result["n_subpoints"][t][n] = s + 1
                    n += 1
                    s = -1
                elif "end" in line:
                    # end of frame
                    result["n_subpoints"][t][n] = s + 1
                    result["n_agents"][t] = n + 1
                    result["viz_types"][t][0 : n + 1] = (n + 1) * [1001.0]
                    result["type_ids"][t][0 : n + 1] = (n + 1) * [fiber_type_id]
                continue

            s += 1
            columns = line.split()
            result["subpoints"][t][n][s] = 1e3 * np.array(
                [float(columns[1]), float(columns[2]), float(columns[3])]
            )

        return result

    def read(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """
        simularium_data = {}

        fiber_type_id = 0
        agent_data = self.parse_fibers(data["fiber_points_path"], fiber_type_id)

        # trajectory info
        totalSteps = len(agent_data["times"])
        simularium_data["trajectoryInfo"] = {
            "version": 1,
            "timeStepSize": (
                float(agent_data["times"][1] - agent_data["times"][0])
                if totalSteps > 1
                else 0.0
            ),
            "totalSteps": totalSteps,
            "size": {
                "x": float(data["box_size"][0]),
                "y": float(data["box_size"][1]),
                "z": float(data["box_size"][2]),
            },
            "nAgentTypes": 1,
            str(fiber_type_id): {"name": "fiber"},
        }

        # spatial data
        simularium_data["spatialData"] = {
            "version": 1,
            "msgType": 1,
            "bundleStart": 0,
            "bundleSize": totalSteps,
            "bundleData": self._get_spatial_bundle_data_subpoints(agent_data),
        }

        # plot data
        simularium_data["plotData"] = {
            "version": 1,
            "data": data["plots"] if "plots" in data else [],
        }

        return simularium_data
