#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List, Tuple

import numpy as np

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, UnitData, DimensionData
from ..constants import VIZ_TYPE, DISPLAY_TYPE
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

    @staticmethod
    def _ignore_line(line: str) -> bool:
        """
        if the line doesn't have any data, it can be ignored
        """
        return len(line) < 1 or line[0:7] == "warning" or "report" in line

    @staticmethod
    def _parse_object_dimensions(
        data_lines: List[str],
        is_fiber: bool,
    ) -> DimensionData:
        """
        Parse a Cytosim output file containing objects
        (fibers, solids, singles, or couples) to get the number
        of subpoints per agent per timestep
        """
        result = DimensionData(0, 0)
        agents = 0
        subpoints = 0
        for line in data_lines:
            if CytosimConverter._ignore_line(line):
                continue
            if line[0] == "%":
                if "frame" in line:
                    if agents > result.max_agents:
                        result.max_agents = agents
                    agents = 0
                    result.total_steps += 1
                elif "fiber" in line:
                    if subpoints > result.max_subpoints:
                        result.max_subpoints = subpoints
                    subpoints = 0
                    agents += 1
                continue
            if is_fiber:
                subpoints += 1
            else:
                agents += 1
        if agents > result.max_agents:
            result.max_agents = agents
        if subpoints > result.max_subpoints:
            result.max_subpoints = subpoints
        return result

    @staticmethod
    def _parse_dimensions(cytosim_data: Dict[str, List[str]]) -> DimensionData:
        """
        Parse Cytosim output files to get the total steps,
        maximum agents per timestep, and maximum subpoints per agent
        """
        result = DimensionData(0, 0)
        for object_type in cytosim_data:
            object_dimensions = CytosimConverter._parse_object_dimensions(
                cytosim_data[object_type],
                "fiber" in object_type,
            )
            result = result.add(object_dimensions)
        return result

    @staticmethod
    def _parse_object(
        object_type: str,
        data_columns: List[str],
        time_index: int,
        scale_factor: float,
        object_info: CytosimObjectInfo,
        result: AgentData,
        uids: Dict[int, int],
        used_unique_IDs: List[int],
    ) -> Tuple[AgentData, Dict[int, int], List[int]]:
        """
        Parse an object from Cytosim
        """
        agent_index = int(result.n_agents[time_index])
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
            object_info.display_data[raw_tid].name
            if raw_tid in object_info.display_data
            else object_type[:-1] + str(raw_tid)
        )
        # radius
        result.radii[time_index][agent_index] = scale_factor * (
            float(object_info.display_data[raw_tid].radius)
            if raw_tid in object_info.display_data
            and object_info.display_data[raw_tid].radius is not None
            else 1.0
        )
        return (result, uids, used_unique_IDs)

    @staticmethod
    def _parse_objects(
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
        uids = {}
        is_fiber = "fiber" in object_type
        for line in data_lines:
            if CytosimConverter._ignore_line(line):
                continue
            columns = line.split()
            if line[0] == "%":
                if "frame" in line:
                    # start of frame
                    time_index += 1
                elif "time" in line:
                    # time metadata
                    result.times[time_index] = float(columns[2])
                elif "fiber" in columns[1]:
                    # start of fiber object
                    (result, uids, used_unique_IDs,) = CytosimConverter._parse_object(
                        object_type,
                        columns,
                        time_index,
                        scale_factor,
                        object_info,
                        result,
                        uids,
                        used_unique_IDs,
                    )
                    result.n_agents[time_index] += 1
                continue
            elif is_fiber:
                # each fiber point
                subpoint_index = int(
                    result.n_subpoints[time_index][int(result.n_agents[time_index] - 1)]
                )
                # position
                result.subpoints[time_index][int(result.n_agents[time_index] - 1)][
                    subpoint_index
                ] = scale_factor * np.array(
                    [
                        float(columns[1].strip("+,")),
                        float(columns[2].strip("+,")),
                        float(columns[3].strip("+,")),
                    ]
                )
                result.n_subpoints[time_index][
                    int(result.n_agents[time_index] - 1)
                ] += 1
            else:
                # each non-fiber object
                (result, uids, used_unique_IDs,) = CytosimConverter._parse_object(
                    object_type,
                    columns,
                    time_index,
                    scale_factor,
                    object_info,
                    result,
                    uids,
                    used_unique_IDs,
                )
                # position
                result.positions[time_index][
                    int(result.n_agents[time_index])
                ] = scale_factor * (
                    np.array(
                        [
                            float(columns[object_info.position_indices[0]].strip("+,")),
                            float(columns[object_info.position_indices[1]].strip("+,")),
                            float(columns[object_info.position_indices[2]].strip("+,")),
                        ]
                    )
                )
                result.n_agents[time_index] += 1
        result.n_timesteps = time_index + 1
        return (result, used_unique_IDs)

    @staticmethod
    def _read(input_data: CytosimData) -> TrajectoryData:
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
        dimensions = CytosimConverter._parse_dimensions(cytosim_data)
        agent_data = AgentData.from_dimensions(dimensions)
        agent_data.draw_fiber_points = input_data.draw_fiber_points
        uids = []
        for object_type in input_data.object_info:
            agent_data, uids = CytosimConverter._parse_objects(
                object_type,
                cytosim_data[object_type],
                input_data.meta_data.scale_factor,
                input_data.object_info[object_type],
                agent_data,
                uids,
            )
        # get display data (geometry and color)
        for object_type in input_data.object_info:
            for tid in input_data.object_info[object_type].display_data:
                display_data = input_data.object_info[object_type].display_data[tid]
                if "fiber" in object_type and (
                    display_data.display_type != DISPLAY_TYPE.NONE
                    and display_data.display_type != DISPLAY_TYPE.FIBER
                ):
                    display_data.display_type = DISPLAY_TYPE.FIBER
                    print(
                        f"{display_data.name} display type of "
                        f"{display_data.display_type.value} was changed to FIBER"
                    )
                agent_data.display_data[display_data.name] = display_data
        # create TrajectoryData
        input_data.meta_data._set_box_size()
        return TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=UnitData("s"),
            spatial_units=UnitData("µm", 1.0 / input_data.meta_data.scale_factor),
            plots=input_data.plots,
        )
