#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from ..data_objects import ScatterPlotData, HistogramPlotData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class PlotReader(ABC):
    @abstractmethod
    def read(self, data: ScatterPlotData or HistogramPlotData) -> Dict[str, Any]:
        pass
