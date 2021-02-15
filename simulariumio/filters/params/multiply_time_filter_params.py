#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from .filter_params import FilterParams

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MultiplyTimeFilterParams(FilterParams):
    multiplier: float

    def __init__(
        self,
        multiplier: float,
    ):
        """
        This object contains parameters 
        for multiplying time values

        Parameters
        ----------
        multiplier : float
            float by which to multiply time values
        """
        self.name = "multiply_time"
        self.multiplier = multiplier
