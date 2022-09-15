#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod

import numpy as np

from ..data_objects import TrajectoryData, AgentData
from ..constants import SUBPOINT_VALUES_PER_ITEM

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
        display_type = agent_data.display_type_for_agent(time_index, agent_index)
        values_per_item = SUBPOINT_VALUES_PER_ITEM(display_type)
        n_items = round(n_sp / values_per_item)
        items = agent_data.subpoints[time_index][agent_index][:n_sp]
        items = items.reshape(n_items, values_per_item)
        return items
