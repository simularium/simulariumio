#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List, Tuple
import sys

import numpy as np

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, UnitData, MetaData
from ..constants import VIZ_TYPE, FIBER_AGENT_BUFFER_DIMENSIONS
from .cytosim_data import CytosimData
from .cytosim_object_info import CytosimObjectInfo

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CytosimConverter(TrajectoryConverter):
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

    def _parse_object(
        self,
        object_type: str,
        data_columns: List[str],
        time_index: int,
        agent_index: int,
        scale_factor: float,
        object_info: CytosimObjectInfo,
        result: AgentData,
        uids: Dict[int, int],
        used_unique_IDs: List[int],
    ) -> Tuple[AgentData, Dict[int, int], List[int]]:
        """
        Parse an object from Cytosim
        """
        result = result.check_increase_buffer_size(agent_index, axis=1)
        # viz type and raw IDs
        if "fiber" in object_type:
            result.viz_types[time_index][agent_index] = VIZ_TYPE.FIBER
            fiber_info = data_columns[2].split(":")
            raw_uid = int(fiber_info[1])
            raw_tid = int(fiber_info[0][1:])
        else:
            result.viz_types[time_index][agent_index] = VIZ_TYPE.DEFAULT
            raw_uid = int(data_columns[1].strip("+,"))
            raw_tid = int(data_columns[0].strip("+,"))
        # unique instance ID
        if raw_uid not in uids:
            uid = raw_uid
            while uid in used_unique_IDs:
                uid += 1
            uids[raw_uid] = uid
            used_unique_IDs.append(uid)
        result.unique_ids[time_index][agent_index] = uids[raw_uid]
        # type name
        result.types[time_index].append(
            object_info.agents[raw_tid].name
            if raw_tid in object_info.agents
            else object_type[:-1] + str(raw_tid)
        )
        # radius
        result.radii[time_index][agent_index] = (
            (scale_factor * float(object_info.agents[raw_tid].radius))
            if raw_tid in object_info.agents
            else 1.0
        )
        return (result, uids, used_unique_IDs)

    def _parse_objects(
        self,
        object_type: str,
        data_lines: List[str],
        scale_factor: float,
        object_info: CytosimObjectInfo,
        result: AgentData,
        used_unique_IDs: List[int],
    ) -> Tuple[Dict[str, Any], List[int]]:
        """
        Parse a Cytosim output file containing objects
        (fibers, solids, singles, or couples) to get agents
        """
        time_index = -1
        agent_index = -1
        subpoint_index = -1
        n_other_agents = 0
        parse_time = (
            result.times.size > 1 and float(result.times[1]) < sys.float_info.epsilon
        )
        uids = {}
        is_fiber = "fiber" in object_type
        for line in data_lines:
            if self._ignore_line(line):
                continue
            columns = line.split()
            if line[0] == "%":
                if "frame" in line:
                    # start of frame
                    time_index += 1
                    result = result.check_increase_buffer_size(time_index, axis=0)
                    n_other_agents = int(result.n_agents[time_index])
                    agent_index = -1
                elif parse_time and "time" in line:
                    # time metadata
                    result.times[time_index] = float(columns[2])
                elif "fiber" in columns[1]:
                    # start of fiber object
                    if agent_index >= 0 and subpoint_index >= 0:
                        result.n_subpoints[time_index][n_other_agents + agent_index] = (
                            subpoint_index + 1
                        )
                    agent_index += 1
                    subpoint_index = -1
                    result, uids, used_unique_IDs = self._parse_object(
                        object_type,
                        columns,
                        time_index,
                        n_other_agents + agent_index,
                        scale_factor,
                        object_info,
                        result,
                        uids,
                        used_unique_IDs,
                    )
                elif "end" in line:
                    # end of frame
                    if is_fiber:
                        result.n_subpoints[time_index][n_other_agents + agent_index] = (
                            subpoint_index + 1
                        )
                    result.n_agents[time_index] += agent_index + 1
                continue
            elif is_fiber:
                # each fiber point
                subpoint_index += 1
                result = result.check_increase_buffer_size(subpoint_index, axis=2)
                # position
                result.subpoints[time_index][n_other_agents + agent_index][
                    subpoint_index
                ] = scale_factor * np.array(
                    [
                        float(columns[1].strip("+,")),
                        float(columns[2].strip("+,")),
                        float(columns[3].strip("+,")),
                    ]
                )
            else:
                # each non-fiber object
                agent_index += 1
                result, uids, used_unique_IDs = self._parse_object(
                    object_type,
                    columns,
                    time_index,
                    n_other_agents + agent_index,
                    scale_factor,
                    object_info,
                    result,
                    uids,
                    used_unique_IDs,
                )
                # position
                result.positions[time_index][
                    n_other_agents + agent_index
                ] = scale_factor * (
                    np.array(
                        [
                            float(columns[object_info.position_indices[0]].strip("+,")),
                            float(columns[object_info.position_indices[1]].strip("+,")),
                            float(columns[object_info.position_indices[2]].strip("+,")),
                        ]
                    )
                )
        result.n_timesteps = time_index + 1
        return (result, used_unique_IDs)

    def _read(self, input_data: CytosimData) -> TrajectoryData:
        """
        Return a TrajectoryData object containing the CytoSim data
        """
        print("Reading Cytosim Data -------------")
        # load the data from Cytosim output .txt files
        cytosim_data = {}
        for object_type in input_data.object_info:
            with open(input_data.object_info[object_type].filepath, "r") as myfile:
                cytosim_data[object_type] = myfile.read().split("\n")
        # parse
        agent_data = AgentData.from_dimensions(FIBER_AGENT_BUFFER_DIMENSIONS)
        agent_data.draw_fiber_points = input_data.draw_fiber_points
        uids = []
        for object_type in input_data.object_info:
            agent_data, uids = self._parse_objects(
                object_type,
                cytosim_data[object_type],
                input_data.meta_data.scale_factor,
                input_data.object_info[object_type],
                agent_data,
                uids,
            )
        # create TrajectoryData
        return TrajectoryData(
            meta_data=MetaData(
                box_size=input_data.meta_data.scale_factor
                * input_data.meta_data.box_size,
                camera_defaults=input_data.meta_data.camera_defaults,
            ),
            agent_data=agent_data,
            time_units=UnitData("s"),
            spatial_units=UnitData("µm", 1.0 / input_data.meta_data.scale_factor),
            plots=input_data.plots,
        )
