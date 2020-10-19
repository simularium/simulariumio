#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List, Tuple
import sys

import numpy as np

from ..converter import Converter
from ..data_objects import AgentData
from ..exceptions import DataError
from ..constants import VIZ_TYPE
from .cytosim_data import CytosimData
from .cytosim_object_info import CytosimObjectInfo

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CytosimConverter(Converter):
    def __init__(self, input_data: CytosimData):
        """
        This object reads simulation trajectory outputs
        from CytoSim (https://gitlab.com/f.nedelec/cytosim)
        and plot data and writes them in the JSON format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : CytosimData
            An object containing info for reading
            Cytosim simulation trajectory outputs and plot data
        """
        self._data = self._read(input_data)

    def _ignore_line(self, line: str) -> bool:
        """
        if the line doesn't have any data, it can be ignored
        """
        return len(line) < 1 or line[0:7] == "warning" or "report" in line

    def _parse_fiber_data_dimensions(
        self, fibers_lines: List[str]
    ) -> Tuple[List[int], int]:
        """
        Parse a Cytosim fiber_points.txt output file to get the number
        of subpoints per agent per timestep
        """
        result = []
        t = -1
        s = 0
        max_subpoints = 0
        for line in fibers_lines:
            if self._ignore_line(line):
                continue
            if line[0] == "%":
                if "frame" in line:
                    result.append(0)
                    t += 1
                elif "fiber" in line:
                    result[t] += 1
                    if s > max_subpoints:
                        max_subpoints = s
                    s = 0
                continue
            s += 1
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

    def _parse_data_dimensions(self, cytosim_data: Dict[str, List[str]]) -> Tuple[int]:
        """
        Parse Cytosim output files to get the total steps,
        maximum agents per timestep, and maximum subpoints per agent
        """
        dimensions = []
        max_subpoints = 0
        for object_type in cytosim_data:
            if object_type == "fibers":
                dims, max_subpoints = self._parse_fiber_data_dimensions(
                    cytosim_data[object_type]
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
        result: AgentData,
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
            result.times.size > 1 and float(result.times[1]) < sys.float_info.epsilon
        )
        types = {}
        uids = {}
        for line in fibers_lines:
            if self._ignore_line(line):
                continue
            if line[0] == "%":
                if "frame" in line:
                    # start of frame
                    t += 1
                    n_other_agents = int(result.n_agents[t])
                    n = -1
                elif "time" in line and parse_time:
                    # time metadata
                    result.times[t] = float(line.split()[2])
                elif "fiber" in line:
                    # start of fiber
                    if n >= 0 and s >= 0:
                        result.n_subpoints[t][n_other_agents + n] = s + 1
                    n += 1
                    s = -1
                    result.viz_types[t][n_other_agents + n] = VIZ_TYPE.fiber
                    result.radii[t][n_other_agents + n] = 1.0
                    fiber_info = line.split()[2].split(":")
                    # unique instance ID
                    raw_uid = int(fiber_info[1])
                    if raw_uid not in uids:
                        uid = raw_uid
                        while uid in used_unique_IDs:
                            uid += 1
                        uids[raw_uid] = uid
                        used_unique_IDs.append(uid)
                    result.unique_ids[t][n_other_agents + n] = uids[raw_uid]
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
                    result.type_ids[t][n_other_agents + n] = tid
                elif "end" in line:
                    # end of frame
                    result.n_subpoints[t][n_other_agents + n] = s + 1
                    result.n_agents[t] += n + 1
                continue
            # each fiber point
            s += 1
            columns = line.split()
            result.subpoints[t][n_other_agents + n][s] = scale_factor * np.array(
                [float(columns[1]), float(columns[2]), float(columns[3])]
            )
        return (result, agent_types, used_unique_IDs)

    def _parse_others(
        self,
        object_type: str,
        data_lines: List[str],
        scale_factor: float,
        object_info: CytosimObjectInfo,
        result: AgentData,
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
            result.times.size > 0 and float(result.times[1]) < sys.float_info.epsilon
        )
        types = {}
        uids = {}
        for line in data_lines:
            if self._ignore_line(line):
                continue
            if line[0] == "%":
                if "frame" in line:
                    # start of frame
                    if t >= 0:
                        result.n_agents[t] += n + 1
                        result.viz_types[t][n_other_agents : n_other_agents + n + 1] = (
                            n + 1
                        ) * [VIZ_TYPE.default]
                    t += 1
                    n_other_agents = int(result.n_agents[t])
                    n = -1
                elif "time" in line and parse_time:
                    # time metadata
                    result.times[t] = float(line.split()[2])
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
            result.unique_ids[t][n_other_agents + n] = uids[raw_uid]
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
            result.type_ids[t][n_other_agents + n] = tid
            # position
            result.positions[t][n_other_agents + n] = scale_factor * (
                np.array(
                    [
                        float(columns[object_info.position_indices[0]]),
                        float(columns[object_info.position_indices[1]]),
                        float(columns[object_info.position_indices[2]]),
                    ]
                )
            )
            # radius
            result.radii[t][n_other_agents + n] = (
                (scale_factor * float(object_info.agents[raw_tid].radius))
                if raw_tid in object_info.agents
                else 1.0
            )
        result.n_agents[t] += n + 1
        result.viz_types[t][n_other_agents : n_other_agents + n + 1] = (n + 1) * [
            VIZ_TYPE.default
        ]
        return (result, agent_types, used_unique_IDs)

    def _read(self, input_data: CytosimData) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """
        # load the data from Cytosim output .txt files
        cytosim_data = {}
        for object_type in input_data.object_info:
            with open(input_data.object_info[object_type].filepath, "r") as myfile:
                cytosim_data[object_type] = myfile.read().split("\n")
        # parse
        (totalSteps, max_agents, max_subpoints) = self._parse_data_dimensions(
            cytosim_data
        )
        agent_data = AgentData(
            times=np.zeros(totalSteps),
            n_agents=np.zeros(totalSteps),
            viz_types=np.zeros((totalSteps, max_agents)),
            unique_ids=np.zeros((totalSteps, max_agents)),
            types=None,
            positions=np.zeros((totalSteps, max_agents, 3)),
            radii=np.ones((totalSteps, max_agents)),
            n_subpoints=np.zeros((totalSteps, max_agents)),
            subpoints=np.zeros((totalSteps, max_agents, max_subpoints, 3)),
            draw_fiber_points=input_data.draw_fiber_points,
        )
        agent_data.type_ids = np.zeros((totalSteps, max_agents))
        agent_types = {}
        uids = []
        for object_type in input_data.object_info:
            if "fiber" not in object_type:
                agent_data, agent_types, uids = self._parse_others(
                    object_type,
                    cytosim_data[object_type],
                    input_data.scale_factor,
                    input_data.object_info[object_type],
                    agent_data,
                    agent_types,
                    uids,
                )
            else:
                agent_data, agent_types, uids = self._parse_fibers(
                    cytosim_data[object_type],
                    input_data.scale_factor,
                    agent_data,
                    agent_types,
                    uids,
                )
        # shape data
        simularium_data = {}
        # trajectory info
        simularium_data["trajectoryInfo"] = {
            "version": 1,
            "timeStepSize": (
                float(agent_data.times[1] - agent_data.times[0])
                if totalSteps > 1
                else 0.0
            ),
            "totalSteps": totalSteps,
            "size": {
                "x": input_data.scale_factor * float(input_data.box_size[0]),
                "y": input_data.scale_factor * float(input_data.box_size[1]),
                "z": input_data.scale_factor * float(input_data.box_size[2]),
            },
            "typeMapping": {},
        }
        for tid in agent_types:
            s = str(tid)
            object_type = agent_types[tid]["object_type"]
            raw_id = agent_types[tid]["raw_id"]
            if raw_id in input_data.object_info[object_type].agents:
                simularium_data["trajectoryInfo"]["typeMapping"][s] = {
                    "name": input_data.object_info[object_type].agents[raw_id].name
                }
            else:
                simularium_data["trajectoryInfo"]["typeMapping"][s] = {
                    "name": (
                        object_type[:-1] if object_type.endswith("s") else object_type
                    )
                    + str(raw_id)
                }
        # spatial data
        simularium_data["spatialData"] = {
            "version": 1,
            "msgType": 1,
            "bundleStart": 0,
            "bundleSize": totalSteps,
            "bundleData": self._get_spatial_bundle_data_subpoints(agent_data, uids),
        }
        # plot data
        simularium_data["plotData"] = {
            "version": 1,
            "data": input_data.plots,
        }
        return simularium_data
