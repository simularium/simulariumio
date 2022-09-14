#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Tuple

import numpy as np

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import (
    TrajectoryData,
    AgentData,
    UnitData,
    DimensionData,
    DisplayData,
)
from .springsalad_data import SpringsaladData
from ..constants import (
    VIZ_TYPE,
    DISPLAY_TYPE,
    VALUES_PER_3D_POINT,
    SUBPOINT_VALUES_PER_ITEM,
)

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

    @staticmethod
    def _parse_dimensions(
        springsalad_data: List[str], draw_bonds: bool
    ) -> DimensionData:
        """
        Parse SpringSaLaD SIM_VIEW txt file to get the number of timesteps
        and maximum agents per timestep
        """
        result = DimensionData(
            0, 0, 2 * SUBPOINT_VALUES_PER_ITEM(DISPLAY_TYPE.FIBER) if draw_bonds else 0
        )
        agents = 0
        for line in springsalad_data:
            if "CurrentTime" in line:  # beginning of a frame
                if agents > result.max_agents:
                    result.max_agents = agents
                agents = 0
                result.total_steps += 1
            if "ID" in line:  # line has data for one agent
                agents += 1
            if draw_bonds and "Link" in line:  # line has data for a bond
                agents += 1
        if agents > result.max_agents:
            result.max_agents = agents
        return result

    @staticmethod
    def _parse_springsalad_data(
        springsalad_data: List[str], input_data: SpringsaladData
    ) -> Tuple[AgentData, np.ndarray]:
        """
        Parse SpringSaLaD SIM_VIEW txt file to get spatial data
        """
        dimensions = SpringsaladConverter._parse_dimensions(
            springsalad_data, input_data.draw_bonds
        )
        result = AgentData.from_dimensions(dimensions)
        box_size = np.zeros(VALUES_PER_3D_POINT)
        time_index = -1
        agent_index = 0
        max_uid = 0
        scene_agent_positions = {}
        for line in springsalad_data:
            cols = line.split()
            if "xsize" in line:
                box_size[0] = 2 * float(cols[1])
            if "ysize" in line:
                box_size[1] = 2 * float(cols[1])
            if "z_outside" in line:
                box_size[2] += 2 * float(cols[1])
            if "z_inside" in line:
                box_size[2] += 2 * float(cols[1])
            if "CurrentTime" in line:  # beginning of a scene (timepoint)
                agent_index = 0
                time_index += 1
                result.times[time_index] = float(
                    line.split("CurrentTime")[1].split()[0]
                )
                scene_agent_positions = {}
                max_uid = 0
            if "ID" in line:  # line has data for one agent in scene
                result.n_agents[time_index] += 1
                result.unique_ids[time_index][agent_index] = int(cols[1])
                raw_type_name = cols[3]
                result.types[time_index].append(
                    TrajectoryConverter._get_display_type_name_from_raw(
                        raw_type_name, input_data.display_data
                    )
                )
                position = input_data.meta_data.scale_factor * np.array(
                    [float(cols[4]), float(cols[5]), float(cols[6])]
                )
                scene_agent_positions[int(cols[1])] = position
                result.positions[time_index][agent_index] = position
                result.radii[time_index][
                    agent_index
                ] = input_data.meta_data.scale_factor * (
                    input_data.display_data[raw_type_name].radius
                    if raw_type_name in input_data.display_data
                    and input_data.display_data[raw_type_name].radius is not None
                    else float(cols[2])
                )
                agent_index += 1
            if input_data.draw_bonds and "Link" in line:  # line has data for a bond
                particle1_id = int(cols[1])
                particle2_id = int(cols[3])
                if (
                    particle1_id not in scene_agent_positions
                    or particle2_id not in scene_agent_positions
                ):
                    raise Exception(
                        "Could not find particle ID connected by Link "
                        f"at timepoint {time_index} in SpringSaLaD data, "
                        "try converting without drawing bonds"
                    )
                result.n_agents[time_index] += 1
                result.viz_types[time_index][agent_index] = VIZ_TYPE.FIBER
                result.unique_ids[time_index][agent_index] = max_uid
                max_uid += 1
                result.types[time_index].append("Link")
                result.n_subpoints[time_index][
                    agent_index
                ] = 2 * SUBPOINT_VALUES_PER_ITEM(DISPLAY_TYPE.FIBER)
                result.subpoints[time_index][agent_index][
                    0:VALUES_PER_3D_POINT
                ] = scene_agent_positions[particle1_id]
                result.subpoints[time_index][agent_index][
                    VALUES_PER_3D_POINT : 2 * VALUES_PER_3D_POINT
                ] = scene_agent_positions[particle2_id]
                agent_index += 1
        result.n_timesteps = time_index + 1
        return result, box_size

    @staticmethod
    def _read(input_data: SpringsaladData) -> TrajectoryData:
        """
        Return an object containing the data shaped for Simularium format
        """
        print("Reading SpringSaLaD Data -------------")
        springsalad_data = input_data.sim_view_txt_file.get_contents().split("\n")
        agent_data, box_size = SpringsaladConverter._parse_springsalad_data(
            springsalad_data, input_data
        )
        # get display data (geometry and color)
        for tid in input_data.display_data:
            display_data = input_data.display_data[tid]
            agent_data.display_data[display_data.name] = display_data
        if input_data.draw_bonds:
            agent_data.display_data["Link"] = DisplayData(
                name="Link",
                display_type=DISPLAY_TYPE.FIBER,
            )
        input_data.meta_data._set_box_size(box_size)
        return TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=UnitData("s"),
            spatial_units=UnitData("nm", 1.0 / input_data.meta_data.scale_factor),
            plots=input_data.plots,
        )
