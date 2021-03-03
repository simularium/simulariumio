#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List, Tuple
import sys

import numpy as np

from ..custom_converter import CustomConverter
from ..data_objects import CustomData, AgentData, UnitData
from ..exceptions import DataError
from ..constants import VIZ_TYPE
from .cytosim_data import CytosimData
from .cytosim_object_info import CytosimObjectInfo

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CytosimConverter(CustomConverter):
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

    def _parse_object_type_dimensions(
        self,
        data_lines: List[str],
        is_fiber: bool,
    ) -> Tuple[List[int], int]:
        """
        Parse a Cytosim output file containing objects
        (fibers, solids, singles, or couples) to get the number
        of subpoints per agent per timestep
        """
        result = []
        t = -1
        s = 0
        max_subpoints = 0
        for line in data_lines:
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
            if is_fiber:
                s += 1
            else:
                result[t] += 1
        if s > max_subpoints:
            max_subpoints = s
        return (result, max_subpoints)

    def _parse_dimensions(self, cytosim_data: Dict[str, List[str]]) -> Tuple[int]:
        """
        Parse Cytosim output files to get the total steps,
        maximum agents per timestep, and maximum subpoints per agent
        """
        dimensions = []
        max_subpoints = 0
        for object_type in cytosim_data:
            dims, n_subpoints = self._parse_object_type_dimensions(
                cytosim_data[object_type],
                "fiber" in object_type,
            )
            if n_subpoints > max_subpoints:
                max_subpoints = n_subpoints
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

    def _parse_object(
        self,
        object_type: str,
        data_columns: List[str],
        t: int,
        n: int,
        scale_factor: float,
        object_info: CytosimObjectInfo,
        result: AgentData,
        uids: Dict[int, int],
        used_unique_IDs: List[int],
        types: Dict[int, int],
        used_type_IDs: List[int],
    ) -> [AgentData, Dict[int, int], List[int], Dict[int, int], List[int]]:
        """"""
        if "fiber" in object_type:
            result.viz_types[t][n] = VIZ_TYPE.fiber
            fiber_info = data_columns[2].split(":")
            raw_uid = int(fiber_info[1])
            raw_tid = int(fiber_info[0][1:])
        else:
            result.viz_types[t][n] = VIZ_TYPE.default
            raw_uid = int(data_columns[1].strip("+,"))
            raw_tid = int(data_columns[0].strip("+,"))
        # unique instance ID
        if raw_uid not in uids:
            uid = raw_uid
            while uid in used_unique_IDs:
                uid += 1
            uids[raw_uid] = uid
            used_unique_IDs.append(uid)
        result.unique_ids[t][n] = uids[raw_uid]
        # type ID
        if raw_tid not in types:
            tid = raw_tid
            while tid in used_type_IDs:
                tid += 1
            types[raw_tid] = tid
            used_type_IDs.append(tid)
        else:
            tid = types[raw_tid]
        result.type_ids[t][n] = tid
        # type name
        while n >= len(result.types[t]):
            result.types[t].append("")
        if raw_tid in object_info.agents:
            result.types[t][n] = object_info.agents[raw_tid].name
        else:
            result.types[t][n] = object_type[:-1] + str(raw_tid)
        # radius
        result.radii[t][n] = (
            (scale_factor * float(object_info.agents[raw_tid].radius))
            if raw_tid in object_info.agents
            else 1.0
        )
        return (result, uids, used_unique_IDs, types, used_type_IDs)

    def _parse_objects(
        self,
        object_type: str,
        data_lines: List[str],
        scale_factor: float,
        object_info: CytosimObjectInfo,
        result: AgentData,
        used_unique_IDs: List[int],
        used_type_IDs: List[int],
    ) -> Tuple[Dict[str, Any], List[int], List[int]]:
        """
        Parse a Cytosim output file containing objects
        (fibers, solids, singles, or couples) to get agents
        """
        t = -1
        n = -1
        s = -1
        n_other_agents = 0
        parse_time = (
            result.times.size > 1 and float(result.times[1]) < sys.float_info.epsilon
        )
        types = {}
        uids = {}
        is_fiber = "fiber" in object_type
        for line in data_lines:
            if self._ignore_line(line):
                continue
            columns = line.split()
            if line[0] == "%":
                if "frame" in line:
                    # start of frame
                    t += 1
                    n_other_agents = int(result.n_agents[t])
                    n = -1
                elif parse_time and "time" in line:
                    # time metadata
                    result.times[t] = float(columns[2])
                elif "fiber" in columns[1]:
                    # start of fiber object
                    if n >= 0 and s >= 0:
                        result.n_subpoints[t][n_other_agents + n] = s + 1
                    n += 1
                    s = -1
                    (
                        result,
                        uids,
                        used_unique_IDs,
                        types,
                        used_type_IDs,
                    ) = self._parse_object(
                        object_type,
                        columns,
                        t,
                        n_other_agents + n,
                        scale_factor,
                        object_info,
                        result,
                        uids,
                        used_unique_IDs,
                        types,
                        used_type_IDs,
                    )
                elif "end" in line:
                    # end of frame
                    if is_fiber:
                        result.n_subpoints[t][n_other_agents + n] = s + 1
                    result.n_agents[t] += n + 1
                continue
            elif is_fiber:
                # each fiber point
                s += 1
                # position
                result.subpoints[t][n_other_agents + n][s] = scale_factor * np.array(
                    [
                        float(columns[1].strip("+,")),
                        float(columns[2].strip("+,")),
                        float(columns[3].strip("+,")),
                    ]
                )
            else:
                # each non-fiber object
                n += 1
                (
                    result,
                    uids,
                    used_unique_IDs,
                    types,
                    used_type_IDs,
                ) = self._parse_object(
                    object_type,
                    columns,
                    t,
                    n_other_agents + n,
                    scale_factor,
                    object_info,
                    result,
                    uids,
                    used_unique_IDs,
                    types,
                    used_type_IDs,
                )
                # position
                result.positions[t][n_other_agents + n] = scale_factor * (
                    np.array(
                        [
                            float(columns[object_info.position_indices[0]].strip("+,")),
                            float(columns[object_info.position_indices[1]].strip("+,")),
                            float(columns[object_info.position_indices[2]].strip("+,")),
                        ]
                    )
                )
        return (result, used_unique_IDs, used_type_IDs)

    def _read(self, input_data: CytosimData) -> CustomData:
        """
        Return a CustomData object containing the CytoSim data
        """
        print("Reading Cytosim Data -------------")
        # load the data from Cytosim output .txt files
        cytosim_data = {}
        for object_type in input_data.object_info:
            with open(input_data.object_info[object_type].filepath, "r") as myfile:
                cytosim_data[object_type] = myfile.read().split("\n")
        # parse
        (totalSteps, max_agents, max_subpoints) = self._parse_dimensions(cytosim_data)
        agent_data = AgentData(
            times=np.zeros(totalSteps),
            n_agents=np.zeros(totalSteps),
            viz_types=np.zeros((totalSteps, max_agents)),
            unique_ids=np.zeros((totalSteps, max_agents)),
            types=[[] for t in range(totalSteps)],
            positions=np.zeros((totalSteps, max_agents, 3)),
            radii=np.ones((totalSteps, max_agents)),
            n_subpoints=np.zeros((totalSteps, max_agents)),
            subpoints=np.zeros((totalSteps, max_agents, max_subpoints, 3)),
            draw_fiber_points=input_data.draw_fiber_points,
        )
        agent_data.type_ids = np.zeros((totalSteps, max_agents))
        uids = []
        types = []
        for object_type in input_data.object_info:
            agent_data, uids, types = self._parse_objects(
                object_type,
                cytosim_data[object_type],
                input_data.scale_factor,
                input_data.object_info[object_type],
                agent_data,
                uids,
                types,
            )
        # create CustomData
        return CustomData(
            box_size=input_data.scale_factor * input_data.box_size,
            agent_data=agent_data,
            time_units=UnitData("s"),
            spatial_units=UnitData("µm", 1.0 / input_data.scale_factor),
            plots=input_data.plots,
        )
