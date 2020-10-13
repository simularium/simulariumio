#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict

import numpy as np

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class ScatterPlotData:
    title: str
    xaxis_title: str
    yaxis_title: str
    xtrace: np.ndarray
    ytraces: Dict[str, np.ndarray]
    render_mode: str

    def __init__(
        self,
        title: str,
        xaxis_title: str,
        yaxis_title: str,
        xtrace: np.ndarray,
        ytraces: Dict[str, np.ndarray],
        render_mode: str = "markers",
    ):
        """
        This object contains data for a scatterplot

        Parameters
        ----------
        title: str
            A string display title for the plot
        xaxis_title: str
            A string label (with units) for the x-axis
        yaxis_title: str
            A string label (with units) for the y-axis
        xtrace: np.ndarray (shape = [x values])
            A numpy ndarray of values for x,
            the independent variable
        ytraces: Dict[str, np.ndarray] (shape = [x values])]
            A dictionary with y-trace display names as keys,
            each mapped to a numpy ndarray of values for y,
            the dependent variable
        render_mode: str (optional)
            A string specifying how to draw the datapoints.
            Options:
                "markers" : draw as points
                "lines" : connect points with line
            Default: "markers"
        """
        self.title = title
        self.xaxis_title = xaxis_title
        self.yaxis_title = yaxis_title
        self.xtrace = xtrace
        self.ytraces = ytraces
        self.render_mode = render_mode
