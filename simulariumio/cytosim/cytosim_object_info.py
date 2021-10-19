#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, List

from ..data_objects import DisplayData, InputFileData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CytosimObjectInfo:
    cytosim_file: InputFileData
    display_data: Dict[int, DisplayData]
    position_indices: List[int]

    def __init__(
        self,
        cytosim_file: InputFileData,
        display_data: Dict[int, DisplayData] = None,
        position_indices: List[int] = [2, 3, 4],
    ):
        """
        This object contains info for reading Cytosim data
        for one type of Cytosim object
        (e.g. fibers, couples, singles, or solids)

        Parameters
        ----------
        cytosim_file : InputFileData
            A InputFileData object containing a string path
            or string contents of Cytosim output text file,
            e.g. fiber_points.txt
        display_data : Dict[int, DisplayData] (optional)
            A dict mapping the type index from Cytosim data
            to DisplayData, including names and display info
            to use for rendering this agent type in the Simularium Viewer
            Default: for names, use "[object type][type ID]". e.g. "filament1",
                for radius, use 1.0,
                for rendering, use default representations and colors
        position_indices : List[int] (optional)
            the columns in Cytosim's reports are not
            always consistent, use this to override them
            if your output file has different column indices
            for position XYZ
            Default: [2, 3, 4]
        """
        self.cytosim_file = cytosim_file
        self.display_data = display_data if display_data is not None else {}
        self.position_indices = position_indices
