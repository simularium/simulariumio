#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from .cytosim_object_info import CytosimObjectInfo
from ..data_objects import MetaData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CytosimData:
    object_info: Dict[str, CytosimObjectInfo]
    meta_data: MetaData
    draw_fiber_points: bool
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        object_info: Dict[str, CytosimObjectInfo],
        meta_data: MetaData = None,
        draw_fiber_points: bool = False,
        plots: List[Dict[str, Any]] = None,
    ):
        """
        This object holds simulation trajectory outputs
        from CytoSim (https://gitlab.com/f.nedelec/cytosim)
        and plot data

        Parameters
        ----------
        object_info : Dict[str, CytosimObjectInfo]
            A dict mapping Cytosim object type
            (either "fibers", "solids", "singles", or "couples")
            to info for reading and rendering the Cytosim data
            for agents of that object type
        meta_data : MetaData
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        draw_fiber_points : bool (optional)
            (only used for fibers)
            in addition to drawing a line for each fiber,
            also draw spheres at every other point along it?
            Default: False
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.object_info = object_info
        self.meta_data = meta_data if meta_data is not None else MetaData()
        self.draw_fiber_points = draw_fiber_points
        self.plots = plots if plots is not None else []
