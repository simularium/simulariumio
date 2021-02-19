#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict

import numpy as np

from .filter_params import FilterParams

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class TranslateFilterParams(FilterParams):
    translation_per_type_id: Dict[int, np.ndarray]
    default_translation: np.ndarray

    def __init__(
        self,
        translation_per_type_id: Dict[int, np.ndarray],
        default_translation: np.ndarray = np.zeros(3),
    ):
        """
        This object contains parameters for translating 3D positions
        in each frame of simularium data

        Parameters
        ----------
        translation_per_type_id : Dict[int, int]
            translation for agents of each type ID
        default_translation : int
            translation for any agent types not specified
            in translation_per_type_id
            Default: np.zeros(3)
        """
        self.name = "translate"
        self.translation_per_type_id = translation_per_type_id
        self.default_translation = default_translation
