#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class OrientationData:
    type_name: str
    neighbor1_type_name: str
    neighbor1_relative_position: np.ndarray
    neighbor2_type_name: str
    neighbor2_relative_position: np.ndarray

    def __init__(
        self,
        type_name: str,
        neighbor1_type_name: str,
        neighbor1_relative_position: np.ndarray,
        neighbor2_type_name: str,
        neighbor2_relative_position: np.ndarray,
    ):
        """
        This object stores relative neighbor particle positions needed 
        to calculate a particle's orientation.
        
        Note: whether a particle's neighbor is first or second is arbitrary, 
        as long as it is kept consistent for a given type

        Parameters
        ----------
        type_name : str
            The type name of the particle being oriented
        neighbor1_type_name : str
            The type name of the first neighbor of the particle being oriented
        neighbor1_relative_position : np.ndarray (shape = [3])
            The global position of the first neighbor
        neighbor2_type_name : str
            The type name of the second neighbor of the particle being oriented
        neighbor2_relative_position : np.ndarray (shape = [3])
            The global position of the second neighbor
        """
        self.type_name = type_name
        self.neighbor1_type_name = neighbor1_type_name
        self.neighbor1_relative_position = neighbor1_relative_position
        self.neighbor2_type_name = neighbor2_type_name
        self.neighbor2_relative_position = neighbor2_relative_position
