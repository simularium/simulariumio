#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict

from .filter_params import FilterParams
from ...data_objects import AgentData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class AddAgentsFilterParams(FilterParams):
    new_agent_data: AgentData

    def __init__(self, new_agent_data : AgentData):
        """
        This object contains parameters for adding 
        the given agents to each frame of the simulation

        Parameters
        ----------
        new_agent_data : AgentData
            agent data to append to the trajectory
        """
        self.name = "add_agents"
        self.new_agent_data = new_agent_data
