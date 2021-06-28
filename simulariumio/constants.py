#!/usr/bin/env python
# -*- coding: utf-8 -*-

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


class BUFFER_SIZE_INC:
    """
    How large to make numpy arrays before reading agent data
    from other simulation engine formats.
    Also increment by this amount when increasing the buffer size
    """

    TIMESTEPS: int = 1000
    AGENTS: int = 1000
    SUBPOINTS: int = 10


DEFAULT_AGENT_BUFFER_DIMENSIONS: DimensionData = DimensionData(
    total_steps=BUFFER_SIZE_INC.TIMESTEPS,
    max_agents=BUFFER_SIZE_INC.AGENTS,
)

FIBER_AGENT_BUFFER_DIMENSIONS: DimensionData = DimensionData(
    total_steps=BUFFER_SIZE_INC.TIMESTEPS,
    max_agents=BUFFER_SIZE_INC.AGENTS,
    max_subpoints=BUFFER_SIZE_INC.SUBPOINTS,
)


class DEFAULT_CAMERA_SETTINGS:
    CAMERA_POSITION: np.ndarray = np.array([0.0, 0.0, 120.0])
    LOOK_AT_POSITION: np.ndarray = np.array([0.0, 0.0, 0.0])
    UP_VECTOR: np.ndarray = np.array([0.0, 1.0, 0.0])
    FOV_DEGREES: float = 75.0


DEFAULT_PLOT_MODE = "markers"
