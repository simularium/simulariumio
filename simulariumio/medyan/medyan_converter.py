#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List, Tuple
import math

import numpy as np

from ..custom_converter import CustomConverter
from ..data_objects import AgentData
from ..constants import VIZ_TYPE
from .medyan_data import MedyanData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MedyanConverter(CustomConverter):
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

    def _parse_data_dimensions(self, lines: List[str]) -> List[int]:
        """
        Parse a MEDYAN snapshot.traj output file to get the number
        of subpoints per agent per timestep
        """
        totalSteps = 0
        max_agents = 0
        max_subpoints = 0
        at_frame_start = True
        for line in lines:
            if len(line) < 1:
                at_frame_start = True
                continue
            if at_frame_start:
                # start of timestep
                cols = line.split()
                n = int(cols[2]) + int(cols[3]) + int(cols[4])
                if n > max_agents:
                    max_agents = n
                totalSteps += 1
                at_frame_start = False
            elif "FILAMENT" in line:
                # start of filament
                cols = line.split()
                s = int(cols[3])
                if max_subpoints < s:
                    max_subpoints = s
            elif "LINKER" in line or "MOTOR" in line:
                # start of linker or motor
                if max_subpoints < 2:
                    max_subpoints = 2
        return totalSteps, max_agents, max_subpoints

    def _get_trajectory_data(
        self, input_data: MedyanData
    ) -> Tuple[AgentData, Dict[str, Dict[int, int]]]:
        """
        Parse a MEDYAN snapshot.traj output file to get agents
        """
        with open(input_data.path_to_snapshot, "r") as myfile:
            lines = myfile.read().split("\n")
        totalSteps, max_agents, max_subpoints = self._parse_data_dimensions(lines)
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
        for line in lines:
            if len(line) < 1:
                at_frame_start = True
                continue
            cols = line.split()
            if at_frame_start:
                # start of timestep
                t += 1
                n = 0
                agent_data.times[t] = float(cols[1])
                agent_data.n_agents[t] = int(cols[2]) + int(cols[3]) + int(cols[4])
                at_frame_start = False
            if "FILAMENT" in line or "LINKER" in line or "MOTOR" in line:
                # start of object
                agent_data.viz_types[t][n] = VIZ_TYPE.fiber
                if "FILAMENT" in line:
                    object_type = "filament"
                elif "LINKER" in line:
                    object_type = "linker"
                elif "MOTOR" in line:
                    object_type = "motor"
                # unique instance ID
                raw_uid = int(cols[1])
                if raw_uid not in uids[object_type]:
                    uids[object_type][raw_uid] = last_uid
                    last_uid += 1
                agent_data.unique_ids[t][n] = uids[object_type][raw_uid]
                # type ID
                raw_tid = int(cols[2])
                if raw_tid not in tids[object_type]:
                    tids[object_type][raw_tid] = last_tid
                    last_tid += 1
                agent_data.type_ids[t][n] = tids[object_type][raw_tid]
                # radius
                agent_data.radii[t][n] = (
                    input_data.agent_info[object_type][raw_tid].radius
                    if raw_tid in input_data.agent_info[object_type]
                    else 1.0
                )
                if "FILAMENT" in line:
                    agent_data.n_subpoints[t][n] = int(cols[3])
                else:
                    agent_data.n_subpoints[t][n] = 2
                parsing_object = True
            elif parsing_object:
                # object coordinates
                for i in range(len(cols)):
                    s = math.floor(i / 3)
                    d = i % 3
                    agent_data.subpoints[t][n][s][d] = float(cols[i])
                parsing_object = False
                n += 1
        return agent_data, tids

    def _read(self, input_data: MedyanData) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """
        print("Reading MEDYAN Data -------------")
        # load the data from MEDYAN snapshot.traj
        agent_data, type_id_mapping = self._get_trajectory_data(input_data)
        # shape data
        simularium_data = {}
        # type mapping
        type_name_mapping = {}
        for object_type in input_data.agent_info:
            for raw_tid in type_id_mapping[object_type]:
                tid = type_id_mapping[object_type][raw_tid]
                type_name_mapping[str(tid)] = {
                    "name": (
                        input_data.agent_info[object_type][raw_tid].name
                        if raw_tid in input_data.agent_info[object_type]
                        else object_type + str(raw_tid)
                    )
                }
        # trajectory info
        totalSteps = agent_data.n_agents.shape[0]
        simularium_data["trajectoryInfo"] = {
            "version": 1,
            "timeStepSize": CustomConverter._format_timestep(
                float(agent_data.times[2] - agent_data.times[1])
                if totalSteps > 2
                else float(agent_data.times[1] - agent_data.times[0])
                if totalSteps > 1
                else 0.0
            ),
            "totalSteps": totalSteps,
            "spatialUnitFactorMeters": input_data.scale_factor * 1e-6,
            "size": {
                "x": input_data.scale_factor * float(input_data.box_size[0]),
                "y": input_data.scale_factor * float(input_data.box_size[1]),
                "z": input_data.scale_factor * float(input_data.box_size[2]),
            },
            "typeMapping": type_name_mapping,
        }
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
            "data": input_data.plots,
        }
        return simularium_data
