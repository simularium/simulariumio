#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum
import logging
from typing import Any, Dict, List

from ..data_objects import MetaData, UnitData, DisplayData, InputFileData
from ..constants import DISPLAY_TYPE

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class HAND_TYPE(Enum):
    RIGHT = "RIGHT"
    LEFT = "LEFT"


class CellpackData:
    results_file: InputFileData
    recipe_file_path: str
    meta_data: MetaData
    display_data: Dict[str, DisplayData]
    geometry_type: DISPLAY_TYPE
    time_units: UnitData
    spatial_units: UnitData
    plots: List[Dict[str, Any]]
    handedness: HAND_TYPE
    geometry_url: str

    def __init__(
        self,
        results_file: InputFileData,
        recipe_file_path: str,
        meta_data: MetaData = None,
        display_data: Dict[str, DisplayData] = None,
        geometry_type: DISPLAY_TYPE = DISPLAY_TYPE.PDB,
        time_units: UnitData = None,
        spatial_units: UnitData = None,
        plots: List[Dict[str, Any]] = None,
        handedness: HAND_TYPE = HAND_TYPE.RIGHT,
        geometry_url: str = None,
    ):
        """
        This object holds simulation trajectory outputs
        from Cellpack (http://www.cellpack.org) and plot data

        Parameters
        ----------
        results_file: InputFileData
            A InputFileData object containing the string path
            or string contents of the Cellpack results output txt file.
        recipe_file_path: str
            A InputFileData object containing the string path
            or string contents of a Cellpack recipe that was used to
            produce the results_file. The recipe name must match in both
            files for the converter to run.
        meta_data: MetaData (optional)
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
            NOTE: When passing in a scale_factor use the number relative to a normal
            cellPACK recipe, it will be scaled an additional 10% because of the
            conversion from cellPACK to Simularium.
        display_data: Dict[str, DisplayData] (optional)
            A dictionary containing any per agent/ingredient display overrides,
            Ie, if the ingredients are all going to be displayed as PDBs, except
            for some.
        geometry_type: DISPLAY_TYPE
            The display type to use for the ingredients
        time_units: UnitData (optional)
            multiplier and unit name for time values
            Default: 1.0 second
        spatial_units: UnitData (optional)
            multiplier and unit name for spatial values
            (including positions, radii, and box size)
            Default: 1.0 meter
        plots: List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        handedness: HAND_TYPE (optional)
            The handedness of the data's coordinate system
            Default: HAND_TYPE.RIGHT
        geometry_url: str (optional)
            The base URL for all geometry files
            Default: https://raw.githubusercontent.com/mesoscope/cellPACK_data/master/cellPACK_database_1.1.0/geometries/  # noqa: E501
        """
        self.results_file = results_file
        self.recipe_file_path = recipe_file_path
        self.geometry_type = geometry_type
        self.meta_data = meta_data if meta_data is not None else MetaData()
        self.display_data = display_data if display_data is not None else {}
        self.time_units = time_units if time_units is not None else UnitData("s")
        self.spatial_units = (
            spatial_units if spatial_units is not None else UnitData("m")
        )
        self.plots = plots if plots is not None else []
        self.handedness = handedness
        self.geometry_url = geometry_url
