#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

import numpy as np

from .cytosim_object_info import CytosimObjectInfo

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CytosimData:
    box_size: np.ndarray
    object_info: Dict[str, CytosimObjectInfo]
    draw_fiber_points: bool
    scale_factor: float
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        box_size: np.ndarray,
        object_info: Dict[str, CytosimObjectInfo],
        draw_fiber_points: bool = False,
        scale_factor: float = 1.0,
        plots: List[Dict[str, Any]] = [],
    ):
        """
        This object holds simulation trajectory outputs
        from CytoSim (https://gitlab.com/f.nedelec/cytosim)
        and plot data

        Parameters
        ----------
        box_size : np.ndarray (shape = [3])
            A numpy ndarray containing the XYZ dimensions
            of the simulation bounding volume
        object_info : Dict[str, CytosimObjectInfo]
            A dict mapping Cytosim object type
            (either "fibers", "solids", "singles", or "couples")
            to info for reading the Cytosim data for agents
            of that object type
        draw_fiber_points : bool (optional)
            (only used for fibers)
            in addition to drawing a line for each fiber,
            also draw spheres at every other point along it?
            Default: False
        scale_factor : float (optional)
            A multiplier for the Cytosim scene, use if
            visualization is too large or small
            Default: 1.0
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.box_size = box_size
        self.object_info = object_info
        self.draw_fiber_points = draw_fiber_points
        self.scale_factor = scale_factor
        self.plots = plots
