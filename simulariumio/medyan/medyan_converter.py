#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Callable, Tuple
import math

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import (
    TrajectoryData,
    AgentData,
    UnitData,
    DimensionData,
    DisplayData,
)
from ..constants import (
    VIZ_TYPE,
    DISPLAY_TYPE,
    VALUES_PER_3D_POINT,
    SUBPOINT_VALUES_PER_ITEM,
)
from ..exceptions import InputDataError
from .medyan_data import MedyanData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MedyanConverter(TrajectoryConverter):
    def __init__(
        self,
        input_data: MedyanData,
        progress_callback: Callable[[float], None] = None,
        callback_interval: float = 10,
    ):
        """
        This object reads simulation trajectory outputs
        from MEDYAN (http://medyan.org/)
        and plot data and writes them in the JSON format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : MedyanData
            An object containing info for reading
            MEDYAN simulation trajectory outputs and plot data
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
    def _draw_endpoints(line: str, object_type: str, input_data: MedyanData) -> bool:
        """
        Parse a line of a MEDYAN snapshot.traj output file
        and determine whether to also draw the endpoints as spheres
        """
        if object_type == "motor" or object_type == "linker":
            type_name = MedyanConverter._get_display_type_name(
                line, object_type, input_data
            )
            if type_name in input_data.agents_with_endpoints:
                return True
        return False

    @staticmethod
    def _get_display_type_name(
        line: str, object_type: str, input_data: MedyanData
    ) -> bool:
        """
        Parse a line of a MEDYAN snapshot.traj output file
        and return the type name to display for this agent type
        """
        raw_tid = int(line.split()[2])
        if raw_tid not in input_data.display_data[object_type]:
            display_name = object_type + str(raw_tid)
            input_data.display_data[object_type][raw_tid] = DisplayData(
                name=display_name,
                display_type=DISPLAY_TYPE.FIBER,
            )
            return display_name
        else:
            return input_data.display_data[object_type][raw_tid].name

    @staticmethod
    def _parse_data_dimensions(
        lines: List[str], input_data: MedyanData
    ) -> DimensionData:
        """
        Parse a MEDYAN snapshot.traj output file to get the max numbers
        of subpoints per agent and agents per timestep, and number of timesteps
        """
        result = DimensionData(0, 0)
        agents = 0
        at_frame_start = True
        for line in lines:
            if len(line) < 1:
                at_frame_start = True
                continue
            if at_frame_start:
                # start of timestep
                cols = line.split()
                if agents > result.max_agents:
                    result.max_agents = agents
                agents = int(cols[2]) + int(cols[3]) + int(cols[4])
                result.total_steps += 1
                at_frame_start = False
            elif "FILAMENT" in line or "LINKER" in line or "MOTOR" in line:
                # start of object
                if "FILAMENT" in line:
                    object_type = "filament"
                elif "LINKER" in line:
                    object_type = "linker"
                else:
                    object_type = "motor"
                if MedyanConverter._draw_endpoints(line, object_type, input_data):
                    agents += 2
                if "FILAMENT" in line:
                    # start of filament
                    # filaments N xyz points = 3 * N subpoints
                    cols = line.split()
                    subpoints = SUBPOINT_VALUES_PER_ITEM(DISPLAY_TYPE.FIBER) * int(
                        cols[3]
                    )
                    if result.max_subpoints < subpoints:
                        result.max_subpoints = subpoints
                else:
                    # start of linker or motor
                    # all linkers and motors have 2 xyz points = 6 subpoints
                    if result.max_subpoints < 2 * SUBPOINT_VALUES_PER_ITEM(
                        DISPLAY_TYPE.FIBER
                    ):
                        result.max_subpoints = 2 * SUBPOINT_VALUES_PER_ITEM(
                            DISPLAY_TYPE.FIBER
                        )
        if agents > result.max_agents:
            result.max_agents = agents
        return result

    def _get_trajectory_data(
        self,
        input_data: MedyanData,
    ) -> Tuple[AgentData, float]:
        """
        Parse a MEDYAN snapshot.traj output file to get agents
        """
        try:
            lines = input_data.snapshot_file.get_contents().split("\n")
            dimensions = MedyanConverter._parse_data_dimensions(lines, input_data)
        except Exception as e:
            raise InputDataError(f"Error reading input medyan data: {e}")

        result = AgentData.from_dimensions(dimensions)
        time_index = -1
        at_frame_start = True
        parsing_object = False
        uids = {
            "filament": {},
            "linker": {},
            "motor": {},
        }
        last_uid = 0
        tids = {
            "filament": {},
            "linker": {},
            "motor": {},
        }
        last_tid = 0
        object_type = ""
        draw_endpoints = False
        line_count = 0

        for line in lines:
            if len(line) < 1:
                at_frame_start = True
                continue
            cols = line.split()
            if at_frame_start:
                # start of timestep
                time_index += 1
                agent_index = 0
                result.times[time_index] = float(cols[1])
                result.n_agents[time_index] = int(cols[2]) + int(cols[3]) + int(cols[4])
                at_frame_start = False
            if "FILAMENT" in line or "LINKER" in line or "MOTOR" in line:
                # start of object
                result.viz_types[time_index][agent_index] = VIZ_TYPE.FIBER
                if "FILAMENT" in line:
                    object_type = "filament"
                elif "LINKER" in line:
                    object_type = "linker"
                else:
                    object_type = "motor"
                draw_endpoints = MedyanConverter._draw_endpoints(
                    line, object_type, input_data
                )
                # unique instance ID
                raw_uid = int(cols[1])
                if raw_uid not in uids[object_type]:
                    uids[object_type][raw_uid] = last_uid
                    last_uid += 1 if not draw_endpoints else 3
                result.unique_ids[time_index][agent_index] = uids[object_type][raw_uid]
                # type ID
                raw_tid = int(cols[2])
                if raw_tid not in tids[object_type]:
                    tids[object_type][raw_tid] = last_tid
                    last_tid += 1
                # type name
                result.types[time_index].append(
                    MedyanConverter._get_display_type_name(
                        line, object_type, input_data
                    )
                )
                # radius
                radius = (
                    input_data.display_data[object_type][raw_tid].radius
                    if raw_tid in input_data.display_data[object_type]
                    and input_data.display_data[object_type][raw_tid].radius is not None
                    else 1.0
                )
                result.radii[time_index][agent_index] = radius
                if object_type == "filament":
                    result.n_subpoints[time_index][agent_index] = int(
                        cols[3]
                    ) * SUBPOINT_VALUES_PER_ITEM(DISPLAY_TYPE.FIBER)
                else:
                    result.n_subpoints[time_index][
                        agent_index
                    ] = 2 * SUBPOINT_VALUES_PER_ITEM(DISPLAY_TYPE.FIBER)
                # draw endpoints?
                if draw_endpoints:
                    for i in range(2):
                        result.viz_types[time_index][
                            agent_index + i + 1
                        ] = VIZ_TYPE.DEFAULT
                        result.unique_ids[time_index][agent_index + i + 1] = (
                            uids[object_type][raw_uid] + i + 1
                        )
                        end_type = result.types[time_index][agent_index] + " End"
                        result.types[time_index].append(end_type)
                        if end_type not in result.display_data:
                            result.display_data[end_type] = DisplayData(
                                name=end_type,
                                display_type=DISPLAY_TYPE.SPHERE,
                            )
                        result.radii[time_index][agent_index + i + 1] = 2 * radius
                parsing_object = True
            elif parsing_object:
                # object coordinates
                for i in range(len(cols)):
                    result.subpoints[time_index][agent_index][i] = float(cols[i])
                    if draw_endpoints:
                        endpoint_index = math.floor(i / float(VALUES_PER_3D_POINT))
                        dim_index = i % VALUES_PER_3D_POINT
                        result.positions[time_index][agent_index + endpoint_index + 1][
                            dim_index
                        ] = float(cols[i])

                parsing_object = False
                agent_index += 1
                if draw_endpoints:
                    agent_index += 2
                    result.n_agents[time_index] += 2
            line_count += 1
            self.check_report_progress(line_count / len(lines))

        result.n_timesteps = time_index + 1

        if input_data.center:
            return TrajectoryConverter.center_and_scale_agent_data(
                result, input_data.meta_data.scale_factor
            )

        return TrajectoryConverter.scale_agent_data(
            result, input_data.meta_data.scale_factor
        )

    def _read(self, input_data: MedyanData) -> TrajectoryData:
        """
        Return an object containing the data shaped for Simularium format
        """
        print("Reading MEDYAN Data -------------")
        agent_data, scale_factor = self._get_trajectory_data(input_data)
        # get display data (geometry and color)
        for object_type in input_data.display_data:
            for tid in input_data.display_data[object_type]:
                display_data = input_data.display_data[object_type][tid]
                if (
                    display_data.display_type != DISPLAY_TYPE.NONE
                    and display_data.display_type != DISPLAY_TYPE.FIBER
                ):
                    display_data.display_type = DISPLAY_TYPE.FIBER
                    print(
                        f"{display_data.name} display type of "
                        f"{display_data.display_type.value} was changed to FIBER"
                    )
                agent_data.display_data[display_data.name] = display_data
        input_data.meta_data.scale_factor = scale_factor
        input_data.meta_data._set_box_size()
        return TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=UnitData("s"),
            spatial_units=UnitData("nm", 1.0 / scale_factor),
            plots=input_data.plots,
        )
