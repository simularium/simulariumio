#!/usr/bin/env python
# -*- coding: utf-8 -*-

from enum import Enum
from typing import List
import os

import numpy as np
import pandas as pd

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
    SP_INDEX: int = 11  # index of first subpoint, only valid if num subpoints > 0
    MIN_VALUES_PER_AGENT: int = 11


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


class DISPLAY_TYPE(Enum):
    """
    These values are required for file I/O,
    changing them requires a version bump
    """

    NONE = None
    SPHERE = "SPHERE"
    PDB = "PDB"
    OBJ = "OBJ"
    FIBER = "FIBER"
    SPHERE_GROUP = "SPHERE_GROUP"
    # CUBE = "CUBE"  # coming soon
    # GIZMO = "GIZMO"  # coming soon


VALUES_PER_3D_POINT: int = 3


def SUBPOINT_VALUES_PER_ITEM(display_type: DISPLAY_TYPE) -> int:
    """
    How many values per item saved in subpoints?
    given the display type of the agent
    """
    if display_type == DISPLAY_TYPE.FIBER:
        # fibers store xyz position
        # for each control point in subpoints
        return VALUES_PER_3D_POINT
    if display_type == DISPLAY_TYPE.SPHERE_GROUP:
        # sphere groups store xyz position and radius
        # for each sphere in subpoints
        return VALUES_PER_3D_POINT + 1
    return 1  # other types don't use subpoints


class CURRENT_VERSION:
    TRAJECTORY_INFO: int = 3
    SPATIAL_DATA: int = 1
    PLOT_DATA: int = 1


DEFAULT_BOX_SIZE = 100.0 * np.ones(3)


class BINARY_BLOCK_TYPE(Enum):
    """
    The types of data saved in a block
    """

    SPATIAL_DATA_JSON = 0
    TRAJ_INFO_JSON = 1
    PLOT_DATA_JSON = 2
    SPATIAL_DATA_BINARY = 3
    # TRAJ_INFO_BINARY = 4  # coming soon
    # PLOT_DATA_BINARY = 5  # coming soon


class BINARY_SETTINGS:
    FILE_IDENTIFIER: str = "SIMULARIUMBINARY"
    VERSION: int = 2
    MAX_BYTES: int = 4000000000  # 4GB is max for one file
    HEADER_CONSTANT_N_VALUES: int = 3  # header length, binary version, number of blocks
    N_BLOCKS: int = 3  # all files have traj info, spatial data, and plot data
    HEADER_N_VALUES_PER_BLOCK: int = 3  # block offsets, types, lengths
    BLOCK_HEADER_N_VALUES: int = 2  # block type, block length
    SPATIAL_BLOCK_HEADER_CONSTANT_N_VALUES: int = (
        2  # spatial data version, number of frames
    )
    SPATIAL_BLOCK_HEADER_N_VALUES_PER_FRAME: int = 2  # frame offsets and lengths
    FRAME_HEADER_N_VALUES: int = 3  # frame number, time stamp, number of agents
    BYTES_PER_VALUE: int = 4
    BLOCK_OFFSET_BYTE_ALIGNMENT: int = 4

    # The number of int values stored in the header of binary files
    HEADER_N_INT_VALUES: int = (
        HEADER_CONSTANT_N_VALUES + N_BLOCKS * HEADER_N_VALUES_PER_BLOCK
    )

    # Currently every binary file is written with these 3 blocks
    DEFAULT_BLOCK_TYPES: List[int] = [
        BINARY_BLOCK_TYPE.TRAJ_INFO_JSON.value,
        BINARY_BLOCK_TYPE.SPATIAL_DATA_BINARY.value,
        BINARY_BLOCK_TYPE.PLOT_DATA_JSON.value,
    ]


JMOL_COLORS_CSV_PATH = "package_data/jmolcolors.csv"


def JMOL_COLORS() -> pd.DataFrame:
    """
    Get a dataframe with Jmol colors for atomic element types
    """
    this_dir, _ = os.path.split(__file__)
    return pd.read_csv(os.path.join(this_dir, JMOL_COLORS_CSV_PATH))


DEFAULT_COLORS = [
    "#fee34d",
    "#f7b232",
    "#bf5736",
    "#94a7fc",
    "#ce8ec9",
    "#58606c",
    "#0ba345",
    "#9267cb",
    "#81dbe6",
    "#bd7800",
    "#bbbb99",
    "#5b79f0",
    "#89a500",
    "#da8692",
    "#418463",
    "#9f516c",
    "#00aabf",
]

MAX_AGENT_ID = 0x80000000  # Agent IDs should fit in a 32 bit signed int
