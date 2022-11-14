#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import (
    MetaData,
    UnitData,
    DisplayData,
    InputFileData,
)
from ..utils import unpack_display_data

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
    def from_dict(
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
        if "displayData" in buffer_data:
            display_data = unpack_display_data(buffer_data["displayData"])

        spatial_units = None
        if "spatialUnits" in buffer_data:
            # spatial units defaults to meter in the UI
            spatial_units = UnitData.from_dict(
                buffer_data["spatialUnits"],
                default_name="meter",
                default_mag=1.0
            )

        time_units = None
        if "timeUnits" in buffer_data:
            # time units default to seconds on UI
            time_units = UnitData.from_dict(
                buffer_data["timeUnits"],
                default_name="second",
                default_mag=1.0
            )

        return cls(
            meta_data=MetaData.from_dict(buffer_data.get("metaData")),
            smoldyn_file=InputFileData(
                file_contents=buffer_data["fileContents"]["fileContents"],
            ),
            display_data=display_data,
            time_units=time_units,
            spatial_units=spatial_units,
        )
