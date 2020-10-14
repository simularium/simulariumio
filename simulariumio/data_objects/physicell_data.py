#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict, List

import numpy as np

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class PhysicellData:
    box_size: np.ndarray
    timestep: float
    path_to_output_dir: str
    types: Dict[int, Dict[Any, str]]
    scale_factor: float
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        box_size: np.ndarray,
        timestep: float,
        path_to_output_dir: str,
        types: Dict[int, Dict[Any, str]] = None,
        scale_factor: float = 1.0,
        plots: List[Dict[str, Any]] = [],
    ):
        """
        This object holds simulation trajectory outputs
        from ReaDDy (https://readdy.github.io/)
        and plot data

        Parameters
        ----------
        box_size : np.ndarray (shape = [3])
            A numpy ndarray containing the XYZ dimensions
            of the simulation bounding volume
        timestep : float
            A float amount of time that passes each step
            Default: 0.0
        path_to_output_dir : string
            A string path to the PhysiCell output directory
            containing MultiCellDS XML and MATLAB files
        types : Dict[int, Dict[Any, str]] (optional)
            the cell type ID from PhysiCell data mapped
            to display name for that type, and display names
            for phases of that type
            "name" or [cell phase ID from PhysiCell data] : str
                "name" or the cell phase ID from PhysiCell data mapped
                to the display names
                Default: "cell[cell type ID from PhysiCell data]#
                    phase[cell phase ID from PhysiCell data]"
        scale_factor : float (optional)
            A multiplier for the ReaDDy scene, use if
            visualization is too large or small
            Default: 1.0
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.box_size = box_size
        self.timestep = timestep
        self.path_to_output_dir = path_to_output_dir
        self.types = types
        self.scale_factor = scale_factor
        self.plots = plots
