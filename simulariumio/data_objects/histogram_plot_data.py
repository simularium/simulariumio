#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict

import numpy as np

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class HistogramPlotData:
    title: str
    xaxis_title: str
    xtrace: np.ndarray
    traces: Dict[str, np.ndarray]

    def __init__(self, title: str, xaxis_title: str, traces: Dict[str, np.ndarray]):
        """
        This object contains data for a scatterplot

        Parameters
        ----------
        title: str
            A string display title for the plot
        xaxis_title: str
            A string label (with units) for the x-axis
        traces: Dict[str, np.ndarray] (shape = [values])]
            A dictionary with trace display names as keys,
            each mapped to a numpy ndarray of values
        """
        self.title = title
        self.xaxis_title = xaxis_title
        self.traces = traces
