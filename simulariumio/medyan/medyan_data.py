#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from .medyan_agent_info import MedyanAgentInfo
from ..data_objects import MetaData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MedyanData:
    meta_data: MetaData
    path_to_snapshot: str
    agent_info: Dict[str, Dict[int, MedyanAgentInfo]]
    draw_fiber_points: bool
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        meta_data: MetaData,
        path_to_snapshot: str,
        filament_agent_info: Dict[int, MedyanAgentInfo] = {},
        linker_agent_info: Dict[int, MedyanAgentInfo] = {},
        motor_agent_info: Dict[int, MedyanAgentInfo] = {},
        draw_fiber_points: bool = False,
        plots: List[Dict[str, Any]] = [],
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
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.meta_data = meta_data
        self.path_to_snapshot = path_to_snapshot
        self.agent_info = {
            "filament": filament_agent_info,
            "linker": linker_agent_info,
            "motor": motor_agent_info,
        }
        self.draw_fiber_points = draw_fiber_points
        self.plots = plots
