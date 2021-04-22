#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Dict, Any
import json
import os
import array
import codecs

import numpy as np
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
    def _get_rotation_euler_angles_for_normals(normals: np.ndarray) -> np.ndarray:
        """
        TODO
        Generate a random orientation around the normal
        and return its euler angles
        """
        return normals

    @staticmethod
    def _convert_ubytes_to_string(ubyte_array: np.ndarray) -> str:
        """
        Convert a numpy array of unsigned char to a string
        """
        decoder = codecs.getdecoder("utf-8")
        return np.array([decoder(item)[0] for item in ubyte_array], dtype="unicode")[0]

    @staticmethod
    def _read_binary_cellblender_viz_frame(
        file_name: str,
        current_time: float,
        molecule_info: Dict[str, Dict[str, Any]],
        display_names: Dict[str, str],
        columns_list: List[str],
        scale_factor: float,
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
                        display_names[type_name]
                        if type_name in display_names
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
                    positions = scale_factor * np.array(positions)
                    if is_surface_mol:
                        normals = array.array("f")
                        normals.fromfile(mol_file, n_data)
                        normals = np.array(normals)
                        rotations = (
                            McellConverter._get_rotation_euler_angles_for_normals(
                                normals
                            )
                        )
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
                                "radius": scale_factor
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
                    input_data.display_names,
                    columns_list,
                    input_data.scale_factor,
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
