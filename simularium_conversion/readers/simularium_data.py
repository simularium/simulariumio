#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List

###############################################################################

log = logging.getLogger(__name__)

###############################################################################

class SimulariumData:
    times: np.ndarray = None
    n_agents: np.ndarray = None
    positions: np.ndarray = None
    types: List[str] = None
    radii: np.ndarray = None

    def __init__(
        self, 
        times: np.ndarray, 
        max_n_agents: number, 
        positions: np.ndarray, 
        types: List[str], 
        radii: np.ndarray
    ):
        '''
        This object stores trajectory data in a shape that's 
        ready to write to .simularium JSON

        Parameters
        ----------
        times: np.ndarray (shape = [timesteps])
            A numpy ndarray containing the elapsed simulated time at each timestep

        max_n_agents: number
            The maximum number of agents that exist at any one timestep
                
        positions : np.ndarray (shape = [timesteps, agents, 3])
            A numpy ndarray containing the XYZ position for each agent at each timestep
                
        types: List[str] (list of shape [timesteps, agents])
            A list containing the string name for the type of each agent at each timestep
                
        radii : np.ndarray (shape = [timesteps, agents])
            A numpy ndarray containing the radius for each agent at each timestep
        '''
        self.times = times
        self.max_n_agents = max_n_agents
        self.positions = positions
        self.types = types
        self.radii = radii