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

    def _parse_fiber_data_dimensions(
        self, fibers_lines: List[str], draw_points: bool
    ) -> Tuple[List[int], int]:
        """
        Parse a Cytosim fiber_points.txt output file to get the number 
        of subpoints per agent per timestep
        """
        result = []
        t = -1
        s = 0
        max_subpoints = 0
        n_test_frames = 150 # TEST t
        for line in fibers_lines:
            if self._ignore_line(line):
                continue
            if line[0] == "%":
                if "frame" in line:
                    if t >= n_test_frames-1: # TEST
                        return (result, max_subpoints)
                    result.append(0)
                    t += 1
                elif "fiber" in line:
                    result[t] += 1
                    if s > max_subpoints:
                        max_subpoints = s
                    s = 0
                continue
            s += 1
            if draw_points:
                result[t] += 1
        if s > max_subpoints:
            max_subpoints = s
        return (result, max_subpoints)

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

    def _parse_data_dimensions(
        self, cytosim_data: Dict[str, List[str]], draw_fiber_points: bool
    ) -> Tuple[int]:
        """
        Parse Cytosim output files to get the total steps,
        maximum agents per timestep, and maximum subpoints per agent 
        """
        dimensions = []
        max_subpoints = 0
        for object_type in cytosim_data:
            if object_type == "fibers":
                dims, max_subpoints = self._parse_fiber_data_dimensions(
                    cytosim_data[object_type], draw_fiber_points
                )
            else:
                dims = self._parse_other_data_dimensions(cytosim_data[object_type])
            if len(dimensions) < 1:
                dimensions = dims
            else:
                if len(dims) != len(dimensions):
                    raise DataError(
                        "number of timesteps in Cytosim data is not consistent"
                    )
                for t in range(len(dimensions)):
                    dimensions[t] += dims[t]
        max_agents = 0
        for t in range(len(dimensions)):
            if dimensions[t] > max_agents:
                max_agents = dimensions[t]
        return (len(dimensions), max_agents, max_subpoints)

    def _parse_fibers(
        self,
        fibers_lines: List[str],
        scale_factor: float,
        draw_fiber_points: bool,
        result: Dict[str, Any],
        agent_types: Dict[int, Any],
        used_unique_IDs: List[int],
    ) -> Tuple[Dict[str, Any], List[str], List[int]]:
        """
        Parse a Cytosim fiber_points.txt output file to get fiber agents
        """
        t = -1
        n = -1
        s = -1
        parse_time = (
            result["times"].size > 1
            and float(result["times"][1]) < sys.float_info.epsilon
        )
        types = {}
        uids = {}
        n_test_agents = 18 # TEST
        n_test_frames = 150 # TEST t
        for line in fibers_lines:
            if self._ignore_line(line):
                continue
            if line[0] == "%":
                if "frame" in line:
                    # start of frame
                    if t >= n_test_frames-1: # TEST
                        break
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
                        if n <= n_test_agents: # TEST
                            result["n_subpoints"][t][n_other_agents + n - 1] = s + 1
                    s = -1
                    fiber_info = line.split()[2].split(":")
                    # unique instance ID
                    raw_uid = int(fiber_info[1])
                    if raw_uid not in uids:
                        uid = raw_uid
                        while uid in used_unique_IDs:
                            uid += 1
                        uids[raw_uid] = uid
                        used_unique_IDs.append(uid)
                    else:
                        uid = uids[raw_uid]
                    if n < n_test_agents: # TEST
                        result["unique_ids"][t][n_other_agents + n] = uid
                    # type ID
                    raw_tid = int(fiber_info[0][1:])
                    if raw_tid not in types:
                        tid = raw_tid
                        while tid in agent_types:
                            tid += 1
                        types[raw_tid] = tid
                        agent_types[tid] = {"object_type": "fibers", "raw_id": raw_tid}
                    else:
                        tid = types[raw_tid]
                    if n < n_test_agents: # TEST
                        if n == n_test_agents-1: # TEST
                            result["type_ids"][t][n_other_agents + n] = tid + 1
                        else:
                            result["type_ids"][t][n_other_agents + n] = tid
                elif "end" in line:
                    # end of frame
                    # result["n_subpoints"][t][n_other_agents + n] = s + 1 # TEST
                    n = n_test_agents-1 # TEST
                    result["n_agents"][t] += n + 1
                    result["viz_types"][t][n_other_agents : n_other_agents + n + 1] = (
                        n + 1
                    ) * [1001.0]
                continue
            s += 1
            if n < n_test_agents: # TEST
                columns = line.split()
                result["subpoints"][t][n_other_agents + n][s] = scale_factor * np.array(
                    [float(columns[1]), float(columns[2]), float(columns[3])]
                )

        agent_types[1] = {"object_type": "fibers", "raw_id": 1} # TEST

        if draw_fiber_points:
            t = -1
            n = -1
            i = 0
            uids = {}
            for line in fibers_lines:

                if self._ignore_line(line):
                    continue
                if line[0] == "%":
                    if "frame" in line:
                        # start of frame
                        if t >= n_test_frames-1: # TEST
                            return (result, agent_types, used_unique_IDs)
                        t += 1
                        n_other_agents = int(result["n_agents"][t])
                        n = -1
                        i = 0
                    elif "fiber" in line:
                        # start of fiber
                        n += 1
                        fiber_info = line.split()[2].split(":")
                        # # type ID TEST
                        # raw_tid = int(fiber_info[0][1:])
                        # if raw_tid not in types:
                        #     tid = raw_tid
                        #     while tid in agent_types:
                        #         tid += 1
                        #     types[raw_tid] = tid
                        #     agent_types[tid] = {"object_type": "fibers", "raw_id": raw_tid}
                    elif "end" in line:
                        # end of frame
                        result["n_agents"][t] += i
                        result["viz_types"][t][
                            n_other_agents : n_other_agents + i
                        ] = i * [1000.0]
                        result["radii"][t][n_other_agents : n_other_agents + i] = (
                            i
                        ) * [0.5]
                    continue
                if n < n_test_agents: # TEST
                    columns = line.split()
                    result["positions"][t][n_other_agents + i] = scale_factor * np.array(
                        [float(columns[1]), float(columns[2]), float(columns[3])]
                    )
                    # unique instance ID
                    raw_uid = i
                    if raw_uid not in uids:
                        uid = raw_uid
                        while uid in used_unique_IDs:
                            uid += 1
                        uids[raw_uid] = uid
                        used_unique_IDs.append(uid)
                    result["unique_ids"][t][n_other_agents + i] = uids[raw_uid]
                    if n == n_test_agents-1: # TEST
                        result["type_ids"][t][n_other_agents + i] = types[
                            int(fiber_info[0][1:])
                        ] + 1
                    else:
                        result["type_ids"][t][n_other_agents + i] = types[
                            int(fiber_info[0][1:])
                        ]
                    i += 1

        return (result, agent_types, used_unique_IDs)

    def _parse_others(
        self,
        object_type: str,
        data_lines: List[str],
        scale_factor: float,
        agent_data: Dict[str, float],
        position_indices: List[int],
        result: Dict[str, Any],
        agent_types: Dict[int, Any],
        used_unique_IDs: List[int],
    ) -> Tuple[Dict[str, Any], List[str], List[int]]:
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
        uids = {}
        if len(position_indices) < 3:
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
            # unique instance ID
            raw_uid = int(columns[1])
            if raw_uid not in uids:
                uid = raw_uid
                while uid in used_unique_IDs:
                    uid += 1
                uids[raw_uid] = uid
                used_unique_IDs.append(uid)
            else:
                uid = uids[raw_uid]
            result["unique_ids"][t][n_other_agents + n] = uid
            # type ID
            raw_tid = int(columns[0])
            if raw_tid not in types:
                tid = raw_tid
                while tid in agent_types:
                    tid += 1
                types[raw_tid] = tid
                agent_types[tid] = {"object_type": object_type, "raw_id": raw_tid}
            else:
                tid = types[raw_tid]
            result["type_ids"][t][n_other_agents + n] = tid
            # position
            result["positions"][t][n_other_agents + n] = scale_factor * np.array(
                [
                    float(columns[position_indices[0]]),
                    float(columns[position_indices[1]]),
                    float(columns[position_indices[2]]),
                ]
            )
            # radius
            raw_tid = str(raw_tid)
            result["radii"][t][n_other_agents + n] = (
                (scale_factor * float(agent_data[raw_tid]["radius"]))
                if raw_tid in agent_data and "radius" in agent_data[raw_tid]
                else 1.0
            )
        result["n_agents"][t] += n + 1
        result["viz_types"][t][n_other_agents : n_other_agents + n + 1] = (n + 1) * [
            1000.0
        ]
        return (result, agent_types, used_unique_IDs)

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
        draw_fiber_points = (
            bool(data["data"]["fibers"]["draw_points"])
            if "fibers" in data["data"] and "draw_points" in data["data"]["fibers"]
            else False
        )
        (totalSteps, max_agents, max_subpoints) = self._parse_data_dimensions(
            cytosim_data, draw_fiber_points
        )
        agent_data = {
            "times": np.zeros(totalSteps),
            "n_agents": np.zeros(totalSteps),
            "viz_types": np.zeros((totalSteps, max_agents)),
            "unique_ids": np.zeros((totalSteps, max_agents)),
            "type_ids": np.zeros((totalSteps, max_agents)),
            "positions": np.zeros((totalSteps, max_agents, 3)),
            "radii": np.zeros((totalSteps, max_agents)),
            "n_subpoints": np.zeros((totalSteps, max_agents)),
            "subpoints": np.zeros((totalSteps, max_agents, max_subpoints, 3)),
        }
        agent_types = {}
        uids = []
        scale = float(data["scale_factor"]) if "scale_factor" in data else 1.0
        for object_type in data["data"]:
            if object_type != "fibers":
                agent_data, agent_types, uids = self._parse_others(
                    object_type,
                    cytosim_data[object_type],
                    scale,
                    data["data"][object_type]["agents"]
                    if "agents" in data["data"][object_type]
                    else {},
                    data["data"][object_type]["position_indices"]
                    if "position_indices" in data["data"][object_type]
                    else [],
                    agent_data,
                    agent_types,
                    uids,
                )
            else:
                agent_data, agent_types, uids = self._parse_fibers(
                    cytosim_data[object_type],
                    scale,
                    draw_fiber_points,
                    agent_data,
                    agent_types,
                    uids,
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
            "typeMapping": {},
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
                simularium_data["trajectoryInfo"]["typeMapping"][s] = {
                    "name": data["data"][object_type]["agents"][raw_id]["name"]
                }
            else:
                simularium_data["trajectoryInfo"]["typeMapping"][s] = {
                    "name": object_type[:-1] + raw_id
                }

        # spatial data
        simularium_data["spatialData"] = {
            "version": 1,
            "msgType": 1,
            "bundleStart": 0,
            "bundleSize": totalSteps,
            "bundleData": self._get_spatial_bundle_data_subpoints(agent_data),
        }

        # # TEST: add spheres at box extents
        # print(simularium_data["trajectoryInfo"]["size"]["x"]/2)
        # for t in range(len(simularium_data["spatialData"]["bundleData"])):
        #     simularium_data["spatialData"]["bundleData"][t]["data"] += [1000.0, 100.0, 0.0, -simularium_data["trajectoryInfo"]["size"]["x"]/2, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 0.0]
        #     simularium_data["spatialData"]["bundleData"][t]["data"] += [1000.0, 100.0, 0.0, simularium_data["trajectoryInfo"]["size"]["x"]/2, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 0.0]
        #     simularium_data["spatialData"]["bundleData"][t]["data"] += [1000.0, 100.0, 0.0, 0.0, -simularium_data["trajectoryInfo"]["size"]["y"]/2, 0.0, 0.0, 0.0, 0.0, 10.0, 0.0]
        #     simularium_data["spatialData"]["bundleData"][t]["data"] += [1000.0, 100.0, 0.0, 0.0, simularium_data["trajectoryInfo"]["size"]["y"]/2, 0.0, 0.0, 0.0, 0.0, 10.0, 0.0]
        #     simularium_data["spatialData"]["bundleData"][t]["data"] += [1000.0, 100.0, 0.0, 0.0, 0.0, -simularium_data["trajectoryInfo"]["size"]["z"]/2, 0.0, 0.0, 0.0, 10.0, 0.0]
        #     simularium_data["spatialData"]["bundleData"][t]["data"] += [1000.0, 100.0, 0.0, 0.0, 0.0, simularium_data["trajectoryInfo"]["size"]["z"]/2, 0.0, 0.0, 0.0, 10.0, 0.0]

        # plot data
        simularium_data["plotData"] = {
            "version": 1,
            "data": data["plots"] if "plots" in data else [],
        }

        return simularium_data
