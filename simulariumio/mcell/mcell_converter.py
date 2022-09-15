#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any
import json
import os
import array

import numpy as np
import scipy.linalg as linalg
from scipy.spatial.transform import Rotation

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import (
    TrajectoryData,
    AgentData,
    UnitData,
    DimensionData,
)
from .mcell_data import McellData
from ..constants import VALUES_PER_3D_POINT

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


BLENDER_GEOMETRY_SCALE_FACTOR = 0.005


class McellConverter(TrajectoryConverter):
    def __init__(self, input_data: McellData):
        """
        This object reads simulation trajectory outputs
        from MCell (https://mcell.org/)
        and plot data and writes them in the JSON format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : McellData
            An object containing info for reading
            MCell simulation trajectory outputs and plot data
        """
        self._data = self._read(input_data)

    @staticmethod
    def _normalize(v: np.ndarray) -> np.ndarray:
        """
        normalize a vector
        """
        return v / np.linalg.norm(v)

    @staticmethod
    def _rotate(v: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
        """
        rotate a vector around axis by angle (radians)
        """
        rotation = linalg.expm(
            np.cross(
                np.eye(VALUES_PER_3D_POINT), McellConverter._normalize(axis) * angle
            )
        )
        return np.dot(rotation, np.copy(v))

    @staticmethod
    def _get_perpendicular_vector(v: np.ndarray, angle: float) -> np.ndarray:
        """
        Get a unit vector perpendicular to the given vector
        rotated by the given angle
        """
        if v[0] == 0 and v[1] == 0:
            if v[2] == 0:
                raise ValueError("Cannot calculate perpendicular vector to zero vector")
            return np.array([0, 1, 0])
        u = McellConverter._normalize(np.array([-v[1], v[0], 0]))
        return McellConverter._rotate(u, v, angle)

    @staticmethod
    def _get_rotation_matrix(v1: np.ndarray, v2: np.ndarray) -> np.ndarray:
        """
        Orthonormalize and cross the vectors to get a rotation matrix
        """
        v1 = McellConverter._normalize(v1)
        v2 = McellConverter._normalize(v2)
        v2 = McellConverter._normalize(v2 - (np.dot(v1, v2) / np.dot(v1, v1)) * v1)
        v3 = np.cross(v2, v1)
        return np.array(
            [
                np.array([v2[0], v1[0], v3[0]]),
                np.array([v2[1], v1[1], v3[1]]),
                np.array([v2[2], v1[2], v3[2]]),
            ]
        )

    @staticmethod
    def _get_euler_angles(normal: np.ndarray, angle: float) -> np.ndarray:
        """
        Get euler angles in degrees representing a rotation defined by the basis
        between the given normal and a perpendicular vector rotated at angle
        """
        perpendicular = McellConverter._get_perpendicular_vector(normal, angle)
        rotation = McellConverter._get_rotation_matrix(normal, perpendicular)
        return Rotation.from_matrix(rotation).as_euler("xyz", degrees=True)

    @staticmethod
    def _get_rotation_euler_angles_for_normals(
        normals: np.ndarray, angle: float = None
    ) -> np.ndarray:
        """
        Generate an orientation around each normal and return euler angles
        Either use the given angle or random ones
        """
        if angle is None:
            angles = np.rad2deg(2 * np.pi) * np.random.random(normals.shape[0])
        else:
            angles = np.array(normals.shape[0] * [angle])
        return np.array(
            [McellConverter._get_euler_angles(n, a) for n, a in zip(normals, angles)]
        )

    @staticmethod
    def _should_read_cellblender_binary_file(
        file_name: str, nth_timestep_to_read: int
    ) -> bool:
        """
        Is this a cellblender binary file?
        And should this frame of data be included in the visualization?
        """
        if "ascii" in file_name or not file_name.endswith(".dat"):
            return False
        split_file_name = file_name.split(".")
        time_index = int(split_file_name[split_file_name.index("dat") - 1])
        return time_index % nth_timestep_to_read == 0

    @staticmethod
    def _count_agents_in_binary_cellblender_viz_frame(file_name: str) -> int:
        """
        Count the number of agents in the frame of cellblender data
        """
        total_mols = 0
        with open(file_name, "rb") as mol_file:
            # first 4 bytes must contain value '1'
            b = array.array("I")
            b.fromfile(mol_file, 1)
            assert b[0] == 1
            while True:
                try:
                    # advance through file to get
                    # number of instances of each molecule type
                    n_chars_type_name = array.array("B")
                    n_chars_type_name.fromfile(mol_file, 1)
                    mol_file.seek(n_chars_type_name[0], os.SEEK_CUR)
                    is_surface_mol = array.array("B")
                    is_surface_mol.fromfile(mol_file, 1)
                    is_surface_mol = is_surface_mol[0] == 1
                    n_data = array.array("I")
                    n_data.fromfile(mol_file, 1)
                    n_data = n_data[0]
                    data = array.array("f")
                    data.fromfile(mol_file, n_data)
                    if is_surface_mol:
                        data.fromfile(mol_file, n_data)
                    total_mols += int(n_data / float(VALUES_PER_3D_POINT))
                except EOFError:
                    mol_file.close()
                    break
        return total_mols

    @staticmethod
    def _get_dimensions_of_cellblender_data(
        path_to_binary_files: str, nth_timestep_to_read: int
    ) -> DimensionData:
        """
        Parse cellblender binary files to get the number of timesteps
        and maximum agents per timestep
        """
        result = DimensionData(0, 0)
        for file_name in os.listdir(path_to_binary_files):
            if not McellConverter._should_read_cellblender_binary_file(
                file_name, nth_timestep_to_read
            ):
                continue
            result.total_steps += 1
            n_agents = McellConverter._count_agents_in_binary_cellblender_viz_frame(
                os.path.join(path_to_binary_files, file_name)
            )
            if n_agents > result.max_agents:
                result.max_agents = n_agents
        return result

    @staticmethod
    def _read_binary_cellblender_viz_frame(
        file_name: str,
        time_index: int,
        molecule_info: Dict[str, Dict[str, Any]],
        input_data: McellData,
        result: AgentData,
    ) -> AgentData:
        """
        Read MCell binary visualization files

        code based on cellblender/cellblender_mol_viz.py function mol_viz_file_read
        """
        with open(file_name, "rb") as mol_file:
            # first 4 bytes must contain value '1'
            b = array.array("I")
            b.fromfile(mol_file, 1)
            assert b[0] == 1
            while True:
                try:
                    # get type name
                    n_chars_type_name = array.array("B")
                    n_chars_type_name.fromfile(mol_file, 1)
                    type_name_array = array.array("B")
                    type_name_array.fromfile(mol_file, n_chars_type_name[0])
                    raw_type_name = type_name_array.tobytes().decode()
                    display_type_name = (
                        TrajectoryConverter._get_display_type_name_from_raw(
                            raw_type_name, input_data.display_data
                        )
                    )
                    # get positions and rotations
                    is_surface_mol = array.array("B")
                    is_surface_mol.fromfile(mol_file, 1)
                    is_surface_mol = is_surface_mol[0] == 1
                    n_data = array.array("I")
                    n_data.fromfile(mol_file, 1)
                    n_data = n_data[0]
                    n_mols = int(n_data / 3.0)
                    positions = array.array("f")
                    positions.fromfile(mol_file, n_data)
                    positions = input_data.meta_data.scale_factor * np.array(positions)
                    positions = positions.reshape(n_mols, VALUES_PER_3D_POINT)
                    if is_surface_mol:
                        normals = array.array("f")
                        normals.fromfile(mol_file, n_data)
                        normals = np.array(normals)
                        normals = normals.reshape(n_mols, VALUES_PER_3D_POINT)
                        rotations = (
                            McellConverter._get_rotation_euler_angles_for_normals(
                                normals, input_data.surface_mol_rotation_angle
                            )
                        )
                        rotations = rotations.reshape(VALUES_PER_3D_POINT * n_mols)
                    else:
                        rotations = np.zeros_like(positions)
                    # save to AgentData
                    total_mols = int(result.n_agents[time_index])
                    # MCell binary format has no IDs, so use molecule index
                    result.unique_ids[time_index, total_mols : total_mols + n_mols] = (
                        np.arange(n_mols) + total_mols
                    )
                    result.types[time_index] += n_mols * [display_type_name]
                    result.positions[
                        time_index, total_mols : total_mols + n_mols, :
                    ] = positions
                    result.radii[time_index, total_mols : total_mols + n_mols] = (
                        input_data.meta_data.scale_factor
                        * BLENDER_GEOMETRY_SCALE_FACTOR
                        * (
                            input_data.display_data[raw_type_name].radius
                            if raw_type_name in input_data.display_data
                            and input_data.display_data[raw_type_name].radius
                            is not None
                            else molecule_info[raw_type_name]["display"]["scale"]
                        )
                        * np.ones(n_mols)
                    )
                    result.rotations[
                        time_index, total_mols : total_mols + n_mols, :
                    ] = rotations
                    result.n_agents[time_index] += n_mols
                except EOFError:
                    mol_file.close()
                    break
        return result

    @staticmethod
    def _read_cellblender_data(
        timestep: float,
        molecule_list: Dict[str, Any],
        input_data: McellData,
    ) -> AgentData:
        """
        Parse cellblender binary files to get spatial data
        """
        dimensions = McellConverter._get_dimensions_of_cellblender_data(
            input_data.path_to_binary_files, input_data.nth_timestep_to_read
        )
        result = AgentData.from_dimensions(dimensions)
        # get metadata for each agent type
        molecule_info = {}
        total_steps = 0
        for molecule in molecule_list:
            molecule_info[molecule["mol_name"]] = molecule
        for file_name in os.listdir(input_data.path_to_binary_files):
            if not McellConverter._should_read_cellblender_binary_file(
                file_name, input_data.nth_timestep_to_read
            ):
                continue
            split_file_name = file_name.split(".")
            time_index = int(split_file_name[split_file_name.index("dat") - 1])
            if time_index > total_steps:
                total_steps = time_index
            result.times[time_index] = time_index * timestep
            result = McellConverter._read_binary_cellblender_viz_frame(
                os.path.join(input_data.path_to_binary_files, file_name),
                time_index,
                molecule_info,
                input_data,
                result,
            )
        result.n_timesteps = total_steps + 1
        return result

    @staticmethod
    def _read(input_data: McellData) -> TrajectoryData:
        """
        Return an object containing the data shaped for Simularium format
        """
        print("Reading MCell Data -------------")
        # read data model json
        with open(input_data.path_to_data_model_json) as data_model_file:
            data_model = json.load(data_model_file)
        # read spatial data
        time_units = UnitData(
            "s", float(data_model["mcell"]["initialization"]["time_step"])
        )
        agent_data = McellConverter._read_cellblender_data(
            time_units.magnitude,
            data_model["mcell"]["define_molecules"]["molecule_list"],
            input_data,
        )
        time_units.magnitude = 1
        # get box size
        partitions = data_model["mcell"]["initialization"]["partitions"]
        box_size = np.array(
            [
                float(partitions["x_end"]) - float(partitions["x_start"]),
                float(partitions["y_end"]) - float(partitions["y_start"]),
                float(partitions["z_end"]) - float(partitions["z_start"]),
            ]
        )
        # get display data (geometry and color)
        for type_name in input_data.display_data:
            display_data = input_data.display_data[type_name]
            agent_data.display_data[display_data.name] = display_data
        input_data.meta_data._set_box_size(box_size)
        return TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=time_units,
            spatial_units=UnitData("µm", 1.0 / input_data.meta_data.scale_factor),
            plots=input_data.plots,
        )
