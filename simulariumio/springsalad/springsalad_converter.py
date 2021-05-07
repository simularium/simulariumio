#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Tuple

import numpy as np

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, MetaData, UnitData
from .springsalad_data import SpringsaladData
from ..constants import VIZ_TYPE

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class SpringsaladConverter(TrajectoryConverter):
    def __init__(self, input_data: SpringsaladData):
        """
        This object reads simulation trajectory outputs
        from SpringSaLaD (https://vcell.org/ssalad)
        and plot data and writes them in the JSON format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : SpringsaladData
            An object containing info for reading
            SpringSaLaD simulation trajectory outputs and plot data
        """
        self._data = self._read(input_data)

    def _parse_dimensions(self, springsalad_data: List[str]) -> Tuple[int]:
        """
        Parse SpringSaLaD SIM_VIEW txt file to get the number of timesteps
        and maximum agents per timestep
        """
        total_steps = 0
        max_agents = 0
        current_agents = 0
        for line in springsalad_data:
            if "CurrentTime" in line:  # beginning of a frame
                if current_agents > max_agents:
                    max_agents = current_agents
                current_agents = 0
                total_steps += 1
            if "ID" in line:  # line has data for one agent
                current_agents += 1
        if current_agents > max_agents:
            max_agents = current_agents
        return (total_steps, max_agents)

    def _parse_springsalad_data(
        self, springsalad_data: List[str], input_data: SpringsaladData
    ) -> Tuple[AgentData, np.ndarray]:
        """
        Parse SpringSaLaD SIM_VIEW txt file to get spatial data
        """
        total_steps, max_agents = self._parse_dimensions(springsalad_data)
        result = AgentData(
            times=np.zeros(total_steps),
            n_agents=np.zeros(total_steps),
            viz_types=VIZ_TYPE.DEFAULT * np.ones((total_steps, max_agents)),
            unique_ids=np.zeros((total_steps, max_agents)),
            types=[[] for t in range(total_steps)],
            positions=np.zeros((total_steps, max_agents, 3)),
            radii=np.ones((total_steps, max_agents)),
            rotations=np.zeros((total_steps, max_agents, 3)),
        )
        box_size = np.zeros(3)
        t = -1
        n = 0
        for line in springsalad_data:
            cols = line.split()
            if "xsize" in line:
                box_size[0] = input_data.scale_factor * 2 * float(cols[1])
            if "ysize" in line:
                box_size[1] = input_data.scale_factor * 2 * float(cols[1])
            if "z_outside" in line:
                box_size[2] += input_data.scale_factor * 2 * float(cols[1])
            if "z_inside" in line:
                box_size[2] += input_data.scale_factor * 2 * float(cols[1])
            if "CurrentTime" in line:  # beginning of a scene
                n = 0
                t += 1
                result.times[t] = float(line.split("CurrentTime")[1].split()[0])
            if "ID" in line:  # line has data for one agent in scene
                result.n_agents[t] += 1
                result.unique_ids[t][n] = int(cols[1])
                type_name = cols[3]
                if type_name in input_data.display_names:
                    type_name = input_data.display_names[type_name]
                result.types[t].append(type_name)
                result.positions[t][n] = input_data.scale_factor * np.array(
                    [float(cols[4]), float(cols[5]), float(cols[6])]
                )
                result.radii[t][n] = input_data.scale_factor * float(cols[2])
                n += 1
        return result, box_size

    def _read(self, input_data: SpringsaladData) -> TrajectoryData:
        """
        Return an object containing the data shaped for Simularium format
        """
        print("Reading SpringSaLaD Data -------------")
        with open(input_data.path_to_sim_view_txt, "r") as myfile:
            springsalad_data = myfile.read().split("\n")
        agent_data, box_size = self._parse_springsalad_data(
            springsalad_data, input_data
        )
        return TrajectoryData(
            meta_data=MetaData(
                box_size=box_size,
                camera_defaults=input_data.camera_defaults,
            ),
            agent_data=agent_data,
            time_units=UnitData("s"),
            spatial_units=UnitData("nm", 1.0 / input_data.scale_factor),
            plots=input_data.plots,
        )
