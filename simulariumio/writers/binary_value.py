#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Any

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class BinaryValue:
    value: Any
    format_string: str

    def __init__(
        self,
        value: Any,
        format_string: str,
    ):
        """
        This object contains a value to be written in binary
        and the format string to use when packing it

        Parameters
        ----------
        value: Any
            A value that is either a float, int, or string
            which will be written to binary
        format_string: str
            A format string for packing into binary
        """
        self.value = value
        self.format_string = format_string

    def get_value_list(self) -> List[Any]:
        """
        Get this object as a bytes
        """
        if isinstance(self.value, str):
            return [bytes(self.value, "utf-8")]
        if isinstance(self.value, list):
            return self.value
        return [self.value]
