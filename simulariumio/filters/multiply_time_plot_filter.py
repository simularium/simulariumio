#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import math
from typing import Any, Dict

import numpy as np

from ..data_objects import AgentData
from .filter import Filter
from .params import MultiplyTimePlotFilterParams, FilterParams

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MultiplyTimePlotFilter(Filter):
    def filter_plot_data(
        self, plot_data: Dict[str, Any], params: MultiplyTimePlotFilterParams
    ) -> Dict[str, Any]:
        """
        Multiply time values in plot data
        """
        print(f"Filtering: multiplying plot time by {params.multiplier} -------------")
        for p in range(len(plot_data["data"])):
            if "time" not in plot_data["data"][p]["layout"]["xaxis"]["title"]:
                continue
            for t in range(len(plot_data["data"][p]["data"])):
                trace = plot_data["data"][p]["data"][t]
                trace["x"] = (params.multiplier * np.array(trace["x"])).tolist()
        return plot_data

    def filter_spatial_data(
        self, agent_data: AgentData, params: FilterParams
    ) -> AgentData:
        return agent_data
