#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from .params import FilterParams
from ..data_objects import AgentData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class Filter(ABC):
    @abstractmethod
    def filter_spatial_data(
        self, agent_data: AgentData, params: FilterParams
    ) -> AgentData:
        pass
