#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict
import logging

import numpy as np

from .filter import Filter
from ..data_objects import TrajectoryData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class TranslateFilter(Filter):
    translation_per_type: Dict[str, np.ndarray]
    default_translation: np.ndarray

    def __init__(
        self,
        translation_per_type: Dict[str, np.ndarray] = None,
        default_translation: np.ndarray = np.zeros(3),
    ):
        """
        This object contains parameters for translating 3D positions
        in each frame of simularium data

        Parameters
        ----------
        translation_per_type : Dict[str, int]
            translation for agents of each type
            Default: {}
        default_translation : int
            translation for any agent types not specified
            in translation_per_type
            Default: np.zeros(3)
        """
        self.translation_per_type = (
            translation_per_type if translation_per_type is not None else {}
        )
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
        for time_index in range(total_steps):
            for agent_index in range(int(data.agent_data.n_agents[time_index])):
                if (
                    data.agent_data.types[time_index][agent_index]
                    in self.translation_per_type
                ):
                    translation = self.translation_per_type[
                        data.agent_data.types[time_index][agent_index]
                    ]
                else:
                    translation = self.default_translation
                n_subpoints = int(data.agent_data.n_subpoints[time_index][agent_index])
                if n_subpoints > 0:
                    for subpoint_index in range(
                        int(data.agent_data.n_subpoints[time_index][agent_index])
                    ):
                        for dim in range(3):
                            subpoints[time_index][agent_index][subpoint_index][dim] = (
                                data.agent_data.subpoints[time_index][agent_index][
                                    subpoint_index
                                ][dim]
                                + translation[dim]
                            )
                else:
                    for dim in range(3):
                        positions[time_index][agent_index][dim] = (
                            data.agent_data.positions[time_index][agent_index][dim]
                            + translation[dim]
                        )
        data.agent_data.positions = positions
        data.agent_data.subpoints = subpoints
        return data
