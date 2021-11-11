#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List

import numpy as np

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class OrientationData:
    type_name_substrings: List[str]
    neighbor1_type_name_substrings: List[str]
    neighbor1_relative_position: np.ndarray
    neighbor2_type_name_substrings: List[str]
    neighbor2_relative_position: np.ndarray

    def __init__(
        self,
        type_name_substrings: List[str],
        neighbor1_type_name_substrings: List[str],
        neighbor1_relative_position: np.ndarray,
        neighbor2_type_name_substrings: List[str],
        neighbor2_relative_position: np.ndarray,
    ):
        """
        This object stores relative neighbor particle positions needed
        to calculate a particle's orientation.

        Note: whether a particle's neighbor is first or second is arbitrary,
        as long as it is kept consistent for a given type

        Parameters
        ----------
        type_name_substrings : List[str]
            The substrings that must be found
            in the type name of the particle being oriented
        neighbor1_type_name_substrings : List[str]
            The substrings that must be found
            in the type name of the first neighbor of the particle being oriented
        neighbor1_relative_position : np.ndarray (shape = [3])
            The global position of the first neighbor
        neighbor2_type_name_substrings : List[str]
            The substrings that must be found
            in the type name of the second neighbor of the particle being oriented
        neighbor2_relative_position : np.ndarray (shape = [3])
            The global position of the second neighbor
        """
        self.type_name_substrings = type_name_substrings
        self.neighbor1_type_name_substrings = neighbor1_type_name_substrings
        self.neighbor1_relative_position = neighbor1_relative_position
        self.neighbor2_type_name_substrings = neighbor2_type_name_substrings
        self.neighbor2_relative_position = neighbor2_relative_position

    @staticmethod
    def type_name_contains_substrings(substrings: List[str], type_name: str) -> bool:
        """
        Does the type_name contain all the substrings?
        """
        for substring in substrings:
            if substring not in type_name:
                return False
        return True

    def type_name_matches(self, type_name: str) -> bool:
        """
        Does the type_name contain all the type_name_substrings?
        """
        return OrientationData.type_name_contains_substrings(
            self.type_name_substrings, type_name
        )

    def neighbor1_type_name_matches(self, type_name: str) -> bool:
        """
        Does the type_name contain all the neighbor1_type_name_substrings?
        """
        return OrientationData.type_name_contains_substrings(
            self.neighbor1_type_name_substrings, type_name
        )

    def neighbor2_type_name_matches(self, type_name: str) -> bool:
        """
        Does the type_name contain all the neighbor2_type_name_substrings?
        """
        return OrientationData.type_name_contains_substrings(
            self.neighbor2_type_name_substrings, type_name
        )
