#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class PlotReader(ABC):
    @abstractmethod
    def read(self, data: Dict[str, Any]) -> Dict[str, Any]:
        pass
