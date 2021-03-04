#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from typing import Any, Dict

from .custom_converter import CustomConverter
from .data_objects import CustomData, UnitData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class FileConverter(CustomConverter):
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
        self._data = CustomData.from_buffer_data(buffer_data)

    def update_trajectory_info_version(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the trajectory info block
        to match the current version
        """
        if int(data["trajectoryInfo"]["version"]) == 1:
            spatial_units = UnitData(
                "m", data["trajectoryInfo"]["spatialUnitFactorMeters"]
            )
            data["trajectoryInfo"]["spatialUnits"] = {
                "magnitude": spatial_units.magnitude,
                "name": spatial_units.name,
            }
            data["trajectoryInfo"].pop("spatialUnitFactorMeters")
            time_units = UnitData("s", 1.0)
            data["trajectoryInfo"]["timeUnits"] = {
                "magnitude": time_units.magnitude,
                "name": time_units.name,
            }
            data["trajectoryInfo"]["version"] = 2
            print(
                f"Updated TrajectoryInfo v1 -> v{self.current_trajectory_info_version}"
            )
        return data
