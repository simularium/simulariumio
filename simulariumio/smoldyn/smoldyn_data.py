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
from ..exceptions import DataError

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
    center: bool

    def __init__(
        self,
        smoldyn_file: InputFileData,
        meta_data: MetaData = None,
        display_data: Dict[str, DisplayData] = None,
        time_units: UnitData = None,
        spatial_units: UnitData = None,
        plots: List[Dict[str, Any]] = None,
        center: bool = True,
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
        center : bool (optional)
            If true, the spatial values of the data are centered
            around the origin (0, 0, 0) during conversion
            Default: True
        """
        self.smoldyn_file = smoldyn_file
        self.meta_data = meta_data if meta_data is not None else MetaData()
        self.display_data = display_data if display_data is not None else {}
        self.time_units = time_units if time_units is not None else UnitData("s")
        self.spatial_units = (
            spatial_units if spatial_units is not None else UnitData("m")
        )
        self.plots = plots if plots is not None else []
        self.center = center

    @classmethod
    def from_dict(
        cls, smoldyn_info: Dict[str, Any]
    ):
        """
        Create SmoldynData from a simularium JSON dict

        Parameters
        ----------
        smoldyn_info: Dict[str, Any]
            JSON dict containing values key value pairs representing the
            data to be turned into a SmoldynData object
        """
        if (
            "fileContents" not in smoldyn_info
            or ("fileContents" not in smoldyn_info["fileContents"]
                and "filePath" not in smoldyn_info["fileContents"])
        ):
            raise DataError(
                "File contents or file path must be provided "
                "to create a SmoldynData object"
            )
        display_data = None
        if "displayData" in smoldyn_info:
            display_data = unpack_display_data(smoldyn_info["displayData"])

        spatial_units = None
        if "spatialUnits" in smoldyn_info:
            # spatial units defaults to meter in the UI
            spatial_units = UnitData.from_dict(
                smoldyn_info["spatialUnits"],
                default_name="meter",
                default_mag=1.0
            )

        time_units = None
        if "timeUnits" in smoldyn_info:
            # time units default to seconds on UI
            time_units = UnitData.from_dict(
                smoldyn_info["timeUnits"],
                default_name="second",
                default_mag=1.0
            )

        return cls(
            meta_data=MetaData.from_dict(smoldyn_info.get("metaData")),
            smoldyn_file=InputFileData(
                file_contents=smoldyn_info["fileContents"].get("fileContents"),
                file_path=smoldyn_info["fileContents"].get("filePath")
            ),
            display_data=display_data,
            time_units=time_units,
            spatial_units=spatial_units,
        )

    def __eq__(self, other):
        if isinstance(other, SmoldynData):
            return (
                self.smoldyn_file.get_contents() == other.smoldyn_file.get_contents()
                and self.meta_data == other.meta_data
                and self.display_data == other.display_data
                and self.time_units == other.time_units
                and self.spatial_units == other.spatial_units
                and self.plots == other.plots
            )
        return False
