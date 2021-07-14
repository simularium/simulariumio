#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from ..data_objects import TrajectoryData, AgentData
from .filter import Filter

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class AddAgentsFilter(Filter):
    new_agent_data: AgentData

    def __init__(self, new_agent_data: AgentData):
        """
        This filter adds the given agents
        to each frame of the simulation

        Parameters
        ----------
        new_agent_data : AgentData
            agent data to append to the trajectory
        """
        self.new_agent_data = new_agent_data

    def apply(self, data: TrajectoryData) -> TrajectoryData:
        """
        Add the given agents to each frame of the simularium data
        """
        print("Filtering: add agents -------------")
        data.append_agents(self.new_agent_data)
        return data
