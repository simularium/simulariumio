#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any

from .params import FilterParams
from ..data_objects import CustomData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class Filter(ABC):
    @abstractmethod
    def filter(
        self, data: CustomData, params: FilterParams
    ) -> CustomData:
        pass
