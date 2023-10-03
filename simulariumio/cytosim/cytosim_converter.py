#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List, Tuple, Callable
import numpy as np

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import (
    TrajectoryData,
    AgentData,
    UnitData,
    DimensionData,
    DisplayData,
)
from ..constants import VIZ_TYPE, DISPLAY_TYPE, SUBPOINT_VALUES_PER_ITEM
from ..exceptions import InputDataError
from .cytosim_data import CytosimData
from .cytosim_object_info import CytosimObjectInfo

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CytosimConverter(TrajectoryConverter):
    def __init__(
        self,
        input_data: CytosimData,
        progress_callback: Callable[[float], None] = None,
        callback_interval: float = 10,
    ):
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
        progress_callback : Callable[[float], None] (optional)
            Callback function that accepts 1 float argument and returns None
            which will be called at a given progress interval, determined by
            callback_interval requested, providing the current percent progress
            Default: None
        callback_interval : float (optional)
            If a progress_callback was provided, the period between updates
            to be sent to the callback, in seconds
            Default: 10
        """
        super().__init__(input_data, progress_callback, callback_interval)
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
                subpoints += SUBPOINT_VALUES_PER_ITEM(DISPLAY_TYPE.FIBER)
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
    def _get_display_type_name_from_raw(raw_tid, object_type, display_data):
        """
        Get the display type_name given the type ID from Cytosim
        and the Cytosim object type
        If there is no DisplayData for this type, add it
        """
        if raw_tid not in display_data:
            type_name = object_type[:-1] + str(raw_tid)
            display_data[raw_tid] = DisplayData(
                name=type_name,
                display_type=DISPLAY_TYPE.FIBER
                if "fiber" in object_type
                else DISPLAY_TYPE.SPHERE,
            )
        else:
            type_name = display_data[raw_tid].name
        return type_name

    @staticmethod
    def _parse_object(
        object_type: str,
        data_columns: List[str],
        time_index: int,
        object_info: CytosimObjectInfo,
        result: AgentData,
        uids: Dict[int, int],
        used_unique_IDs: List[int],
    ) -> Tuple[AgentData, Dict[int, int], List[int], float]:
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
            CytosimConverter._get_display_type_name_from_raw(
                raw_tid, object_type, object_info.display_data
            )
        )
        # radius
        result.radii[time_index][agent_index] = (
            float(object_info.display_data[raw_tid].radius)
            if raw_tid in object_info.display_data
            and object_info.display_data[raw_tid].radius is not None
            else 1.0
        )
        return (result, uids, used_unique_IDs)

    def _parse_objects(
        self,
        object_type: str,
        data_lines: List[str],
        object_info: CytosimObjectInfo,
        result: AgentData,
        used_unique_IDs: List[int],
        overall_line: int,
        total_lines: int,
        scale_factor: float = None,
    ) -> Tuple[Dict[str, Any], List[int], int]:
        """
        Parse a Cytosim output file containing objects
        (fibers, solids, singles, or couples) to get agents
        """
        time_index = -1
        uids = {}
        is_fiber = "fiber" in object_type
        for line in data_lines:
            overall_line += 1
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
                    (
                        result,
                        uids,
                        used_unique_IDs,
                    ) = CytosimConverter._parse_object(
                        object_type,
                        columns,
                        time_index,
                        object_info,
                        result,
                        uids,
                        used_unique_IDs,
                    )
                    result.n_agents[time_index] += 1
                continue
            elif is_fiber:
                # each fiber point
                agent_index = int(result.n_agents[time_index] - 1)
                subpoint_index = int(result.n_subpoints[time_index][agent_index])
                # position
                result.subpoints[time_index][agent_index][
                    subpoint_index : subpoint_index
                    + SUBPOINT_VALUES_PER_ITEM(DISPLAY_TYPE.FIBER)
                ] = np.array(
                    [
                        float(columns[1].strip("+,")),
                        float(columns[2].strip("+,")),
                        float(columns[3].strip("+,")),
                    ]
                )
                result.n_subpoints[time_index][agent_index] += SUBPOINT_VALUES_PER_ITEM(
                    DISPLAY_TYPE.FIBER
                )
            else:
                # each non-fiber object
                (
                    result,
                    uids,
                    used_unique_IDs,
                ) = CytosimConverter._parse_object(
                    object_type,
                    columns,
                    time_index,
                    object_info,
                    result,
                    uids,
                    used_unique_IDs,
                )
                # position
                result.positions[time_index][
                    int(result.n_agents[time_index])
                ] = np.array(
                    [
                        float(columns[object_info.position_indices[0]].strip("+,")),
                        float(columns[object_info.position_indices[1]].strip("+,")),
                        float(columns[object_info.position_indices[2]].strip("+,")),
                    ]
                )
                result.n_agents[time_index] += 1
            self.check_report_progress(overall_line / total_lines)
        result, scale_factor = TrajectoryConverter.scale_agent_data(
            result, scale_factor
        )
        result.n_timesteps = time_index + 1
        return (result, used_unique_IDs, overall_line, scale_factor)

    def _read(self, input_data: CytosimData) -> TrajectoryData:
        """
        Return a TrajectoryData object containing the CytoSim data
        """
        print("Reading Cytosim Data -------------")
        # load the data from Cytosim output .txt files
        cytosim_data = {}
        try:
            for object_type in input_data.object_info:
                cytosim_data[object_type] = (
                    input_data.object_info[object_type]
                    .cytosim_file.get_contents()
                    .split("\n")
                )
        except Exception as e:
            raise InputDataError(f"Error reading input cytosim file: {e}")

        # parse
        dimensions = CytosimConverter._parse_dimensions(cytosim_data)
        agent_data = AgentData.from_dimensions(dimensions)
        agent_data.draw_fiber_points = input_data.draw_fiber_points
        overall_line = 0
        total_lines = sum(
            len(cytosim_data[object_type]) for object_type in input_data.object_info
        )

        uids = []
        for object_type in input_data.object_info:
            try:
                (agent_data, uids, overall_line, scale_factor) = self._parse_objects(
                    object_type,
                    cytosim_data[object_type],
                    input_data.object_info[object_type],
                    agent_data,
                    uids,
                    overall_line,
                    total_lines,
                    input_data.meta_data.scale_factor,
                )
            except Exception as e:
                raise InputDataError(f"Error reading input cytosim data: {e}")
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
        input_data.meta_data.scale_factor = scale_factor
        input_data.meta_data._set_box_size()
        return TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=UnitData("s"),
            spatial_units=UnitData("µm", 1.0 / scale_factor),
            plots=input_data.plots,
        )
