#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import MetaData, DisplayData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MedyanData:
    meta_data: MetaData
    path_to_snapshot: str
    display_info: Dict[str, Dict[int, DisplayData]]
    agents_with_endpoints: List[str]
    draw_fiber_points: bool
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        meta_data: MetaData,
        path_to_snapshot: str,
        filament_display_info: Dict[int, DisplayData] = None,
        linker_display_info: Dict[int, DisplayData] = None,
        motor_display_info: Dict[int, DisplayData] = None,
        agents_with_endpoints: List[str] = None,
        draw_fiber_points: bool = False,
        plots: List[Dict[str, Any]] = None,
    ):
        """
        This object holds simulation trajectory outputs
        from MEDYAN (http://medyan.org/) and plot data

        Parameters
        ----------
        meta_data : MetaData
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        path_to_snapshot : string
            A string path to the MEDYAN snapshot.traj output file
        filament_display_info : Dict[int, DisplayData] (optional)
            A dict mapping MEDYAN type ID for filaments
            to DisplayData, including names and display info
            to use for rendering filament agent types in the Simularium Viewer
            Default: for names, use "filament[type ID]"
                for rendering, use default representation and colors
        linker_display_info : Dict[int, DisplayData] (optional)
            A dict mapping MEDYAN type ID for linkers
            to DisplayData, including names and display info
            to use for rendering linker agent types in the Simularium Viewer
            Default: for names, use "linker[type ID]"
                for rendering, use default representation and colors
        motor_display_info : Dict[int, DisplayData] (optional)
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
        self.meta_data = meta_data
        self.path_to_snapshot = path_to_snapshot
        self.display_info = {
            "filament": filament_display_info
            if filament_display_info is not None
            else {},
            "linker": linker_display_info if linker_display_info is not None else {},
            "motor": motor_display_info if motor_display_info is not None else {},
        }
        self.agents_with_endpoints = (
            agents_with_endpoints if agents_with_endpoints is not None else []
        )
        self.draw_fiber_points = draw_fiber_points
        self.plots = plots if plots is not None else []
