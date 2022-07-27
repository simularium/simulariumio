#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from typing import List, Any

from simulariumio import (
    TrajectoryConverter,
    BinaryWriter,
)
from simulariumio.writers.binary_values import BinaryValues
from simulariumio.constants import (
    BINARY_SETTINGS,
    BINARY_BLOCK_TYPE,
    CURRENT_VERSION,
    DEFAULT_CAMERA_SETTINGS,
)
from simulariumio.tests.conftest import binary_test_data


def assert_binary_format_equal(
    chunk_index: int, test_binary_data: List[List[BinaryValues]], expected_format: str
):
    format_string = "".join(
        value.format_string for value in test_binary_data[chunk_index]
    )
    assert format_string == expected_format[chunk_index]


def assert_binary_values_equal(
    chunk_index: int,
    test_binary_data: List[List[BinaryValues]],
    expected_data: List[List[Any]],
):
    data_buffer = [
        value
        for binary_values in test_binary_data[chunk_index]
        for value in binary_values.values
    ]
    for index in range(len(data_buffer)):
        if isinstance(data_buffer[index], float):
            assert data_buffer[index] == pytest.approx(
                expected_data[chunk_index][index]
            )
        else:
            assert data_buffer[index] == expected_data[chunk_index][index]


@pytest.mark.parametrize(
    "max_bytes, expected_header_data, expected_header_format, expected_traj_info, "
    "expected_spatial_data, expected_spatial_format",
    [
        (
            2196,
            [
                [
                    bytes(BINARY_SETTINGS.FILE_IDENTIFIER, "utf-8"),
                    64,  # header length
                    BINARY_SETTINGS.VERSION,
                    BINARY_SETTINGS.N_BLOCKS,
                    64,  # block 0 offset
                    BINARY_BLOCK_TYPE.TRAJ_INFO_JSON.value,
                    1052,  # block 0 length
                    1116,  # block 1 offset
                    BINARY_BLOCK_TYPE.SPATIAL_DATA_BINARY.value,
                    1024,  # block 1 length
                    2140,  # block 2 offset
                    BINARY_BLOCK_TYPE.PLOT_DATA_JSON.value,
                    56,  # block 2 length
                ]
            ],
            [
                "<16s12I",
            ],
            [
                {
                    "version": CURRENT_VERSION.TRAJECTORY_INFO,
                    "timeUnits": {
                        "magnitude": 1.0,
                        "name": "s",
                    },
                    "timeStepSize": 1.0,
                    "totalSteps": 3,
                    "spatialUnits": {
                        "magnitude": 1.0,
                        "name": "µm",
                    },
                    "size": {
                        "x": 1000.0,
                        "y": 1000.0,
                        "z": 1000.0,
                    },
                    "cameraDefault": {
                        "position": {
                            "x": DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[0],
                            "y": DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[1],
                            "z": DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[2],
                        },
                        "lookAtPosition": {
                            "x": DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION[0],
                            "y": DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION[1],
                            "z": DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION[2],
                        },
                        "upVector": {
                            "x": DEFAULT_CAMERA_SETTINGS.UP_VECTOR[0],
                            "y": DEFAULT_CAMERA_SETTINGS.UP_VECTOR[1],
                            "z": DEFAULT_CAMERA_SETTINGS.UP_VECTOR[2],
                        },
                        "fovDegrees": DEFAULT_CAMERA_SETTINGS.FOV_DEGREES,
                    },
                    "typeMapping": {
                        "0": {
                            "name": "H",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "1": {
                            "name": "A",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "2": {
                            "name": "C",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "3": {
                            "name": "X",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "4": {
                            "name": "J",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "5": {
                            "name": "L",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "6": {
                            "name": "D",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "7": {
                            "name": "U",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "8": {
                            "name": "E",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "9": {
                            "name": "Q",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "10": {
                            "name": "K",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                    },
                },
            ],
            [
                [
                    CURRENT_VERSION.SPATIAL_DATA,
                    3,  # number of frames
                    40,  # frame 0 offset
                    340,  # frame 0 length
                    380,  # frame 1 offset
                    328,  # frame 1 length
                    708,  # frame 2 offset
                    316,  # frame 2 length
                    0,  # start of frame 0
                    0.0,
                    5,
                    1000.0,
                    0.0,
                    0.0,
                    4.89610492,
                    -29.81564851,
                    40.77254057,
                    0.0,
                    0.0,
                    0.0,
                    8.38656327,
                    0.0,
                    1001.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    -243.14059805,
                    207.75566987,
                    -95.33921063,
                    -20.54663446,
                    475.97201603,
                    14.43506311,
                    -76.45581828,
                    -97.31170699,
                    -144.30184731,
                    1001.0,
                    2.0,
                    2.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    12.0,
                    108.28447939,
                    175.55049775,
                    -274.34792273,
                    13.44237701,
                    258.21483663,
                    -65.05452787,
                    224.55922362,
                    -455.56482869,
                    -351.23389958,
                    -286.95502659,
                    330.12683064,
                    183.79420473,
                    1000.0,
                    3.0,
                    3.0,
                    43.43048197,
                    48.00424379,
                    -36.02881338,
                    0.0,
                    0.0,
                    0.0,
                    6.18568039,
                    0.0,
                    1001.0,
                    4.0,
                    4.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    49.76236816,
                    -353.11708296,
                    226.84570983,
                    -234.5462914,
                    105.46507228,
                    17.16552317,
                    1,  # start of frame 1
                    1.0,
                    5,
                    1001.0,
                    0.0,
                    5.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    -442.27202981,
                    202.83568625,
                    -262.13407113,
                    -372.23130078,
                    217.21997368,
                    404.88561338,
                    171.37918011,
                    205.80515525,
                    -65.95336727,
                    1000.0,
                    1.0,
                    6.0,
                    -43.37181102,
                    -13.41127423,
                    -17.31316927,
                    0.0,
                    0.0,
                    0.0,
                    6.69209780,
                    0.0,
                    1001.0,
                    2.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    245.9111405,
                    372.15936027,
                    -261.94702214,
                    3.50037066,
                    441.92904046,
                    321.75701298,
                    146.23928574,
                    -315.3241668,
                    82.00405173,
                    1001.0,
                    3.0,
                    7.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    104.82606074,
                    -413.76671598,
                    366.66127719,
                    136.7228888,
                    -210.69313998,
                    -465.59967482,
                    1000.0,
                    4.0,
                    6.0,
                    9.62132397,
                    13.4774314,
                    -20.30846039,
                    0.0,
                    0.0,
                    0.0,
                    9.88033853,
                    0.0,
                    2,  # start of frame 2
                    2.0,
                    5,
                    1000.0,
                    0.0,
                    8.0,
                    -24.91450698,
                    -44.79360525,
                    13.32273796,
                    0.0,
                    0.0,
                    0.0,
                    8.91022619,
                    0.0,
                    1000.0,
                    1.0,
                    9.0,
                    4.10861266,
                    43.86451151,
                    21.93697483,
                    0.0,
                    0.0,
                    0.0,
                    9.01379396,
                    0.0,
                    1001.0,
                    2.0,
                    10.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    -148.70447678,
                    225.27562348,
                    -273.51318785,
                    -5.32043612,
                    -55.97783429,
                    413.32948686,
                    165.64239994,
                    322.63703294,
                    -2.2348818,
                    1001.0,
                    3.0,
                    10.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    -317.48515644,
                    -237.70246887,
                    238.69661676,
                    94.56942257,
                    346.13786088,
                    -7.93209392,
                    1001.0,
                    4.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    7.77508859,
                    260.16762947,
                    -171.02427873,
                    -20.46326319,
                    179.43194042,
                    485.07810635,
                ]
            ],
            [
                "<8IIfI82fIfI79fIfI76f",
            ],
        ),
        (
            2195,
            [
                [
                    bytes(BINARY_SETTINGS.FILE_IDENTIFIER, "utf-8"),
                    64,  # header length
                    BINARY_SETTINGS.VERSION,
                    BINARY_SETTINGS.N_BLOCKS,
                    64,  # block 0 offset
                    BINARY_BLOCK_TYPE.TRAJ_INFO_JSON.value,
                    1052,  # block 0 length
                    1116,  # block 1 offset
                    BINARY_BLOCK_TYPE.SPATIAL_DATA_BINARY.value,
                    700,  # block 1 length
                    1816,  # block 2 offset
                    BINARY_BLOCK_TYPE.PLOT_DATA_JSON.value,
                    56,  # block 2 length
                ],
                [
                    bytes(BINARY_SETTINGS.FILE_IDENTIFIER, "utf-8"),
                    64,  # header length
                    BINARY_SETTINGS.VERSION,
                    BINARY_SETTINGS.N_BLOCKS,
                    64,  # block 0 offset
                    BINARY_BLOCK_TYPE.TRAJ_INFO_JSON.value,
                    1052,  # block 0 length
                    1116,  # block 1 offset
                    BINARY_BLOCK_TYPE.SPATIAL_DATA_BINARY.value,
                    340,  # block 1 length
                    1456,  # block 2 offset
                    BINARY_BLOCK_TYPE.PLOT_DATA_JSON.value,
                    56,  # block 2 length
                ],
            ],
            [
                "<16s12I",
                "<16s12I",
            ],
            [
                {
                    "version": CURRENT_VERSION.TRAJECTORY_INFO,
                    "timeUnits": {
                        "magnitude": 1.0,
                        "name": "s",
                    },
                    "timeStepSize": 1.0,
                    "totalSteps": 2,
                    "spatialUnits": {
                        "magnitude": 1.0,
                        "name": "µm",
                    },
                    "size": {
                        "x": 1000.0,
                        "y": 1000.0,
                        "z": 1000.0,
                    },
                    "cameraDefault": {
                        "position": {
                            "x": DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[0],
                            "y": DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[1],
                            "z": DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[2],
                        },
                        "lookAtPosition": {
                            "x": DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION[0],
                            "y": DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION[1],
                            "z": DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION[2],
                        },
                        "upVector": {
                            "x": DEFAULT_CAMERA_SETTINGS.UP_VECTOR[0],
                            "y": DEFAULT_CAMERA_SETTINGS.UP_VECTOR[1],
                            "z": DEFAULT_CAMERA_SETTINGS.UP_VECTOR[2],
                        },
                        "fovDegrees": DEFAULT_CAMERA_SETTINGS.FOV_DEGREES,
                    },
                    "typeMapping": {
                        "0": {
                            "name": "H",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "1": {
                            "name": "A",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "2": {
                            "name": "C",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "3": {
                            "name": "X",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "4": {
                            "name": "J",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "5": {
                            "name": "L",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "6": {
                            "name": "D",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "7": {
                            "name": "U",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "8": {
                            "name": "E",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "9": {
                            "name": "Q",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "10": {
                            "name": "K",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                    },
                },
                {
                    "version": CURRENT_VERSION.TRAJECTORY_INFO,
                    "timeUnits": {
                        "magnitude": 1.0,
                        "name": "s",
                    },
                    "timeStepSize": 0.0,
                    "totalSteps": 1,
                    "spatialUnits": {
                        "magnitude": 1.0,
                        "name": "µm",
                    },
                    "size": {
                        "x": 1000.0,
                        "y": 1000.0,
                        "z": 1000.0,
                    },
                    "cameraDefault": {
                        "position": {
                            "x": DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[0],
                            "y": DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[1],
                            "z": DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[2],
                        },
                        "lookAtPosition": {
                            "x": DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION[0],
                            "y": DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION[1],
                            "z": DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION[2],
                        },
                        "upVector": {
                            "x": DEFAULT_CAMERA_SETTINGS.UP_VECTOR[0],
                            "y": DEFAULT_CAMERA_SETTINGS.UP_VECTOR[1],
                            "z": DEFAULT_CAMERA_SETTINGS.UP_VECTOR[2],
                        },
                        "fovDegrees": DEFAULT_CAMERA_SETTINGS.FOV_DEGREES,
                    },
                    "typeMapping": {
                        "0": {
                            "name": "H",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "1": {
                            "name": "A",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "2": {
                            "name": "C",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "3": {
                            "name": "X",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "4": {
                            "name": "J",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "5": {
                            "name": "L",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "6": {
                            "name": "D",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "7": {
                            "name": "U",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "8": {
                            "name": "E",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "9": {
                            "name": "Q",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "10": {
                            "name": "K",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                    },
                },
            ],
            [
                [
                    CURRENT_VERSION.SPATIAL_DATA,
                    2,  # number of frames
                    32,  # frame 0 offset
                    340,  # frame 0 length
                    372,  # frame 1 offset
                    328,  # frame 1 length
                    0,  # start of frame 0
                    0.0,
                    5,
                    1000.0,
                    0.0,
                    0.0,
                    4.89610492,
                    -29.81564851,
                    40.77254057,
                    0.0,
                    0.0,
                    0.0,
                    8.38656327,
                    0.0,
                    1001.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    -243.14059805,
                    207.75566987,
                    -95.33921063,
                    -20.54663446,
                    475.97201603,
                    14.43506311,
                    -76.45581828,
                    -97.31170699,
                    -144.30184731,
                    1001.0,
                    2.0,
                    2.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    12.0,
                    108.28447939,
                    175.55049775,
                    -274.34792273,
                    13.44237701,
                    258.21483663,
                    -65.05452787,
                    224.55922362,
                    -455.56482869,
                    -351.23389958,
                    -286.95502659,
                    330.12683064,
                    183.79420473,
                    1000.0,
                    3.0,
                    3.0,
                    43.43048197,
                    48.00424379,
                    -36.02881338,
                    0.0,
                    0.0,
                    0.0,
                    6.18568039,
                    0.0,
                    1001.0,
                    4.0,
                    4.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    49.76236816,
                    -353.11708296,
                    226.84570983,
                    -234.5462914,
                    105.46507228,
                    17.16552317,
                    1,  # start of frame 1
                    1.0,
                    5,
                    1001.0,
                    0.0,
                    5.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    -442.27202981,
                    202.83568625,
                    -262.13407113,
                    -372.23130078,
                    217.21997368,
                    404.88561338,
                    171.37918011,
                    205.80515525,
                    -65.95336727,
                    1000.0,
                    1.0,
                    6.0,
                    -43.37181102,
                    -13.41127423,
                    -17.31316927,
                    0.0,
                    0.0,
                    0.0,
                    6.69209780,
                    0.0,
                    1001.0,
                    2.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    245.9111405,
                    372.15936027,
                    -261.94702214,
                    3.50037066,
                    441.92904046,
                    321.75701298,
                    146.23928574,
                    -315.3241668,
                    82.00405173,
                    1001.0,
                    3.0,
                    7.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    104.82606074,
                    -413.76671598,
                    366.66127719,
                    136.7228888,
                    -210.69313998,
                    -465.59967482,
                    1000.0,
                    4.0,
                    6.0,
                    9.62132397,
                    13.4774314,
                    -20.30846039,
                    0.0,
                    0.0,
                    0.0,
                    9.88033853,
                    0.0,
                ],
                [
                    CURRENT_VERSION.SPATIAL_DATA,
                    1,  # number of frames
                    24,  # frame 0 offset
                    316,  # frame 0 length
                    0,  # start of frame 2
                    2.0,
                    5,
                    1000.0,
                    0.0,
                    8.0,
                    -24.91450698,
                    -44.79360525,
                    13.32273796,
                    0.0,
                    0.0,
                    0.0,
                    8.91022619,
                    0.0,
                    1000.0,
                    1.0,
                    9.0,
                    4.10861266,
                    43.86451151,
                    21.93697483,
                    0.0,
                    0.0,
                    0.0,
                    9.01379396,
                    0.0,
                    1001.0,
                    2.0,
                    10.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    -148.70447678,
                    225.27562348,
                    -273.51318785,
                    -5.32043612,
                    -55.97783429,
                    413.32948686,
                    165.64239994,
                    322.63703294,
                    -2.2348818,
                    1001.0,
                    3.0,
                    10.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    -317.48515644,
                    -237.70246887,
                    238.69661676,
                    94.56942257,
                    346.13786088,
                    -7.93209392,
                    1001.0,
                    4.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    7.77508859,
                    260.16762947,
                    -171.02427873,
                    -20.46326319,
                    179.43194042,
                    485.07810635,
                ],
            ],
            [
                "<6IIfI82fIfI79f",
                "<4IIfI76f",
            ],
        ),
    ],
)
def test_binary_writer(
    max_bytes,
    expected_header_data,
    expected_header_format,
    expected_traj_info,
    expected_spatial_data,
    expected_spatial_format,
):
    converter = TrajectoryConverter(binary_test_data)
    (
        binary_headers,
        trajectory_infos,
        binary_spatial_data,
    ) = BinaryWriter.format_trajectory_data(converter._data, max_bytes)
    for chunk_index in range(len(binary_headers)):
        # header
        assert_binary_format_equal(chunk_index, binary_headers, expected_header_format)
        assert_binary_values_equal(chunk_index, binary_headers, expected_header_data)
        # trajectory info
        assert trajectory_infos[chunk_index] == expected_traj_info[chunk_index]
        # spatial data
        assert_binary_format_equal(
            chunk_index, binary_spatial_data, expected_spatial_format
        )
        assert_binary_values_equal(
            chunk_index, binary_spatial_data, expected_spatial_data
        )
