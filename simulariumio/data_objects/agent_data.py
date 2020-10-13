#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List

import numpy as np

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class AgentData:
    times: np.ndarray
    n_agents: np.ndarray
    viz_types: np.ndarray
    unique_ids: np.ndarray
    types: List[List[str]]
    type_ids: np.ndarray
    positions: np.ndarray
    radii: np.ndarray
    n_subpoints: np.ndarray = None
    subpoints: np.ndarray = None
    draw_fiber_points: bool = False

    def __init__(
        self,
        times: np.ndarray,
        n_agents: np.ndarray,
        viz_types: np.ndarray,
        unique_ids: np.ndarray,
        types: List[List[str]],
        positions: np.ndarray,
        radii: np.ndarray,
        n_subpoints: np.ndarray = None,
        subpoints: np.ndarray = None,
        draw_fiber_points: bool = False,
    ):
        """
        This object contains custom simulation trajectory outputs
        and plot data

        Parameters
        ----------
        times : np.ndarray (shape = [timesteps])
            A numpy ndarray containing the elapsed simulated time
            at each timestep
        n_agents : np.ndarray (shape = [timesteps])
            A numpy ndarray containing the number of agents
            that exist at each timestep
        viz_types : np.ndarray (shape = [timesteps, agents])
            A numpy ndarray containing the viz type
            for each agent at each timestep. Current options:
                1000 : default,
                1001 : fiber (which will require subpoints)
        unique_ids : np.ndarray (shape = [timesteps, agents])
            A numpy ndarray containing the unique ID
            for each agent at each timestep
        types : List[List[str]] (list of shape [timesteps, agents])
            A list containing timesteps, for each a list of
            the string name for the type of each agent
        positions : np.ndarray (shape = [timesteps, agents, 3])
            A numpy ndarray containing the XYZ position
            for each agent at each timestep
        radii : np.ndarray (shape = [timesteps, agents])
            A numpy ndarray containing the radius
            for each agent at each timestep
        n_subpoints : np.ndarray (shape = [timesteps, agents]) (optional)
            A numpy ndarray containing the number of subpoints
            belonging to each agent at each timestep. Required if
            subpoints are provided
            Default: None
        subpoints : np.ndarray
        (shape = [timesteps, agents, subpoints, 3]) (optional)
            A numpy ndarray containing a list of subpoint position data
            for each agent at each timestep. These values are
            currently only used for fiber agents
            Default: None
        draw_fiber_points: bool (optional)
            Draw spheres at every other fiber point for fibers?
            Default: False
        """
        self.times = times
        self.n_agents = n_agents
        self.viz_types = viz_types
        self.unique_ids = unique_ids
        self.types = types
        self.positions = positions
        self.radii = radii
        self.n_subpoints = n_subpoints
        self.subpoints = subpoints
        self.draw_fiber_points = draw_fiber_points
