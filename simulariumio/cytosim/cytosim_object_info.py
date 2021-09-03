#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, List

from ..data_objects.agent_type_info import AgentTypeInfo

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CytosimObjectInfo:
    filepath: str
    agents: Dict[int, AgentTypeInfo]
    position_indices: List[int]

    def __init__(
        self,
        filepath: str,
        agents: Dict[int, AgentTypeInfo] = None,
        position_indices: List[int] = [2, 3, 4],
    ):
        """
        This object contains info for reading Cytosim data
        for one type of Cytosim object
        (e.g. fibers, couples, singles, or solids)

        Parameters
        ----------
        filepath : str
            A string path to fiber_points.txt
        agents : Dict[int, AgentTypeInfo] (optional)
            A dict mapping the type index from Cytosim data
            to display names and radii for each type of agent
            of this type of Cytosim object
        position_indices : List[int] (optional)
            the columns in Cytosim's reports are not
            always consistent, use this to override them
            if your output file has different column indices
            for position XYZ
            Default: [2, 3, 4]
        """
        self.filepath = filepath
        self.agents = agents if agents is not None else {}
        self.position_indices = position_indices
