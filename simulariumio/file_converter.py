#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from typing import Any, Dict

from .trajectory_converter import TrajectoryConverter
from .data_objects import TrajectoryData, UnitData
from .constants import CURRENT_VERSION

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class FileConverter(TrajectoryConverter):
    def __init__(self, input_path: str):
        """
        This object loads the data in .simularium JSON format
        at the input path

        Parameters
        ----------
        input_path: str
            path to the .simularium JSON file to load
        """
        print("Reading Simularium JSON -------------")
        with open(input_path) as simularium_file:
            buffer_data = json.load(simularium_file)
        if (
            int(buffer_data["trajectoryInfo"]["version"])
            < CURRENT_VERSION.TRAJECTORY_INFO
        ):
            buffer_data = self.update_trajectory_info_version(buffer_data)
        self._data = TrajectoryData.from_buffer_data(buffer_data)

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
