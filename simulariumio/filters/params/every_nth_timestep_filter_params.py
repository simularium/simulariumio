#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from .filter_params import FilterParams

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class EveryNthTimestepFilterParams(FilterParams):
    n: int

    def __init__(
        self,
        n: int,
    ):
        """
        This object contains parameters for reducing the number
        of timesteps in simularium data

        Parameters
        ----------
        n : int
            keep every nth time step, filter out all the others
        """
        self.name = "every_nth_timestep"
        self.n = n
