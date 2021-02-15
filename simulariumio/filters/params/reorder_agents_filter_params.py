#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict

from .filter_params import FilterParams

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class ReorderAgentsFilterParams(FilterParams):
    type_id_mapping: Dict[int, int]

    def __init__(self, type_id_mapping : Dict[int, int]):
        """
        This object contains parameters for changing the type IDs
        of the agents, so that the agents are listed, and 
        therefore colored, in a different order in the viewer

        Parameters
        ----------
        type_id_mapping : Dict[int, int]
            change each int key type ID in the data to 
            the given int value
        """
        self.name = "reorder_agents"
        self.type_id_mapping = type_id_mapping
