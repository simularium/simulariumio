#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from abc import ABC, abstractmethod

from ..data_objects import TrajectoryData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class Filter(ABC):
    @abstractmethod
    def apply(self, data: TrajectoryData) -> TrajectoryData:
        pass
