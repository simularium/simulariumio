#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Tuple

import numpy as np
import pandas as pd

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, MetaData, UnitData
from .springsalad_data import SpringsaladData

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

    def _parse_springsalad_data(
        self, springsalad_data: List[str], input_data: SpringsaladData
    ) -> Tuple[AgentData, np.ndarray]:
        """
        Parse SpringSaLaD SIM_VIEW txt file to get the total steps
        and maximum agents per timestep
        """
        columns_list = [
            "time",
            "unique_id",
            "type",
            "positionX",
            "positionY",
            "positionZ",
            "rotationX",
            "rotationY",
            "rotationZ",
            "radius",
        ]
        traj = pd.DataFrame([], columns=columns_list)
        timestamp = 0.0
        box_size = np.zeros(3)
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
                timestamp = float(line.split("CurrentTime")[1].split()[0])
            if "ID" in line:  # line has data for one agent in scene
                type_name = cols[3]
                if type_name in input_data.display_names:
                    type_name = input_data.display_names[type_name]
                agent = pd.DataFrame(
                    [
                        [
                            timestamp,
                            int(cols[1]),  # unique id
                            type_name,  # type
                            input_data.scale_factor * float(cols[4]),  # position X
                            input_data.scale_factor * float(cols[5]),  # position Y
                            input_data.scale_factor * float(cols[6]),  # position Z
                            0.0,  # rotation X
                            0.0,  # rotation Y
                            0.0,  # rotation Z
                            input_data.scale_factor * float(cols[2]),  # radius
                        ]
                    ],
                    columns=columns_list,
                )
                traj = traj.append(agent)
        return AgentData.from_dataframe(traj), box_size

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
