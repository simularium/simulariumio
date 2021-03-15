#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Tuple

import numpy as np

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, MetaData
from ..constants import VIZ_TYPE
from .smoldyn_data import SmoldynData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class SmoldynConverter(TrajectoryConverter):
    def __init__(self, input_data: SmoldynData):
        """
        This object reads simulation trajectory outputs
        from Smoldyn (http://www.smoldyn.org)
        and plot data and writes them in the JSON format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : SmoldynData
            An object containing info for reading
            Smoldyn simulation trajectory outputs and plot data
        """
        self._data = self._read(input_data)

    def _parse_dimensions(self, smoldyn_data_lines: List[str]) -> Tuple[int]:
        """
        Parse Smoldyn output files to get the number of timesteps
        and maximum agents per timestep
        """
        time_steps = -1
        max_agents = 0
        current_agents = 0
        for line in smoldyn_data_lines:
            cols = line.split()
            if len(cols) == 2:
                if current_agents > max_agents:
                    max_agents = current_agents
                current_agents = 0
                time_steps += 1
            else:
                current_agents += 1
        if current_agents > max_agents:
            max_agents = current_agents
        return (time_steps + 1, max_agents)

    @staticmethod
    def _format_type_name(raw_name: str) -> Tuple[str, str]:
        """
        Format a type name to take advantage of Simularium state names
        return ("type#state", "type") if state is found,
        otherwise ("type", "type")
        """
        if "(" in raw_name:
            cols = raw_name.split("(")
            return f"{cols[0]}#{cols[1][:-1]}", cols[0]
        return raw_name, raw_name

    def _parse_objects(
        self,
        smoldyn_data_lines: List[str],
        input_data: SmoldynData,
    ) -> AgentData:
        """
        Parse a Smoldyn output file to get AgentData
        """
        (totalSteps, max_agents) = self._parse_dimensions(smoldyn_data_lines)
        result = AgentData(
            times=np.zeros(totalSteps),
            n_agents=np.zeros(totalSteps),
            viz_types=VIZ_TYPE.DEFAULT * np.ones((totalSteps, max_agents)),
            unique_ids=np.zeros((totalSteps, max_agents)),
            types=[[] for t in range(totalSteps)],
            positions=np.zeros((totalSteps, max_agents, 3)),
            radii=np.ones((totalSteps, max_agents)),
        )
        t = -1
        n = 0
        for line in smoldyn_data_lines:
            if len(line) < 1:
                continue
            cols = line.split()
            if len(cols) == 2:
                if t >= 0:
                    result.n_agents[t] = n
                n = 0
                t += 1
                result.times[t] = float(cols[0])
            else:
                if len(cols) < 4:
                    raise Exception(
                        "Smoldyn data is not formatted as expected, "
                        "please use the Smoldyn `listmols` command for output"
                    )
                is_3D = len(cols) > 4
                result.unique_ids[t][n] = int(cols[4] if is_3D else cols[3])
                type_name, base_type = SmoldynConverter._format_type_name(str(cols[0]))
                result.types[t].append(type_name)
                result.positions[t][n] = input_data.meta_data.scale_factor * np.array(
                    [
                        float(cols[1]),
                        float(cols[2]),
                        float(cols[3]) if is_3D else 0.0,
                    ]
                )
                result.radii[t][n] = input_data.meta_data.scale_factor * (
                    input_data.radii[base_type]
                    if base_type in input_data.radii
                    else 1.0
                )
                n += 1
        result.n_agents[t] = n
        return result

    def _read(self, input_data: SmoldynData) -> TrajectoryData:
        """
        Return a TrajectoryData object containing the Smoldyn data
        """
        print("Reading Smoldyn Data -------------")
        # load the data from Smoldyn output .txt file
        smoldyn_data = []
        with open(input_data.path_to_output_txt, "r") as myfile:
            smoldyn_data = myfile.read().split("\n")
        # parse
        agent_data = self._parse_objects(smoldyn_data, input_data)
        # create TrajectoryData
        input_data.spatial_units.multiply(1.0 / input_data.meta_data.scale_factor)
        return TrajectoryData(
            meta_data=MetaData(
                box_size=input_data.meta_data.scale_factor
                * input_data.meta_data.box_size,
                camera_defaults=input_data.meta_data.camera_defaults,
            ),
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=input_data.spatial_units,
            plots=input_data.plots,
        )
