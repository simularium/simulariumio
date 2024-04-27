#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import copy
from typing import Set, Callable, Tuple

import numpy as np
import pandas as pd
from MDAnalysis.topology.core import guess_atom_element
from MDAnalysis.topology.tables import vdwradii

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, DimensionData, DisplayData
from ..constants import DISPLAY_TYPE, JMOL_COLORS, VIZ_TYPE, SUBPOINT_VALUES_PER_ITEM
from .md_data import MdData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MdConverter(TrajectoryConverter):
    def __init__(
        self,
        input_data: MdData,
        progress_callback: Callable[[float], None] = None,
        callback_interval: float = 10,
        draw_bonds: bool = False,
    ):
        """
        This object reads simulation trajectory outputs
        from molecular dynamics models
        and plot data and writes them in the format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : MdData
            An object containing info for reading
            MD simulation trajectory outputs and plot data
        progress_callback : Callable[[float], None] (optional)
            Callback function that accepts 1 float argument and returns None
            which will be called at a given progress interval, determined by
            callback_interval requested, providing the current percent progress
            Default: None
        callback_interval : float (optional)
            If a progress_callback was provided, the period between updates
            to be sent to the callback, in seconds
            Default: 10
        draw_bonds: bool (optional)
            Default: False
        """
        super().__init__(input_data, progress_callback, callback_interval)
        self.draw_bonds = draw_bonds
        self._data = self._read(input_data)

    @staticmethod
    def _read_universe_dimensions(
        input_data: MdData,
    ) -> DimensionData:
        """
        Use a MD Universe to get the number of timesteps
        and maximum agents per timestep
        """
        result = DimensionData(
            total_steps=0,
            max_agents=0,
        )
        for ts in input_data.md_universe.trajectory[:: input_data.nth_timestep_to_read]:
            result.total_steps += 1
            n_agents = input_data.md_universe.atoms.positions.shape[0]
            if n_agents > result.max_agents:
                result.max_agents = n_agents
        return result

    @staticmethod
    def _get_type_name(raw_type_name: str, input_data: MdData) -> float:
        """
        Get the type_name to use for the particle with the given raw type_name
        """
        element_type = guess_atom_element(raw_type_name)
        for name in input_data.display_data:
            if raw_type_name.lower() == name.lower():
                return input_data.display_data[name].name
            if element_type.lower() == name.lower():
                return input_data.display_data[name].name + "#" + raw_type_name
        return element_type + "#" + raw_type_name

    @staticmethod
    def _get_radius(raw_type_name: str, input_data: MdData) -> float:
        """
        Get the radius to use for the particle with the given raw_type_name
        """
        raw_display_data = TrajectoryConverter._get_display_data_for_agent(
            raw_type_name, input_data.display_data
        )
        if raw_display_data and raw_display_data.radius is not None:
            return raw_display_data.radius
        element_type = guess_atom_element(raw_type_name)
        element_display_data = TrajectoryConverter._get_display_data_for_agent(
            element_type, input_data.display_data
        )
        if element_display_data and element_display_data.radius is not None:
            return element_display_data.radius
        if element_type in vdwradii:
            return vdwradii[element_type]
        return 1.0

    @staticmethod
    def _get_element_hex_color(element_type: str, jmol_colors: pd.DataFrame) -> str:
        """
        Get the standard Jmol hex color for the atomic element type
        """
        element_df = jmol_colors.loc[jmol_colors["atom"] == element_type.title()]
        return "#" + str(element_df.Hex.values[0]) if not element_df.empty else ""

    @staticmethod
    def _get_display_data_for_type(
        raw_type_name: str, jmol_colors: pd.DataFrame, input_data: MdData
    ) -> DisplayData:
        """
        Get the DisplayData with atomic element colors from Jmol
        """
        element_type = guess_atom_element(raw_type_name)
        color = MdConverter._get_element_hex_color(element_type, jmol_colors)
        display_data = None
        raw_name_display_data = TrajectoryConverter._get_display_data_for_agent(
            raw_type_name, input_data.display_data
        )
        if raw_name_display_data:
            display_data = copy.copy(raw_name_display_data)
        else:
            type_name = MdConverter._get_type_name(raw_type_name, input_data)
            element_display_data = TrajectoryConverter._get_display_data_for_agent(
                type_name, input_data.display_data
            )
            if element_display_data:
                display_data = copy.copy(element_display_data)
                display_data.name = type_name
            else:
                display_data = DisplayData(
                    name=type_name, display_type=DISPLAY_TYPE.SPHERE
                )
        if display_data.color:
            return display_data
        display_data.color = color
        return display_data

    @staticmethod
    def _get_display_data_mapping(
        unique_raw_type_names: Set[str], input_data: MdData
    ) -> DisplayData:
        """
        Get display names mapped to display data (geometry and color)
        """
        result = {}
        jmol_colors = JMOL_COLORS()
        for raw_type_name in unique_raw_type_names:
            display_data = MdConverter._get_display_data_for_type(
                raw_type_name, jmol_colors, input_data
            )
            result[display_data.name] = display_data
        return result

    def _read_universe(self, input_data: MdData) -> Tuple[AgentData, float]:
        """
        Use a MD Universe to get AgentData
        """
        dimensions = MdConverter._read_universe_dimensions(input_data)
        if input_data.draw_bonds:
            bond_indices = input_data.md_universe.bonds.indices
            n_bonds = bond_indices.shape[0]
            n_max_subpoints = 2 * SUBPOINT_VALUES_PER_ITEM(DISPLAY_TYPE.FIBER)
        else:
            bond_indices = np.array([])
            n_bonds = 0
            n_max_subpoints = 0
        dimensions = DimensionData(
            dimensions.total_steps, 
            dimensions.max_agents + n_bonds, 
            n_max_subpoints,
        )
        result = AgentData.from_dimensions(dimensions)
        get_type_name_func = np.frompyfunc(MdConverter._get_type_name, 2, 1)
        unique_raw_type_names = set([])
        time_index = 0

        for frame in input_data.md_universe.trajectory[
            :: input_data.nth_timestep_to_read
        ]:
            result.times[time_index] = input_data.md_universe.trajectory.time
            atom_positions = input_data.md_universe.atoms.positions
            if input_data.draw_bonds:
                bond_subpoints = np.array(
                    [
                        np.concatenate(
                            [
                                atom_positions[bond_indices[i][0]],
                                atom_positions[bond_indices[i][1]],
                            ]
                        )
                        for i in range(bond_indices.shape[0])
                    ]
                )
            else:
                bond_subpoints = np.array([])
            n_agents = atom_positions.shape[0] + n_bonds
            result.n_agents[time_index] = n_agents
            result.unique_ids[time_index] = np.arange(n_agents)
            type_name_list = list(input_data.md_universe.atoms.names) 
            if input_data.draw_bonds:
                type_name_list += ['bond']
            unique_raw_type_names.update(type_name_list)
            result.types[time_index][:atom_positions.shape[0]] = get_type_name_func(
                input_data.md_universe.atoms.names, input_data
            )
            if input_data.draw_bonds:
                result.types[time_index][atom_positions.shape[0]:] = ['bond'] * n_bonds
            result.positions[time_index][:atom_positions.shape[0]] = atom_positions
            radii_list = [
                MdConverter._get_radius(type_name, input_data)
                for type_name in input_data.md_universe.atoms.names
            ]
            if input_data.draw_bonds:
                radii_list += [
                    MdConverter._get_radius(type_name, input_data)
                    for type_name in ['bond'] * n_bonds
                ]
            result.radii[time_index] = np.array(radii_list)

            if input_data.draw_bonds:
                result.n_subpoints[time_index] = np.array(
                    [0] * atom_positions.shape[0]
                    + [2 * SUBPOINT_VALUES_PER_ITEM(DISPLAY_TYPE.FIBER)] * n_bonds
                )

                result.subpoints[time_index][
                    atom_positions.shape[0]:] = bond_subpoints
                result.viz_types[time_index][
                    atom_positions.shape[0]:] = [VIZ_TYPE.FIBER] * n_bonds

            time_index += 1
            self.check_report_progress(time_index / dimensions.total_steps)

        result.n_timesteps = dimensions.total_steps
        result.display_data = MdConverter._get_display_data_mapping(
            unique_raw_type_names, input_data
        )

        result, scale_factor = TrajectoryConverter.scale_agent_data(
            result, input_data.meta_data.scale_factor
        )
        result = TrajectoryConverter.center_fiber_positions(result)
        return result, scale_factor

    def _read(self, input_data: MdData) -> TrajectoryData:
        """
        Return a TrajectoryData object containing the MD data
        """
        print("Reading MD Data -------------")
        # get data from the MD Universe
        agent_data, scale_factor = self._read_universe(input_data)
        # create TrajectoryData
        input_data.spatial_units.multiply(1.0 / scale_factor)
        input_data.meta_data.scale_factor = scale_factor
        input_data.meta_data._set_box_size()
        return TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=input_data.spatial_units,
            plots=input_data.plots,
        )
