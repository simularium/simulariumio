#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from typing import Any, Dict

from .trajectory_converter import TrajectoryConverter
from .data_objects import TrajectoryData, UnitData, InputFileData, DisplayData
from .constants import CURRENT_VERSION
from .readers import SimulariumBinaryReader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class FileConverter(TrajectoryConverter):
    def __init__(
        self, input_file: InputFileData, display_data: Dict[int, DisplayData] = None
    ):
        """
        This object loads data from the input file in .simularium format.

        Parameters
        ----------
        input_file: InputFileData
            A InputFileData object containing .simularium data to load
        """
        if display_data is None:
            display_data = {}
        if input_file._is_binary():
            print("Reading Simularium binary -------------")
            buffer_data = SimulariumBinaryReader.load_binary(input_file)
        else:
            print("Reading Simularium JSON -------------")
            buffer_data = json.loads(input_file.get_contents())
        if (
            int(buffer_data["trajectoryInfo"]["version"])
            < CURRENT_VERSION.TRAJECTORY_INFO
        ):
            buffer_data = FileConverter.update_trajectory_info_version(buffer_data)
        self._data = TrajectoryData.from_buffer_data(buffer_data, display_data)

    @staticmethod
    def _update_trajectory_info_v1_to_v2(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the trajectory info block from v1 to v2
        """
        # units
        if "spatialUnitFactorMeters" in data["trajectoryInfo"]:
            spatial_units = UnitData(
                "m", data["trajectoryInfo"]["spatialUnitFactorMeters"]
            )
            data["trajectoryInfo"].pop("spatialUnitFactorMeters")
        else:
            spatial_units = UnitData("m")
        data["trajectoryInfo"]["spatialUnits"] = {
            "magnitude": spatial_units.magnitude,
            "name": spatial_units.name,
        }
        time_units = UnitData("s", 1.0)
        data["trajectoryInfo"]["timeUnits"] = {
            "magnitude": time_units.magnitude,
            "name": time_units.name,
        }
        data["trajectoryInfo"]["version"] = 2
        return data

    @staticmethod
    def _update_trajectory_info_v2_to_v3(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the trajectory info block from v2 to v3
        """
        # all the new fields from v2 to v3 are optional
        data["trajectoryInfo"]["version"] = 3
        return data

    @staticmethod
    def update_trajectory_info_version(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the trajectory info block
        to match the current version

        Parameters
        ----------
        data: Dict[str, Any]
            A .simularium JSON file loaded in memory as a Dict.
            This object will be mutated, not copied.
        """
        original_version = int(data["trajectoryInfo"]["version"])
        if original_version == 1:
            data = FileConverter._update_trajectory_info_v1_to_v2(data)
            data = FileConverter._update_trajectory_info_v2_to_v3(data)
        if original_version == 2:
            data = FileConverter._update_trajectory_info_v2_to_v3(data)
        print(
            f"Updated TrajectoryInfo v{original_version} -> "
            f"v{CURRENT_VERSION.TRAJECTORY_INFO}"
        )
        return data
