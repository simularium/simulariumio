#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import logging


###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class DimensionData:
    total_steps: int
    max_agents: int
    max_subpoints: int

    def __init__(
        self,
        total_steps: int,
        max_agents: int,
        max_subpoints: int = 0,
    ):
        """
        This object contains dimension data

        Parameters
        ----------
        total_steps : int
            The total number of timesteps in a trajectory
        max_agents : int
            The number of agents per timestep
        max_subpoints : int (optional)
            The number of subpoints per agent
            Default: 0
        """
        self.total_steps = total_steps
        self.max_agents = max_agents
        self.max_subpoints = max_subpoints

    def add(self, added_dimensions: DimensionData):
        """
        Add the given dimensions to this object's
        """
        self.total_steps += added_dimensions.total_steps
        self.max_agents += added_dimensions.max_agents
        self.max_subpoints += added_dimensions.max_subpoints

    def __str__(self):
        return (
            f"{self.total_steps} timesteps X {self.max_agents} agents "
            f"X {self.max_subpoints} subpoints"
        )

    def __eq__(self, other):
        if isinstance(other, DimensionData):
            return (
                self.total_steps == other.total_steps
                and self.max_agents == other.max_agents
                and self.max_subpoints == other.max_subpoints
            )
        return False
