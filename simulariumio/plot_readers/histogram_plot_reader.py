#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any

from .plot_reader import PlotReader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class HistogramPlotReader(PlotReader):
    def read(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """
        print("Reading Histogram Data -------------")
        simularium_data = {}
        # layout info
        simularium_data["layout"] = {
            "title": data.title,
            "xaxis": {"title": data.xaxis_title},
            "yaxis": {"title": "frequency"},
        }
        # plot data
        simularium_data["data"] = []
        for trace_name in data.traces:
            simularium_data["data"].append(
                {
                    "name": trace_name,
                    "type": "histogram",
                    "x": data.traces[trace_name].tolist(),
                }
            )
        return simularium_data
