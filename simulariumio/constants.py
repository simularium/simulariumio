#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import List

import numpy as np

from .data_objects.dimension_data import DimensionData


class V1_SPATIAL_BUFFER_STRUCT:
    VIZ_TYPE_INDEX: int = 0
    UID_INDEX: int = 1  # unique ID
    TID_INDEX: int = 2  # type ID
    POSX_INDEX: int = 3
    POSY_INDEX: int = 4
    POSZ_INDEX: int = 5
    ROTX_INDEX: int = 6
    ROTY_INDEX: int = 7
    ROTZ_INDEX: int = 8
    R_INDEX: int = 9  # radius
    NSP_INDEX: int = 10  # num subpoints
    SP_INDEX: int = 11  # subpoints
    VALUES_PER_AGENT: int = 12


class VIZ_TYPE:
    DEFAULT: float = 1000.0
    FIBER: float = 1001.0


"""
Default size to make numpy arrays when data dimensions are unknown
"""
BUFFER_SIZE_INC: DimensionData = DimensionData(
    total_steps=1000,
    max_agents=1000,
    max_subpoints=100,
)


class DEFAULT_CAMERA_SETTINGS:
    CAMERA_POSITION: np.ndarray = np.array([0.0, 0.0, 120.0])
    LOOK_AT_POSITION: np.ndarray = np.array([0.0, 0.0, 0.0])
    UP_VECTOR: np.ndarray = np.array([0.0, 1.0, 0.0])
    FOV_DEGREES: float = 75.0


DEFAULT_PLOT_MODE = "markers"


class BINARY_SETTINGS:
    HEADER: str = "SIMULARIUMBIN"
    VERSION: List[int] = [1, 0, 0]
    EOF: str = "\u005CEOFTHEFRAMEENDSHERE"
    MAX_FRAMES: int = 10000
    MAX_BYTES: int = 500000000
