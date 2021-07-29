#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List
import math

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, UnitData, MetaData, DimensionData
from ..constants import VIZ_TYPE
from .medyan_data import MedyanData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MedyanConverter(TrajectoryConverter):
    def __init__(self, input_data: MedyanData):
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
        """
        self._data = self._read(input_data)

    @staticmethod
    def _draw_endpoints(line: str, object_type: str, input_data: MedyanData) -> bool:
        """
        Parse a line of a MEDYAN snapshot.traj output file
        and use MedyanAgentInfo for that agent type to
        determine whether to also draw the endpoints as spheres
        """
        raw_tid = int(line.split()[2])
        if raw_tid in input_data.agent_info[object_type]:
            return input_data.agent_info[object_type][raw_tid].draw_endpoints
        return False

    @staticmethod
    def _parse_data_dimensions(
        lines: List[str], input_data: MedyanData
    ) -> DimensionData:
        """
        Parse a MEDYAN snapshot.traj output file to get the number
        of subpoints per agent per timestep
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
                    cols = line.split()
                    subpoints = int(cols[3])
                    if result.max_subpoints < subpoints:
                        result.max_subpoints = subpoints
                else:
                    # start of linker or motor
                    if result.max_subpoints < 2:
                        result.max_subpoints = 2
        if agents > result.max_agents:
            result.max_agents = agents
        return result

    @staticmethod
    def _get_trajectory_data(input_data: MedyanData) -> AgentData:
        """
        Parse a MEDYAN snapshot.traj output file to get agents
        """
        with open(input_data.path_to_snapshot, "r") as myfile:
            lines = myfile.read().split("\n")
        dimensions = MedyanConverter._parse_data_dimensions(lines, input_data)
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
                    input_data.agent_info[object_type][raw_tid].name
                    if raw_tid in input_data.agent_info[object_type]
                    else object_type + str(raw_tid)
                )
                # radius
                result.radii[time_index][
                    agent_index
                ] = input_data.meta_data.scale_factor * (
                    input_data.agent_info[object_type][raw_tid].radius
                    if raw_tid in input_data.agent_info[object_type]
                    else 1.0
                )
                if object_type == "filament":
                    result.n_subpoints[time_index][agent_index] = int(cols[3])
                else:
                    result.n_subpoints[time_index][agent_index] = 2
                # draw endpoints?
                if draw_endpoints:
                    for i in range(2):
                        result.viz_types[time_index][
                            agent_index + i + 1
                        ] = VIZ_TYPE.DEFAULT
                        result.unique_ids[time_index][agent_index + i + 1] = (
                            uids[object_type][raw_uid] + i + 1
                        )
                        result.types[time_index].append(
                            result.types[time_index][agent_index]
                        )
                        result.radii[time_index][
                            agent_index + i + 1
                        ] = input_data.meta_data.scale_factor * (
                            input_data.agent_info[object_type][raw_tid].endpoint_radius
                            if raw_tid in input_data.agent_info[object_type]
                            else 1.0
                        )
                parsing_object = True
            elif parsing_object:
                # object coordinates
                for i in range(len(cols)):
                    subpoint_index = math.floor(i / 3)
                    d = i % 3
                    result.subpoints[time_index][agent_index][subpoint_index][
                        d
                    ] = input_data.meta_data.scale_factor * float(cols[i])
                    if draw_endpoints:
                        result.positions[time_index][agent_index + subpoint_index + 1][
                            d
                        ] = input_data.meta_data.scale_factor * float(cols[i])
                parsing_object = False
                agent_index += 1
                if draw_endpoints:
                    agent_index += 2
                    result.n_agents[time_index] += 2
        result.n_timesteps = time_index + 1
        return result

    @staticmethod
    def _read(input_data: MedyanData) -> TrajectoryData:
        """
        Return an object containing the data shaped for Simularium format
        """
        print("Reading MEDYAN Data -------------")
        agent_data = MedyanConverter._get_trajectory_data(input_data)
        time_units = UnitData("s")
        spatial_units = UnitData("nm", 1.0 / input_data.meta_data.scale_factor)
        return TrajectoryData(
            meta_data=MetaData(
                box_size=input_data.meta_data.scale_factor
                * input_data.meta_data.box_size,
                camera_defaults=input_data.meta_data.camera_defaults,
            ),
            agent_data=agent_data,
            time_units=time_units,
            spatial_units=spatial_units,
            plots=input_data.plots,
        )
