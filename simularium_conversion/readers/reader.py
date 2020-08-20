#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .simularium_data import SimulariumData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class Reader(ABC):
    data: SimulariumData = None

    def __init__(self, data: Dict[str, Any] = {}):
        self.data = self._read(data)

    @abstractmethod
    def _read(self, data: Dict[str, Any]) -> SimulariumData:
        pass