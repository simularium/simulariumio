#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Dict, Any
import json
import os

import numpy as np
import pandas as pd

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import TrajectoryData, AgentData, MetaData, UnitData
from .mcell_data import McellData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


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
    def _read_binary_cellblender_viz_frame(
        file_name: str,
        current_time: float,
        molecule_info: Dict[str, Dict[str, Any]],
        display_names: Dict[str, str],
        columns_list: List[str],
    ) -> pd.DataFrame:
        """
        Read MCell binary visualization files

        code based on cellblender/cellblender_mol_viz.py function mol_viz_file_read
        """
        result = pd.DataFrame([], columns=columns_list)
        with open(file_name, "rb") as mol_file:
            # first 4 bytes must contain value '1'
            is_binary = np.fromfile(mol_file, dtype=bytes, count=1)[0] == 1
            assert is_binary
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
                    n_chars_type_name = np.fromfile(mol_file, dtype=bytes, count=1)[0]
                    type_name_chars_array = np.fromfile(
                        mol_file, dtype=bytes, count=n_chars_type_name
                    )
                    type_name = np.array2string(
                        type_name_chars_array, formatter={"str_kind": lambda x: x}
                    ).replace(" ", "")[1:-1]
                    display_type_name = (
                        display_names[type_name]
                        if type_name in display_names
                        else type_name
                    )
                    # get positions and rotations
                    is_surface_mol = np.fromfile(mol_file, dtype=bytes, count=1)[0] == 1
                    n_data = np.fromfile(mol_file, dtype=int, count=1)[0]
                    n_mol = int(n_data / 3.0)
                    positions = np.fromfile(mol_file, dtype=float, count=n_data)
                    if is_surface_mol:
                        normals = np.fromfile(mol_file, dtype=float, count=n_data)
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
                                "time": current_time,
                                "unique_id": np.arange(n_mol),
                                "type": display_type_name,
                                "positionX": positions[::3],
                                "positionY": positions[1::3],
                                "positionZ": positions[2::3],
                                "rotationX": rotations[::3],
                                "rotationY": rotations[1::3],
                                "rotationZ": rotations[2::3],
                                "radius": molecule_info[type_name]["display"]["scale"],
                            }
                        )
                    )
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
        total_steps = int(data_model["mcell"]["initialization"]["file_stop_index"])
        frame_timestep = (timestep * total_steps) / float(n_frames)
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
                frame_data = McellConverter._read_binary_cellblender_viz_frame(
                    os.path.join(input_data.path_to_binary_files, file_name),
                    time_index * frame_timestep,
                    molecule_info,
                    input_data.display_names,
                    columns_list,
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
