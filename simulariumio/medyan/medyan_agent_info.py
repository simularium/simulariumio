#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MedyanAgentInfo:
    name: str
    radius: float

    def __init__(self, name: str, radius: float = 1.0):
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
        """
        self.name = name
        self.radius = radius
