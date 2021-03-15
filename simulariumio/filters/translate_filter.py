#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        max_subpoints = int(np.amax(data.agent_data.n_subpoints)) if data.agent_data.n_subpoints is not None else 0
        # get filtered data
        positions = np.zeros((total_steps, max_agents, 3))
        subpoints = np.zeros((total_steps, max_agents, max_subpoints, 3)) if data.agent_data.n_subpoints is not None else None
        if data.agent_data.type_ids is None:
            data.agent_data.type_ids, tnm = AgentData.get_type_ids_and_mapping(data.agent_data.types)
        for t in range(total_steps):
            for n in range(int(data.agent_data.n_agents[t])):
                if data.agent_data.type_ids[t][n] in self.translation_per_type_id:
                    translation = self.translation_per_type_id[
                        data.agent_data.type_ids[t][n]
                    ]
                else:
                    translation = self.default_translation
                n_subpoints = int(data.agent_data.n_subpoints[t][n]) if data.agent_data.n_subpoints is not None else 0
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
        data.agent_data.positions = positions
        data.agent_data.subpoints = subpoints
        return data
