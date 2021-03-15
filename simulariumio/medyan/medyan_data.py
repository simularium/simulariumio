#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

import numpy as np

from .medyan_agent_info import MedyanAgentInfo

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MedyanData:
    box_size: np.ndarray
    path_to_snapshot: str
    agent_info: Dict[str, Dict[int, MedyanAgentInfo]]
    draw_fiber_points: bool
    scale_factor: float
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        box_size: np.ndarray,
        path_to_snapshot: str,
        filament_agent_info: Dict[int, MedyanAgentInfo] = {},
        linker_agent_info: Dict[int, MedyanAgentInfo] = {},
        motor_agent_info: Dict[int, MedyanAgentInfo] = {},
        draw_fiber_points: bool = False,
        scale_factor: float = 1.0,
        plots: List[Dict[str, Any]] = [],
    ):
        """
        This object holds simulation trajectory outputs
        from MEDYAN (http://medyan.org/) and plot data

        Parameters
        ----------
        box_size : np.ndarray (shape = [3])
            A numpy ndarray containing the XYZ dimensions
            of the cubic simulation bounding volume
        path_to_snapshot : string
            A string path to the MEDYAN snapshot.traj output file
        filament_agent_info : Dict[int, MedyanAgentInfo] (optional)
            A dict mapping MEDYAN type ID for filaments
            to info (name, radius) for filament agents
        linker_agent_info : Dict[int, MedyanAgentInfo] (optional)
            A dict mapping MEDYAN type ID for linkers
            to info (name, radius) for linker agents
        motor_agent_info : Dict[int, MedyanAgentInfo] (optional)
            A dict mapping MEDYAN type ID for motors
            to info (name, radius) for motor agents
        draw_fiber_points : bool (optional)
            (only used for fibers)
            in addition to drawing a line for each fiber,
            also draw spheres at every other point along it?
            Default: False
        scale_factor : float (optional)
            A multiplier for the MEDYAN scene, use if
            visualization is too large or small
            Default: 1.0
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.box_size = box_size
        self.path_to_snapshot = path_to_snapshot
        self.agent_info = {
            "filament": filament_agent_info,
            "linker": linker_agent_info,
            "motor": motor_agent_info,
        }
        self.draw_fiber_points = draw_fiber_points
        self.scale_factor = scale_factor
        self.plots = plots
