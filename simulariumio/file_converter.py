#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from typing import Any, Dict

from .trajectory_converter import TrajectoryConverter
from .data_objects import TrajectoryData, UnitData
from .constants import DEFAULT_CAMERA_SETTINGS

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class FileConverter(TrajectoryConverter):
    current_trajectory_info_version: int = 2

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
            < self.current_trajectory_info_version
        ):
            buffer_data = self.update_trajectory_info_version(buffer_data)
        self._data = TrajectoryData.from_buffer_data(buffer_data)

    def update_trajectory_info_version(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the trajectory info block
        to match the current version
        """
        if int(data["trajectoryInfo"]["version"]) == 1:
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
            # default camera transform
            data["trajectoryInfo"]["cameraDefault"] = {
                "position": {
                    "x": DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[0],
                    "y": DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[1],
                    "z": DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[2],
                },
                "lookAtPosition": {
                    "x": DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION[0],
                    "y": DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION[1],
                    "z": DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION[2],
                },
                "upVector": {
                    "x": DEFAULT_CAMERA_SETTINGS.UP_VECTOR[0],
                    "y": DEFAULT_CAMERA_SETTINGS.UP_VECTOR[1],
                    "z": DEFAULT_CAMERA_SETTINGS.UP_VECTOR[2],
                },
                "fovDegrees": DEFAULT_CAMERA_SETTINGS.FOV_DEGREES,
            }
            data["trajectoryInfo"]["version"] = 2
        print(f"Updated TrajectoryInfo v1 -> v{self.current_trajectory_info_version}")
        return data
