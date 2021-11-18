#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Any

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class BinaryValues:
    values: List[Any]
    format_string: str

    def __init__(
        self,
        values: List[Any],
        format_string: str,
    ):
        """
        This object contains value(s) to be written in binary
        and the format string to use when packing

        Parameters
        ----------
        values: List[Any]
            A list of value(s) that will be written to binary
        format_string: str
            A format string for packing into binary
        """
        self.values = values
        self.format_string = format_string
