#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import numpy as np

from .filter_params import FilterParams

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class TranslateFilterParams(FilterParams):
    translation: np.ndarray

    def __init__(
        self,
        translation: np.ndarray,
    ):
        """
        This object contains parameters for translating 3D positions
        in each frame of simularium data

        Parameters
        ----------
        translation: np.ndarray (shape = [3])
            An XYZ offset to add to each spatial position
        """
        self.name = "translate"
        self.translation = translation
