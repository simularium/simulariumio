#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List
import logging

import numpy as np

from .filter import Filter
from ..data_objects import TrajectoryData
from ..exceptions import DataError
from ..constants import VALUES_PER_3D_POINT

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
        if len(axes_mapping) != VALUES_PER_3D_POINT:
            raise DataError(f"axes_mapping must have length {VALUES_PER_3D_POINT}")
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
        data.meta_data.box_size = self._transform_coordinate(
            data.meta_data.box_size, False
        )
        # get dimensions
        start_dimensions = data.agent_data.get_dimensions()
        max_subpoints = int(np.amax(data.agent_data.n_subpoints))
        # get filtered data
        for time_index in range(start_dimensions.total_steps):
            for agent_index in range(int(data.agent_data.n_agents[time_index])):
                data.agent_data.positions[time_index][
                    agent_index
                ] = self._transform_coordinate(
                    data.agent_data.positions[time_index][agent_index]
                )
                # subpoints
                if max_subpoints < 1:
                    continue
                sp_items = self.get_items_from_subpoints(
                    data.agent_data, time_index, agent_index
                )
                if sp_items is None:
                    continue
                n_sp = int(data.agent_data.n_subpoints[time_index][agent_index])
                n_items = sp_items.shape[0]
                for item_index in range(n_items):
                    sp_items[item_index][
                        :VALUES_PER_3D_POINT
                    ] = self._transform_coordinate(
                        sp_items[item_index][:VALUES_PER_3D_POINT]
                    )
                data.agent_data.subpoints[time_index][agent_index][
                    :n_sp
                ] = sp_items.reshape(n_sp)
        return data
