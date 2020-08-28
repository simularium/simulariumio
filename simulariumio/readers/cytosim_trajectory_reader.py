#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any, List, Tuple
import sys

import numpy as np

from .trajectory_reader import TrajectoryReader
from ..exceptions import DataError

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CytosimTrajectoryReader(TrajectoryReader):
    def _ignore_line(self, line: str) -> bool:
        """
        if the line doesn't have any data, it can be ignored
        """
        return len(line) < 1 or line[0:7] == "warning" or "report" in line

    def _parse_fiber_data_dimensions(self, fibers_lines: List[str]) -> List[List[int]]:
        """
        Parse a Cytosim fiber_points.txt output file to get the number 
        of subpoints per agent per timestep
        """
        result = []
        t = -1
        n = -1
        for line in fibers_lines:
            if self._ignore_line(line):
                continue
            if line[0] == "%":
                if "frame" in line:
                    result.append([])
                    t += 1
                    n = -1
                elif "fiber" in line:
                    result[t].append(0)
                    n += 1
                continue
            result[t][n] += 1
        return result

    def _parse_other_data_dimensions(self, lines: List[str]) -> List[int]:
        """
        Parse a Cytosim output file containing objects other than fibers 
        (solids, singles, or couples) to get the number of agents per timestep
        """
        result = []
        t = -1
        for line in lines:
            if self._ignore_line(line):
                continue
            if line[0] == "%":
                if "frame" in line:
                    result.append(0)
                    t += 1
                continue
            result[t] += 1
        return result

    def _parse_data_dimensions(self, cytosim_data: Dict[str, List[str]]) -> Tuple[int]:
        """
        Parse Cytosim output files to get the total steps,
        maximum agents per timestep, and maximum subpoints per agent 
        """
        dimensions = []
        if "fibers" in cytosim_data:
            dimensions = self._parse_fiber_data_dimensions(cytosim_data["fibers"])
        for object_type in cytosim_data:
            if object_type != "fibers":
                dims = self._parse_other_data_dimensions(cytosim_data[object_type])
                if len(dimensions) < 1:
                    dimensions = [[0] * dims[t] for t in range(len(dims))]
                else:
                    if len(dims) != len(dimensions):
                        raise DataError(
                            "number of timesteps in Cytosim data is not consistent"
                        )
                    for t in range(len(dimensions)):
                        for n in range(dims[t]):
                            dimensions[t].append(0)
        max_agents = 0
        for t in range(len(dimensions)):
            n = len(dimensions[t])
            if n > max_agents:
                max_agents = n
        return (len(dimensions), max_agents, np.amax(np.array(dimensions)))

    def _parse_fibers(
        self,
        fibers_lines: List[str],
        scale_factor: float,
        result: Dict[str, Any],
        agent_types: Dict[int, Any],
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Parse a Cytosim fiber_points.txt output file to get fiber agents
        """
        t = -1
        n = -1
        s = -1
        parse_time = (
            result["times"].size > 0
            and float(result["times"][1]) < sys.float_info.epsilon
        )
        types = {}
        for line in fibers_lines:
            if self._ignore_line(line):
                continue
            if line[0] == "%":
                if "frame" in line:
                    # start of frame
                    t += 1
                    n_other_agents = int(result["n_agents"][t])
                    n = -1
                elif "time" in line and parse_time:
                    # time metadata
                    result["times"][t] = float(line.split()[2])
                elif "fiber" in line:
                    # start of fiber
                    n += 1
                    if n > 0 and s >= 0:
                        result["n_subpoints"][t][n_other_agents + n - 1] = s + 1
                    s = -1
                    tid = int(line.split()[2].split(":")[0][1:])
                    if tid not in types:
                        raw_id = tid
                        while tid in agent_types:
                            tid += 1
                        types[raw_id] = tid
                        agent_types[tid] = {"object_type": "fibers", "raw_id": raw_id}
                    else:
                        tid = types[tid]
                    result["type_ids"][t][n_other_agents + n] = tid
                elif "end" in line:
                    # end of frame
                    result["n_subpoints"][t][n_other_agents + n] = s + 1
                    result["n_agents"][t] += n + 1
                    result["viz_types"][t][n_other_agents : n_other_agents + n + 1] = (
                        n + 1
                    ) * [1001.0]
                continue
            s += 1
            columns = line.split()
            result["subpoints"][t][n_other_agents + n][s] = scale_factor * np.array(
                [float(columns[1]), float(columns[2]), float(columns[3])]
            )
        return (result, agent_types)

    def _parse_others(
        self,
        object_type: str,
        data_lines: List[str],
        scale_factor: float,
        agent_data: Dict[str, float],
        result: Dict[str, Any],
        agent_types: Dict[int, Any],
    ) -> Tuple[Dict[str, Any], List[str]]:
        """
        Parse a Cytosim output file containing objects other than fibers 
        (solids, singles, or couples) to get default agents
        """
        t = -1
        n = -1
        n_other_agents = 0
        parse_time = (
            result["times"].size > 0
            and float(result["times"][1]) < sys.float_info.epsilon
        )
        types = {}
        if object_type == "couples":
            position_indices = [3, 4, 5]
        else:
            position_indices = [2, 3, 4]
        for line in data_lines:
            if self._ignore_line(line):
                continue
            if line[0] == "%":
                if "frame" in line:
                    # start of frame
                    if t >= 0:
                        result["n_agents"][t] += n + 1
                        result["viz_types"][t][
                            n_other_agents : n_other_agents + n + 1
                        ] = (n + 1) * [1000.0]
                    t += 1
                    n_other_agents = int(result["n_agents"][t])
                    n = -1
                elif "time" in line and parse_time:
                    # time metadata
                    result["times"][t] = float(line.split()[2])
                continue
            n += 1
            columns = line.split()
            tid = int(columns[0])
            raw_id = tid
            if tid not in types:
                while tid in agent_types:
                    tid += 1
                types[raw_id] = tid
                agent_types[tid] = {"object_type": object_type, "raw_id": raw_id}
            else:
                tid = types[tid]
            result["type_ids"][t][n_other_agents + n] = tid
            result["positions"][t][n_other_agents + n] = scale_factor * np.array(
                [
                    float(columns[position_indices[0]]),
                    float(columns[position_indices[1]]),
                    float(columns[position_indices[2]]),
                ]
            )
            raw_id = str(raw_id)
            result["radii"][t][n_other_agents + n] = (
                (scale_factor * float(agent_data[raw_id]["radius"]))
                if raw_id in agent_data and "radius" in agent_data[raw_id]
                else 1.0
            )
        result["n_agents"][t] += n + 1
        result["viz_types"][t][n_other_agents : n_other_agents + n + 1] = (n + 1) * [
            1000.0
        ]
        return (result, agent_types)

    def read(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """
        # load the data from Cytosim output .txt files
        cytosim_data = {}
        for object_type in data["data"]:
            with open(data["data"][object_type]["filepath"], "r") as myfile:
                cytosim_data[object_type] = myfile.read().split("\n")

        # parse
        (totalSteps, max_agents, max_subpoints) = self._parse_data_dimensions(
            cytosim_data
        )
        agent_data = {
            "times": np.zeros(totalSteps),
            "n_agents": np.zeros(totalSteps),
            "viz_types": np.zeros((totalSteps, max_agents)),
            "positions": np.zeros((totalSteps, max_agents, 3)),
            "type_ids": np.zeros((totalSteps, max_agents)),
            "radii": np.zeros((totalSteps, max_agents)),
            "n_subpoints": np.zeros((totalSteps, max_agents)),
            "subpoints": np.zeros((totalSteps, max_agents, max_subpoints, 3)),
        }
        agent_types = {}
        scale = float(data["scale_factor"]) if "scale_factor" in data else 1.0
        for object_type in data["data"]:
            if object_type != "fibers":
                agent_data, agent_types = self._parse_others(
                    object_type,
                    cytosim_data[object_type],
                    scale,
                    data["data"][object_type]["agents"]
                    if "agents" in data["data"][object_type]
                    else {},
                    agent_data,
                    agent_types,
                )
            else:
                agent_data, agent_types = self._parse_fibers(
                    cytosim_data[object_type], scale, agent_data, agent_types
                )

        # shape data
        simularium_data = {}

        # trajectory info
        totalSteps = agent_data["times"].size
        simularium_data["trajectoryInfo"] = {
            "version": 1,
            "timeStepSize": (
                float(agent_data["times"][1] - agent_data["times"][0])
                if totalSteps > 1
                else 0.0
            ),
            "totalSteps": totalSteps,
            "size": {
                "x": scale * float(data["box_size"][0]),
                "y": scale * float(data["box_size"][1]),
                "z": scale * float(data["box_size"][2]),
            },
            "nAgentTypes": len(agent_types),
        }
        for tid in agent_types:
            s = str(tid)
            object_type = agent_types[tid]["object_type"]
            raw_id = str(agent_types[tid]["raw_id"])
            if (
                "agents" in data["data"][object_type]
                and raw_id in data["data"][object_type]["agents"]
                and "name" in data["data"][object_type]["agents"][raw_id]
            ):
                simularium_data["trajectoryInfo"][s] = {
                    "name": data["data"][object_type]["agents"][raw_id]["name"]
                }
            else:
                simularium_data["trajectoryInfo"][s] = {"name": object_type + raw_id}

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
