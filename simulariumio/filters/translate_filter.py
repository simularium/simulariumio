#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict
import logging

import numpy as np

from .filter import Filter
from ..data_objects import TrajectoryData
from ..constants import DISPLAY_TYPE, VALUES_PER_3D_POINT

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class TranslateFilter(Filter):
    translation_per_type: Dict[str, np.ndarray]
    default_translation: np.ndarray

    def __init__(
        self,
        translation_per_type: Dict[str, np.ndarray] = None,
        default_translation: np.ndarray = np.zeros(VALUES_PER_3D_POINT),
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
        max_subpoints = int(np.amax(data.agent_data.n_subpoints))
        # get filtered data
        for time_index in range(total_steps):
            for agent_index in range(int(data.agent_data.n_agents[time_index])):
                # get translation for this agent
                if (
                    data.agent_data.types[time_index][agent_index]
                    in self.translation_per_type
                ):
                    translation = self.translation_per_type[
                        data.agent_data.types[time_index][agent_index]
                    ]
                else:
                    translation = self.default_translation
                # apply translation
                display_type = data.agent_data.display_type_for_agent(
                    time_index, agent_index
                )
                translate_subpoints = (
                    max_subpoints > 0 and display_type != DISPLAY_TYPE.SPHERE_GROUP
                )
                if translate_subpoints:
                    sp_items = self.get_items_from_subpoints(
                        data.agent_data, time_index, agent_index
                    )
                    if sp_items is None:
                        translate_subpoints = False
                    else:
                        # translate subpoints for fibers
                        n_items = sp_items.shape[0]
                        for item_index in range(n_items):
                            sp_items[item_index][:VALUES_PER_3D_POINT] += translation
                        n_sp = int(data.agent_data.n_subpoints[time_index][agent_index])
                        data.agent_data.subpoints[time_index][agent_index][
                            :n_sp
                        ] = sp_items.reshape(n_sp)
                if not translate_subpoints:
                    # translate agent position for non-fibers
                    data.agent_data.positions[time_index][agent_index] += translation
        return data
