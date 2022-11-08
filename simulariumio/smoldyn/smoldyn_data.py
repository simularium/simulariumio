#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import numpy as np
from typing import Any, Dict, List

from ..data_objects import (
    MetaData,
    ModelMetaData,
    UnitData,
    DisplayData,
    InputFileData,
    CameraData
)
from ..constants import DISPLAY_TYPE, DEFAULT_CAMERA_SETTINGS, DEFAULT_BOX_SIZE

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class SmoldynData:
    smoldyn_file: InputFileData
    meta_data: MetaData
    display_data: Dict[str, DisplayData]
    time_units: UnitData
    spatial_units: UnitData
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        smoldyn_file: InputFileData,
        meta_data: MetaData = None,
        display_data: Dict[str, DisplayData] = None,
        time_units: UnitData = None,
        spatial_units: UnitData = None,
        plots: List[Dict[str, Any]] = None,
    ):
        """
        This object holds simulation trajectory outputs
        from Smoldyn (http://www.smoldyn.org) and plot data

        Parameters
        ----------
        smoldyn_file: InputFileData
            A InputFileData object containing the string path
            or string contents of the Smoldyn output txt file.
            Generate by adding to your config.txt file:
                `output_files output.txt
                `cmd n 1 executiontime output.txt`
                `cmd n 1 listmols output.txt`
        meta_data : MetaData (optional)
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        display_data: Dict[str, DisplayData] (optional)
            The particle type name from Smoldyn data mapped
            to display names and rendering info for that type,
            Default: for names, use Smoldyn name,
                for radius, use 1.0,
                for rendering, use default representations and colors
        time_units: UnitData (optional)
            multiplier and unit name for time values
            Default: 1.0 second
        spatial_units: UnitData (optional)
            multiplier and unit name for spatial values
            (including positions, radii, and box size)
            Default: 1.0 meter
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.smoldyn_file = smoldyn_file
        self.meta_data = meta_data if meta_data is not None else MetaData()
        self.display_data = display_data if display_data is not None else {}
        self.time_units = time_units if time_units is not None else UnitData("s")
        self.spatial_units = (
            spatial_units if spatial_units is not None else UnitData("m")
        )
        self.plots = plots if plots is not None else []

    @classmethod
    def from_buffer_data(
        cls, buffer_data: Dict[str, Any]
    ):
        """
        Create SmoldynData from a simularium JSON dict containing buffers

        Parameters
        ----------
        buffer_data: Dict[str, Any]
            JSON dict containing values key value pairs representing the
            data to be turned into a SmoldynData object
        """
        display_data = None
        camera_data = None
        box_size = None
        model_meta_data = None
        if "display_data" in buffer_data:
            display_data = dict()
            for index in buffer_data["display_data"]:
                agent_info = buffer_data["display_data"][index]
                for agent_name in agent_info:
                    agent_data = agent_info[agent_name]
                    display_data[agent_name] = DisplayData(
                        name=agent_data.get("name"),
                        radius=float(agent_data.get("radius", 1.0)),
                        display_type=agent_data.get(
                            "display_type",
                            DISPLAY_TYPE.SPHERE
                        ),
                        url=agent_data.get("url"),
                        color=agent_data.get("color"),
                    )
        if "meta_data" in buffer_data:
            metadata = buffer_data["meta_data"]
            if "box_size" in metadata:
                box_size = SmoldynData._unpack_position_vector(
                    metadata["box_size"],
                    DEFAULT_BOX_SIZE
                )

            if "camera_defaults" in metadata:
                camera_defaults = metadata["camera_defaults"]
                camera_data = CameraData.from_buffer_data(camera_defaults)

            if "model_meta_data" in metadata:
                model_data = metadata["model_meta_data"]
                model_meta_data = ModelMetaData.from_buffer_data(model_data)

        spatial_units = None
        if "spatial_units" in buffer_data:
            # spatial units defaults to meters on UI
            name = (
                buffer_data["spatial_units"]["name"]
                if "name" in buffer_data["spatial_units"]
                else "meter")

            if "magnitude" in buffer_data["spatial_units"]:
                spatial_units = UnitData(
                    name,
                    float(buffer_data["spatial_units"]["magnitude"])
                )
            else:
                spatial_units = UnitData(name)

        time_units = None
        if "time_units" in buffer_data:
            # time units default to seconds on UI
            name = (
                buffer_data["time_units"]["name"]
                if "name" in buffer_data["time_units"]
                else "second")

            if "magnitude" in buffer_data["time_units"]:
                time_units = UnitData(
                    name,
                    float(buffer_data["time_units"]["magnitude"])
                )
            else:
                time_units = UnitData(name)

        return cls(
            meta_data=MetaData(
                box_size=box_size,
                trajectory_title=buffer_data.get("trajectory_title", ""),
                scale_factor=float(buffer_data.get("scale_factor", 1.0)),
                camera_defaults=camera_data,
                model_meta_data=model_meta_data,
            ),
            smoldyn_file=InputFileData(
                file_contents=buffer_data["file_contents"]["file_contents"],
            ),
            display_data=display_data,
            time_units=time_units,
            spatial_units=spatial_units,
        )

    @staticmethod
    def _unpack_position_vector(
        vector_dict: Dict[str, str], defaults: np.ndarray
    ) -> np.ndarray:
        # if no vector information was given, go with the defaults
        if vector_dict is None:
            return defaults

        # use all positions given, but use defaults if any are missing
        return np.array(
            [
                float(vector_dict.get("0", defaults[0])),
                float(vector_dict.get("1", defaults[1])),
                float(vector_dict.get("2", defaults[2])),
            ]
        )
