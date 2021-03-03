#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import logging

import numpy as np

from ..data_objects import CustomData
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
        This filter multiplies time values

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

    def apply(self, data: CustomData) -> CustomData:
        """
        Multiply time values in the data
        """
        print(f"Filtering: multiplying time by {self.multiplier} -------------")
        # spatial data
        agent_data = copy.copy(data.agent_data)
        agent_data.times *= self.multiplier
        # plot data
        plot_data = copy.copy(data.plots)
        if self.apply_to_plots:
            for p in range(len(plot_data)):
                x_title = plot_data[p]["layout"]["xaxis"]["title"]
                if "time" not in x_title.lower():
                    continue
                for tr in range(len(plot_data[p]["data"])):
                    trace = plot_data[p]["data"][tr]
                    trace["x"] = (self.multiplier * np.array(trace["x"])).tolist()
        return CustomData(
            box_size=np.copy(data.box_size),
            agent_data=agent_data,
            time_units=copy.copy(data.time_units).multiply(self.multiplier),
            spatial_units=copy.copy(data.spatial_units),
            plots=plot_data,
        )
