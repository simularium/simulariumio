#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict
import logging

import numpy as np

from .filter import Filter
from ..data_objects import TrajectoryData
from ..constants import VALUES_PER_3D_POINT
from ..utils import translate_agent_positions

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class TranslateFilter(Filter):
    translation_per_type: Dict[str, np.ndarray]
    default_translation: np.ndarray

    def __init__(
        self,
        translation_per_type: Dict[str, np.ndarray] = None,
        default_translation: np.ndarray = np.zeros(VALUES_PER_3D_POINT),
    ):
        """
        This object contains parameters for translating 3D positions
        in each frame of simularium data

        Parameters
        ----------
        translation_per_type : Dict[str, int]
            translation for agents of each type
            Default: {}
        default_translation : int
            translation for any agent types not specified
            in translation_per_type
            Default: np.zeros(3)
        """
        self.translation_per_type = (
            translation_per_type if translation_per_type is not None else {}
        )
        self.default_translation = default_translation

    def apply(self, data: TrajectoryData) -> TrajectoryData:
        """
        Add the XYZ translation to all spatial coordinates
        """
        print("Filtering: translation -------------")
        data.agent_data = translate_agent_positions(
            data.agent_data,
            self.default_translation,
            self.translation_per_type
        )
        return data
