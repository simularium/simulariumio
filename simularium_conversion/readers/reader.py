#!/usr/bin/env python
# -*- coding: utf-8 -*-



###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class Reader(ABC):
    def __init__(self, data: Dict[str, Any] = {}):
        self._data = data

    @abstractmethod
        def _read(self) -> np.ndarray:
            pass