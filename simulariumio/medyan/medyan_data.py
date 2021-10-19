#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import MetaData, DisplayData, InputFileData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MedyanData:
    snapshot_file: InputFileData
    meta_data: MetaData
    display_data: Dict[str, Dict[int, DisplayData]]
    agents_with_endpoints: List[str]
    draw_fiber_points: bool
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        snapshot_file: InputFileData,
        meta_data: MetaData = None,
        filament_display_data: Dict[int, DisplayData] = None,
        linker_display_data: Dict[int, DisplayData] = None,
        motor_display_data: Dict[int, DisplayData] = None,
        agents_with_endpoints: List[str] = None,
        draw_fiber_points: bool = False,
        plots: List[Dict[str, Any]] = None,
    ):
        """
        This object holds simulation trajectory outputs
        from MEDYAN (http://medyan.org/) and plot data

        Parameters
        ----------
        snapshot_file : InputFileData
            A InputFileData object containing the string path
            or string contents of the MEDYAN snapshot.traj output file
        meta_data : MetaData (optional)
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        filament_display_data : Dict[int, DisplayData] (optional)
            A dict mapping MEDYAN type ID for filaments
            to DisplayData, including names and display info
            to use for rendering filament agent types in the Simularium Viewer
            Default: for names, use "filament[type ID]"
                for radius, use 1.0,
                for rendering, use default representation and colors
        linker_display_data : Dict[int, DisplayData] (optional)
            A dict mapping MEDYAN type ID for linkers
            to DisplayData, including names and display info
            to use for rendering linker agent types in the Simularium Viewer
            Default: for names, use "linker[type ID]"
                for rendering, use default representation and colors
        motor_display_data : Dict[int, DisplayData] (optional)
            A dict mapping MEDYAN type ID for motors
            to DisplayData, including names and display info
            to use for rendering motor agent types in the Simularium Viewer
            Default: for names, use "motor[type ID]"
                for rendering, use default representation and colors
        agents_with_endpoints: List[str]
            (only used for motors and linkers)
            A list of output agent names for which to draw spheres
            (with 2x radius of the fiber)
            at the end points that define the object
            in addition to a line connecting them
            Default: don't draw any endpoints
        draw_fiber_points : bool (optional)
            (only used for fibers)
            in addition to drawing a line for each fiber,
            also draw spheres at every other point along it?
            Default: False
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.snapshot_file = snapshot_file
        self.meta_data = meta_data if meta_data is not None else MetaData()
        self.display_data = {
            "filament": filament_display_data
            if filament_display_data is not None
            else {},
            "linker": linker_display_data if linker_display_data is not None else {},
            "motor": motor_display_data if motor_display_data is not None else {},
        }
        self.agents_with_endpoints = (
            agents_with_endpoints if agents_with_endpoints is not None else []
        )
        self.draw_fiber_points = draw_fiber_points
        self.plots = plots if plots is not None else []
