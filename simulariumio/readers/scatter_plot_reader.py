#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any

from ..exceptions import MissingDataError, DataError
from .reader import Reader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class ScatterPlotReader(Reader):
    def read(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """

        if "title" not in data:
            raise MissingDataError("title")
        if "xaxis_title" not in data:
            raise MissingDataError("xaxis_title")
        if "yaxis_title" not in data:
            raise MissingDataError("yaxis_title")
        if "xtrace" not in data:
            raise MissingDataError("xtrace")
        if "ytraces" not in data:
            raise MissingDataError("ytraces")

        simularium_data = {}

        # layout info
        simularium_data["layout"] = {
            "title": data["title"],
            "xaxis": {"title": data["xaxis_title"]},
            "yaxis": {"title": data["yaxis_title"]},
        }

        # plot data
        simularium_data["data"] = []
        for ytrace_name in data["ytraces"]:
            if len(data["ytraces"][ytrace_name]) != len(data["xtrace"]):
                raise DataError(
                    f"y-trace {ytrace_name} has a different length than x-trace"
                )
            simularium_data["data"].append(
                {
                    "name": ytrace_name,
                    "type": "scatter",
                    "x": data["xtrace"],
                    "y": data["ytraces"][ytrace_name],
                    "mode": data["render_mode"] if "render_mode" in data else "markers",
                }
            )

        return simularium_data
