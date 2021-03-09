#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
from typing import Dict
import logging

import numpy as np

from .filter import Filter
from ..data_objects import TrajectoryData, AgentData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class TranslateFilter(Filter):
    translation_per_type_id: Dict[int, np.ndarray]
    default_translation: np.ndarray

    def __init__(
        self,
        translation_per_type_id: Dict[int, np.ndarray] = {},
        default_translation: np.ndarray = np.zeros(3),
    ):
        """
        This object contains parameters for translating 3D positions
        in each frame of simularium data

        Parameters
        ----------
        translation_per_type_id : Dict[int, int]
            translation for agents of each type ID
            Default: {}
        default_translation : int
            translation for any agent types not specified
            in translation_per_type_id
            Default: np.zeros(3)
        """
        self.translation_per_type_id = translation_per_type_id
        self.default_translation = default_translation

    def apply(self, data: TrajectoryData) -> TrajectoryData:
        """
        Add the XYZ translation to all spatial coordinates
        """
        print("Filtering: translation -------------")
        # get dimensions
        total_steps = data.agent_data.times.size
        max_agents = int(np.amax(data.agent_data.n_agents))
        max_subpoints = int(np.amax(data.agent_data.n_subpoints))
        # get filtered data
        positions = np.zeros((total_steps, max_agents, 3))
        subpoints = np.zeros((total_steps, max_agents, max_subpoints, 3))
        # get filtered data
        for t in range(total_steps):
            for n in range(int(data.agent_data.n_agents[t])):
                if data.agent_data.type_ids[t][n] in self.translation_per_type_id:
                    translation = self.translation_per_type_id[
                        data.agent_data.type_ids[t][n]
                    ]
                else:
                    translation = self.default_translation
                n_subpoints = int(data.agent_data.n_subpoints[t][n])
                if n_subpoints > 0:
                    for s in range(int(data.agent_data.n_subpoints[t][n])):
                        for d in range(3):
                            subpoints[t][n][s][d] = (
                                data.agent_data.subpoints[t][n][s][d] + translation[d]
                            )
                else:
                    for d in range(3):
                        positions[t][n][d] = (
                            data.agent_data.positions[t][n][d] + translation[d]
                        )
        return TrajectoryData(
            box_size=np.copy(data.box_size),
            agent_data=AgentData(
                times=np.copy(data.agent_data.times),
                n_agents=np.copy(data.agent_data.n_agents),
                viz_types=np.copy(data.agent_data.viz_types),
                unique_ids=np.copy(data.agent_data.unique_ids),
                types=copy.copy(data.agent_data.types),
                positions=positions,
                radii=np.copy(data.agent_data.radii),
                n_subpoints=np.copy(data.agent_data.n_subpoints),
                subpoints=subpoints,
                draw_fiber_points=data.agent_data.draw_fiber_points,
                type_ids=np.copy(data.agent_data.type_ids),
            ),
            time_units=copy.copy(data.time_units),
            spatial_units=copy.copy(data.spatial_units),
            plots=copy.copy(data.plots),
        )
