#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod

import numpy as np

from ..data_objects import TrajectoryData, AgentData
from ..exceptions import DataError
from ..constants import SUBPOINTS_FOR_DISPLAY_TYPE

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class Filter(ABC):
    @abstractmethod
    def apply(self, data: TrajectoryData) -> TrajectoryData:
        pass

    @staticmethod
    def get_items_from_subpoints(
        agent_data: AgentData, time_index: int, agent_index: int
    ) -> np.ndarray:
        """
        Reshape the subpoints array by the items represented
        """
        n_sp = int(agent_data.n_subpoints[time_index][agent_index])
        if n_sp < 1:
            return None
        type_name = agent_data.types[time_index][agent_index]
        if type_name not in agent_data.display_data:
            raise DataError(
                f"{type_name} has no DisplayData, DisplayData."
                "display_type is required to filter subpoints"
            )
        display_type = agent_data.display_data[type_name].display_type
        values_per_item = SUBPOINTS_FOR_DISPLAY_TYPE(display_type)
        n_items = round(n_sp / values_per_item)
        items = agent_data.subpoints[time_index][agent_index][:n_sp]
        items = items.reshape(n_items, values_per_item)
        return items
