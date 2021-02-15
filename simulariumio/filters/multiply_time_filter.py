#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Any, Dict
import logging
import math

import numpy as np

from ..data_objects import AgentData
from .filter import Filter
from .params import MultiplyTimeFilterParams, FilterParams

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MultiplyTimeFilter(Filter):
    def filter_spatial_data(
        self, agent_data: AgentData, params: MultiplyTimeFilterParams
    ) -> AgentData:
        """
        Multiply time values in the spatial data
        """
        print(f"Filtering: multiplying time by {params.multiplier} -------------")
        agent_data.times *= params.multiplier
        return agent_data

    def filter_plot_data(
        self, plot_data: Dict[str, Any], params: FilterParams
    ) -> Dict[str, Any]:
        return plot_data
