#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Dict, Any
import json
import os
import array

import numpy as np
import scipy.linalg as linalg
from scipy.spatial.transform import Rotation
import pandas as pd

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, MetaData, UnitData
from .mcell_data import McellData

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
    def normalize(v: np.ndarray) -> np.ndarray:
        """
        normalize a vector
        """
        return v / np.linalg.norm(v)

    @staticmethod
    def rotate(v: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
        """
        rotate a vector around axis by angle (radians)
        """
        rotation = linalg.expm(
            np.cross(np.eye(3), McellConverter.normalize(axis) * angle)
        )
        return np.dot(rotation, np.copy(v))

    @staticmethod
    def get_perpendicular_vector(v: np.ndarray, angle: float) -> np.ndarray:
        """
        Get a unit vector perpendicular to the given vector
        rotated by the given angle
        """
        if v[0] == 0 and v[1] == 0:
            if v[2] == 0:
                raise ValueError("Cannot calculate perpendicular vector to zero vector")
            return np.array([0, 1, 0])
        u = McellConverter.normalize(np.array([-v[1], v[0], 0]))
        return McellConverter.rotate(u, v, angle)

    @staticmethod
    def get_rotation_matrix(v1: np.ndarray, v2: np.ndarray) -> np.matrix:
        """
        Orthonormalize and cross the vectors to get a rotation matrix
        """
        v1 = McellConverter.normalize(v1)
        v2 = McellConverter.normalize(v2)
        v2 = McellConverter.normalize(v2 - (np.dot(v1, v2) / np.dot(v1, v1)) * v1)
        v3 = np.cross(v2, v1)
        return np.matrix(
            [[v2[0], v1[0], v3[0]], [v2[1], v1[1], v3[1]], [v2[2], v1[2], v3[2]]]
        )

    @staticmethod
    def get_euler_angles(normal: np.ndarray, angle: float) -> np.ndarray:
        """
        Get euler angles in degrees representing a rotation defined by the basis
        between the given normal and a perpendicular vector rotated at angle
        """
        perpendicular = McellConverter.get_perpendicular_vector(normal, angle)
        rotation = McellConverter.get_rotation_matrix(normal, perpendicular)
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
            [McellConverter.get_euler_angles(n, a) for n, a in zip(normals, angles)]
        )

    @staticmethod
    def _read_binary_cellblender_viz_frame(
        file_name: str,
        current_time: float,
        molecule_info: Dict[str, Dict[str, Any]],
        columns_list: List[str],
        input_data: McellData,
    ) -> pd.DataFrame:
        """
        Read MCell binary visualization files

        code based on cellblender/cellblender_mol_viz.py function mol_viz_file_read
        """
        result = pd.DataFrame([], columns=columns_list)
        total_mols = 0
        with open(file_name, "rb") as mol_file:
            # first 4 bytes must contain value '1'
            b = array.array("I")
            b.fromfile(mol_file, 1)
            assert b[0] == 1
            while True:
                try:
                    """
                    ni = Initially, byte array of molecule name length.
                    Later, array of number of molecule positions in xyz
                    (essentially, the number of molecules multiplied by 3).
                    ns = Array of ascii character codes for molecule name.
                    s = String of molecule name.
                    mt = Surface molecule flag.
                    """
                    # get type name
                    n_chars_type_name = array.array("B")
                    n_chars_type_name.fromfile(mol_file, 1)
                    type_name_array = array.array("B")
                    type_name_array.fromfile(mol_file, n_chars_type_name[0])
                    type_name = type_name_array.tostring().decode()
                    display_type_name = (
                        input_data.display_names[type_name]
                        if type_name in input_data.display_names
                        else type_name
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
                    positions = input_data.scale_factor * np.array(positions)
                    if is_surface_mol:
                        normals = array.array("f")
                        normals.fromfile(mol_file, n_data)
                        normals = np.array(normals)
                        normals = normals.reshape(n_mols, 3)
                        rotations = (
                            McellConverter._get_rotation_euler_angles_for_normals(
                                normals, input_data.surface_mol_rotation_angle
                            )
                        )
                        rotations = rotations.reshape(3 * n_mols)
                    else:
                        rotations = np.zeros_like(positions)
                    # append to DataFrame
                    result = result.append(
                        pd.DataFrame(
                            {
                                "time": current_time * np.ones(n_mols),
                                "unique_id": np.arange(n_mols)
                                + total_mols,  # MCell binary format has no IDs
                                "type": np.repeat(display_type_name, n_mols),
                                "positionX": positions[::3],
                                "positionY": positions[1::3],
                                "positionZ": positions[2::3],
                                "rotationX": rotations[::3],
                                "rotationY": rotations[1::3],
                                "rotationZ": rotations[2::3],
                                "radius": input_data.scale_factor
                                * BLENDER_GEOMETRY_SCALE_FACTOR
                                * molecule_info[type_name]["display"]["scale"]
                                * np.ones(n_mols),
                            }
                        )
                    )
                    total_mols += n_mols
                except EOFError:
                    mol_file.close()
                    break
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
        # get the timestep per visualized frame
        n_frames = 0
        for file_name in os.listdir(input_data.path_to_binary_files):
            if "ascii" not in file_name and file_name.endswith(".dat"):
                n_frames += 1
        timestep = float(data_model["mcell"]["initialization"]["time_step"])
        # get metadata for each agent type
        molecule_info = {}
        molecule_list = data_model["mcell"]["define_molecules"]["molecule_list"]
        for molecule in molecule_list:
            molecule_info[molecule["mol_name"]] = molecule
        # read agent data for each frame
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
        for file_name in os.listdir(input_data.path_to_binary_files):
            if "ascii" not in file_name and file_name.endswith(".dat"):
                split_file_name = file_name.split(".")
                time_index = int(split_file_name[split_file_name.index("dat") - 1])
                if time_index % input_data.nth_timestep_to_read != 0:
                    continue
                frame_data = McellConverter._read_binary_cellblender_viz_frame(
                    os.path.join(input_data.path_to_binary_files, file_name),
                    time_index * timestep,
                    molecule_info,
                    columns_list,
                    input_data,
                )
                traj = traj.append(frame_data)
        # get box size
        partitions = data_model["mcell"]["initialization"]["partitions"]
        box_size = np.array(
            [
                float(partitions["x_end"]) - float(partitions["x_start"]),
                float(partitions["y_end"]) - float(partitions["y_start"]),
                float(partitions["z_end"]) - float(partitions["z_start"]),
            ]
        )
        return TrajectoryData(
            meta_data=MetaData(
                box_size=input_data.scale_factor * box_size,
                camera_defaults=input_data.camera_defaults,
            ),
            agent_data=AgentData.from_dataframe(traj),
            time_units=UnitData("s"),
            spatial_units=UnitData("µm", 1.0 / input_data.scale_factor),
            plots=input_data.plots,
        )
