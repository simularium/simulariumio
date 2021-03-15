#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MedyanAgentInfo:
    name: str
    radius: float
    draw_endpoints: bool
    endpoint_radius: float

    def __init__(
        self,
        name: str,
        radius: float = 1.0,
        draw_endpoints: bool = False,
        endpoint_radius: float = 1.0,
    ):
        """
        This object contains info about how to display a type of agent

        Parameters
        ----------
        name : str
            A string display name for this type of agent
            Default: "[MEDYAN object type][agent type index from MEDYAN data]"
                e.g. "filament1", "motor0"
        radius : float (optional)
            A float radius for rendering this agent.
            this is the thickness of the line
            Default : 1.0
        draw_points : bool
            Draw spheres at the end points that define the object
            in addition to a line connecting them?
            Default: False
        endpoint_radius : float
            If drawing spheres at the end points that define the object,
            what is their visualized radius?
            Default: 1.0
        """
        self.name = name
        self.radius = radius
        self.draw_endpoints = draw_endpoints
        self.endpoint_radius = endpoint_radius
