#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

from ..data_objects import MetaData, AgentTypeInfo

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MedyanData:
    meta_data: MetaData
    path_to_snapshot: str
    agent_info: Dict[str, Dict[int, AgentTypeInfo]]
    agents_with_endpoints: List[str]
    draw_fiber_points: bool
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        meta_data: MetaData,
        path_to_snapshot: str,
        filament_agent_info: Dict[int, AgentTypeInfo] = None,
        linker_agent_info: Dict[int, AgentTypeInfo] = None,
        motor_agent_info: Dict[int, AgentTypeInfo] = None,
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
        filament_agent_info : Dict[int, AgentTypeInfo] (optional)
            A dict mapping MEDYAN type ID for filaments
            to info (name, radius) for filament agents
        linker_agent_info : Dict[int, AgentTypeInfo] (optional)
            A dict mapping MEDYAN type ID for linkers
            to info (name, radius) for linker agents
        motor_agent_info : Dict[int, AgentTypeInfo] (optional)
            A dict mapping MEDYAN type ID for motors
            to info (name, radius) for motor agents
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
        self.agent_info = {
            "filament": filament_agent_info if filament_agent_info is not None else {},
            "linker": linker_agent_info if linker_agent_info is not None else {},
            "motor": motor_agent_info if motor_agent_info is not None else {},
        }
        self.agents_with_endpoints = (
            agents_with_endpoints if agents_with_endpoints is not None else []
        )
        self.draw_fiber_points = draw_fiber_points
        self.plots = plots if plots is not None else []
