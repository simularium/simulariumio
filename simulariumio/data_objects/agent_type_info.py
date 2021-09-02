#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from .display_data import DisplayData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class AgentTypeInfo:
    name: str
    radius: float
    display_data: DisplayData

    def __init__(
        self, name: str, radius: float = None, display_data: DisplayData = None
    ):
        """
        This object contains info about how to display a type of agent

        Parameters
        ----------
        name : str
            A string display name for this type of agent
            Default: use names from simulator data if possible
        radius : float (optional)
            A float radius for rendering this agent.
            For fibers, this is the thickness of the line
            For default agents, this is the scale of the representation
            Default : 1.0
        display_data: DisplayData (optional)
            Information about how to render this type of agent
            Default: None
        """
        self.name = name
        self.radius = radius
        self.display_data = display_data
