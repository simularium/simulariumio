#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import numpy as np

from ..data_objects import TrajectoryData
from .filter import Filter

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MultiplyTimeFilter(Filter):
    multiplier: float
    apply_to_plots: bool

    def __init__(
        self,
        multiplier: float,
        apply_to_plots: bool = True,
    ):
        """
        This filter scales the time-stamp values
        for each simulation frame by a provided multiplier

        Parameters
        ----------
        multiplier : float
            float by which to multiply time values
        apply_to_plots : bool (optional)
            also multiply time values in plot data?
            Default = True
        """
        self.multiplier = multiplier
        self.apply_to_plots = apply_to_plots

    def apply(self, data: TrajectoryData) -> TrajectoryData:
        """
        Multiply time values in the data
        """
        print(f"Filtering: multiplying time by {self.multiplier} -------------")
        # plot data
        if self.apply_to_plots:
            for plot in range(len(data.plots)):
                x_title = data.plots[plot]["layout"]["xaxis"]["title"]
                if "time" not in x_title.lower():
                    continue
                for tr in range(len(data.plots[plot]["data"])):
                    trace = data.plots[plot]["data"][tr]
                    trace["x"] = (self.multiplier * np.array(trace["x"])).tolist()
        # spatial data
        data.agent_data.times = self.multiplier * data.agent_data.times
        return data
