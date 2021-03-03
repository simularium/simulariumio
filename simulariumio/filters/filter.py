#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod

from ..data_objects import CustomData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class Filter(ABC):
    @abstractmethod
    def apply(self, data: CustomData) -> CustomData:
        pass
