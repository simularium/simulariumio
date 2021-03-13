#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Tuple

import numpy as np

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData
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
        time_steps = 0
        max_agents = 0
        current_agents = 0
        for line in smoldyn_data_lines:
            if line.startswith("mol") or line.startswith("surface_mol"):
                current_agents += 1
            elif line.contains("end_file"):
                if current_agents > max_agents:
                    max_agents = current_agents
                current_agents = 0
                time_steps += 1
        return (time_steps, max_agents)

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
        t = 0
        n = 0
        for line in smoldyn_data_lines:
            cols = line.split()
            if line.startswith("time_now"):
                result.times[t] = float(cols[1])
            elif line.startswith("mol") or line.startswith("surface_mol"):
                position_ix = [3, 4, 5]
                if line.startswith("surface_mol"):
                    position_ix = [6, 7, 8]
                result.unique_ids[t][n] = n
                type_name = str(cols[2])
                result.types[t].append(type_name)
                result.positions[t][n] = input_data.meta_data.scale_factor * np.array(
                    [
                        float(cols[position_ix[0]]),
                        float(cols[position_ix[1]]),
                        float(cols[position_ix[2]]) if len(cols) > position_ix[2] else 0.0,
                    ]
                )
                result.radii[t][n] = input_data.meta_data.scale_factor * (input_data.radii[type_name] if type_name in input_data.radii else 1.0)
                n += 1
            elif line.contains("end_file"):
                result.n_agents[t] = n
                n = 0
                t += 1
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
