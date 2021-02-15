#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict

from .filter_params import FilterParams

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class EveryNthAgentFilterParams(FilterParams):
    n_per_type_id: Dict[int, int]
    default_n: int

    def __init__(self, n_per_type_id: Dict[int, int], default_n: int = 1):
        """
        This object contains parameters for reducing the number of agents
        in each frame of simularium data

        Parameters
        ----------
        n_per_type_id : Dict[int, int]
            N for agents of each type ID,
            keep every nth agent of that type ID, filter out all the others
        """
        self.name = "every_nth_agent"
        self.n_per_type_id = n_per_type_id
        self.default_n = default_n
