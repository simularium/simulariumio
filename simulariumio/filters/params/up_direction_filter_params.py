#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from .filter_params import FilterParams

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class UpDirectionFilterParams(FilterParams):
    up_dir: str

    def __init__(
        self,
        up_dir: str,
    ):
        """
        This object contains parameters for setting the up direction
        in each frame of simularium data

        Parameters
        ----------
        up_dir : str
            which dimension of the XYZ position data is up?
            Options: "Z"
            for "Z": [+X, +Y, +Z] -> [+X, -Z, +Y]
        """
        self.name = "up_direction"
        self.up_dir = up_dir.upper()
        if self.up_dir != "Z":
            raise Exception('Up direction must be "Z", got {self.up_dir}')
