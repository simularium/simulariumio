#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List
import math

import numpy as np

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, UnitData
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

    def _draw_endpoints(
        self, line: str, object_type: str, input_data: MedyanData
    ) -> bool:
        """
        Parse a line of a MEDYAN snapshot.traj output file
        and use MedyanAgentInfo for that agent type to
        determine whether to also draw the endpoints as spheres
        """
        raw_tid = int(line.split()[2])
        if raw_tid in input_data.agent_info[object_type]:
            return input_data.agent_info[object_type][raw_tid].draw_endpoints
        return False

    def _parse_data_dimensions(
        self, lines: List[str], input_data: MedyanData
    ) -> List[int]:
        """
        Parse a MEDYAN snapshot.traj output file to get the number
        of subpoints per agent per timestep
        """
        totalSteps = 0
        max_agents = 0
        max_subpoints = 0
        n = 0
        at_frame_start = True
        for line in lines:
            if len(line) < 1:
                at_frame_start = True
                continue
            if at_frame_start:
                # start of timestep
                cols = line.split()
                if n > max_agents:
                    max_agents = n
                n = int(cols[2]) + int(cols[3]) + int(cols[4])
                totalSteps += 1
                at_frame_start = False
            elif "FILAMENT" in line or "LINKER" in line or "MOTOR" in line:
                # start of object
                if "FILAMENT" in line:
                    object_type = "filament"
                elif "LINKER" in line:
                    object_type = "linker"
                else:
                    object_type = "motor"
                if self._draw_endpoints(line, object_type, input_data):
                    n += 2
                if "FILAMENT" in line:
                    # start of filament
                    cols = line.split()
                    s = int(cols[3])
                    if max_subpoints < s:
                        max_subpoints = s
                else:
                    # start of linker or motor
                    if max_subpoints < 2:
                        max_subpoints = 2
        if n > max_agents:
            max_agents = n
        return totalSteps, max_agents, max_subpoints

    def _get_trajectory_data(self, input_data: MedyanData) -> AgentData:
        """
        Parse a MEDYAN snapshot.traj output file to get agents
        """
        with open(input_data.path_to_snapshot, "r") as myfile:
            lines = myfile.read().split("\n")
        totalSteps, max_agents, max_subpoints = self._parse_data_dimensions(
            lines, input_data
        )
        result = AgentData(
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
        result.type_ids = np.zeros((totalSteps, max_agents))
        t = -1
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
                t += 1
                n = 0
                result.times[t] = float(cols[1])
                result.n_agents[t] = int(cols[2]) + int(cols[3]) + int(cols[4])
                at_frame_start = False
            if "FILAMENT" in line or "LINKER" in line or "MOTOR" in line:
                # start of object
                result.viz_types[t][n] = VIZ_TYPE.FIBER
                if "FILAMENT" in line:
                    object_type = "filament"
                elif "LINKER" in line:
                    object_type = "linker"
                else:
                    object_type = "motor"
                draw_endpoints = self._draw_endpoints(line, object_type, input_data)
                # unique instance ID
                raw_uid = int(cols[1])
                if raw_uid not in uids[object_type]:
                    uids[object_type][raw_uid] = last_uid
                    last_uid += 1 if not draw_endpoints else 3
                result.unique_ids[t][n] = uids[object_type][raw_uid]
                # type ID
                raw_tid = int(cols[2])
                if raw_tid not in tids[object_type]:
                    tids[object_type][raw_tid] = last_tid
                    last_tid += 1
                result.type_ids[t][n] = tids[object_type][raw_tid]
                # type name
                while n >= len(result.types[t]):
                    result.types[t].append("")
                result.types[t][n] = (
                    input_data.agent_info[object_type][raw_tid].name
                    if raw_tid in input_data.agent_info[object_type]
                    else object_type + str(raw_tid)
                )
                # radius
                result.radii[t][n] = input_data.scale_factor * (
                    input_data.agent_info[object_type][raw_tid].radius
                    if raw_tid in input_data.agent_info[object_type]
                    else 1.0
                )
                if "FILAMENT" in line:
                    result.n_subpoints[t][n] = int(cols[3])
                else:
                    result.n_subpoints[t][n] = 2
                # draw endpoints?
                if draw_endpoints:
                    for i in range(2):
                        result.viz_types[t][n + i + 1] = VIZ_TYPE.DEFAULT
                        result.unique_ids[t][n + i + 1] = (
                            uids[object_type][raw_uid] + i + 1
                        )
                        result.type_ids[t][n + i + 1] = tids[object_type][raw_tid]
                        while n + i + 1 >= len(result.types[t]):
                            result.types[t].append("")
                        result.types[t][n + i + 1] = result.types[t][n]
                        result.radii[t][n + i + 1] = input_data.scale_factor * (
                            input_data.agent_info[object_type][raw_tid].endpoint_radius
                            if raw_tid in input_data.agent_info[object_type]
                            else 1.0
                        )
                parsing_object = True
            elif parsing_object:
                # object coordinates
                for i in range(len(cols)):
                    s = math.floor(i / 3)
                    d = i % 3
                    result.subpoints[t][n][s][d] = input_data.scale_factor * float(
                        cols[i]
                    )
                    if draw_endpoints:
                        result.positions[t][n + s + 1][
                            d
                        ] = input_data.scale_factor * float(cols[i])
                parsing_object = False
                n += 1
                if draw_endpoints:
                    n += 2
                    result.n_agents[t] += 2
        return result

    def _read(self, input_data: MedyanData) -> TrajectoryData:
        """
        Return an object containing the data shaped for Simularium format
        """
        print("Reading MEDYAN Data -------------")
        agent_data = self._get_trajectory_data(input_data)
        time_units = UnitData("s")
        spatial_units = UnitData("nm", 1.0 / input_data.scale_factor)
        return TrajectoryData(
            box_size=input_data.scale_factor * input_data.box_size,
            agent_data=agent_data,
            time_units=time_units,
            spatial_units=spatial_units,
            plots=input_data.plots,
        )
