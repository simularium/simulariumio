#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List
import logging

import numpy as np

from .filter import Filter
from ..data_objects import TrajectoryData
from ..exceptions import DataError

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class TransformSpatialAxesFilter(Filter):
    axes_mapping: List[str]

    def __init__(
        self,
        axes_mapping: List[str],
    ):
        """
        This filter transforms spatial axes
        to rotate and/or reflect the scene
        in each frame of simularium data

        Parameters
        ----------
        axes_mapping : List[str]
            a list describing how to remap the axes
            e.g. ["+X", "-Z", "+Y"] for [+X, +Y, +Z] -> [+X, -Z, +Y]
            e.g. ["-Z", "-Y", "+X"] for [+X, +Y, +Z] -> [-Z, -Y, +X]
        """
        if len(axes_mapping) != 3:
            raise DataError("axes_mapping must have length 3")
        for d in range(len(axes_mapping)):
            axes_mapping[d] = axes_mapping[d].lower()
        self.axes_mapping = axes_mapping

    def _transform_coordinate(
        self, position: np.ndarray, set_direction: bool = True
    ) -> np.ndarray:
        """
        Transform an +X+Y+Z coordinate according to axes_mapping
        """
        result = np.zeros_like(position)
        for d in range(len(self.axes_mapping)):
            axis = self.axes_mapping[d]
            if "x" in axis:
                result[d] = position[0]
            if "y" in axis:
                result[d] = position[1]
            if "z" in axis:
                result[d] = position[2]
            if set_direction and "-" in axis:
                result[d] *= -1.0
        return result

    def apply(self, data: TrajectoryData) -> TrajectoryData:
        """
        Transform spatial coordinates to rotate and/or reflect the scene
        """
        print(f"Filtering: transform spatial axes {self.axes_mapping} -------------")
        # box size
        box_size = self._transform_coordinate(data.meta_data.box_size, False)
        # get dimensions
        total_steps = data.agent_data.times.size
        max_agents = int(np.amax(data.agent_data.n_agents))
        use_subpoints = data.agent_data.n_subpoints is not None
        if use_subpoints:
            max_subpoints = int(np.amax(data.agent_data.n_subpoints))
            subpoints = np.zeros((total_steps, max_agents, max_subpoints, 3))
        positions = np.zeros((total_steps, max_agents, 3))
        # get filtered data
        for t in range(total_steps):
            for n in range(int(data.agent_data.n_agents[t])):
                positions[t][n] = self._transform_coordinate(
                    data.agent_data.positions[t][n]
                )
                if use_subpoints and data.agent_data.n_subpoints[t][n] > 0:
                    for s in range(int(data.agent_data.n_subpoints[t][n])):
                        subpoints[t][n][s] = self._transform_coordinate(
                            data.agent_data.subpoints[t][n][s]
                        )
        data.meta_data.box_size = box_size
        data.agent_data.positions = positions
        if use_subpoints:
            data.agent_data.subpoints = subpoints
        return data
