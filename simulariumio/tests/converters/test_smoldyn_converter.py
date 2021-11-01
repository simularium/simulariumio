#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np

from simulariumio.smoldyn import (
    SmoldynConverter,
    SmoldynData,
)
from simulariumio import MetaData, UnitData, DisplayData, InputFileData
from simulariumio.constants import (
    DEFAULT_CAMERA_SETTINGS,
    CURRENT_VERSION,
    DISPLAY_TYPE,
)


@pytest.mark.parametrize(
    "trajectory, expected_data",
    [
        # 2D
        (
            SmoldynData(
                meta_data=MetaData(
                    box_size=np.array([2.0, 2.0, 0.1]),
                    scale_factor=100,
                ),
                smoldyn_file=InputFileData(
                    file_path="simulariumio/tests/data/smoldyn/example_2D.txt"
                ),
                display_data={
                    "S(solution)": DisplayData(
                        name="S",
                        radius=0.01,
                        display_type=DISPLAY_TYPE.OBJ,
                        url="s.obj",
                        color="#dfdacd",
                    ),
                    "E(front)": DisplayData(
                        name="E",
                        radius=0.1,
                        color="#0080ff",
                    ),
                    "ES(front)": DisplayData(
                        name="ES",
                    ),
                },
            ),
            {
                "trajectoryInfo": {
                    "version": CURRENT_VERSION.TRAJECTORY_INFO,
                    "timeUnits": {
                        "magnitude": 1.0,
                        "name": "s",
                    },
                    "timeStepSize": 0.01,
                    "totalSteps": 3,
                    "spatialUnits": {
                        "magnitude": 10,
                        "name": "mm",
                    },
                    "size": {"x": 200.0, "y": 200.0, "z": 10.0},
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
                            "name": "S",
                            "geometry": {
                                "displayType": "OBJ",
                                "url": "s.obj",
                                "color": "#dfdacd",
                            },
                        },
                        "1": {
                            "name": "E",
                            "geometry": {
                                "displayType": "SPHERE",
                                "color": "#0080ff",
                            },
                        },
                        "2": {
                            "name": "ES",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                    },
                },
                "spatialData": {
                    "version": CURRENT_VERSION.SPATIAL_DATA,
                    "msgType": 1,
                    "bundleStart": 0,
                    "bundleSize": 3,
                    "bundleData": [
                        {
                            "frameNumber": 0,
                            "time": 0.0,
                            "data": [
                                1000.0,
                                500.0,
                                0.0,
                                -87.48,
                                -45.101200000000006,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                1.0,
                                0.0,
                                1000.0,
                                499.0,
                                0.0,
                                63.683,
                                44.5285,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                1.0,
                                0.0,
                                1000.0,
                                600.0,
                                1.0,
                                84.49889999999999,
                                -53.4784,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                10.0,
                                0.0,
                            ],
                        },
                        {
                            "frameNumber": 1,
                            "time": 0.01,
                            "data": [
                                1000.0,
                                500.0,
                                0.0,
                                -81.3601,
                                -46.5024,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                1.0,
                                0.0,
                                1000.0,
                                499.0,
                                0.0,
                                68.1931,
                                26.2768,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                1.0,
                                0.0,
                                1000.0,
                                600.0,
                                1.0,
                                84.49889999999999,
                                -53.4784,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                10.0,
                                0.0,
                                1000.0,
                                606.0,
                                2.0,
                                66.6775,
                                74.52590000000001,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                100.0,
                                0.0,
                            ],
                        },
                        {
                            "frameNumber": 2,
                            "time": 0.02,
                            "data": [
                                1000.0,
                                500.0,
                                0.0,
                                -82.8472,
                                -51.7215,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                1.0,
                                0.0,
                                1000.0,
                                600.0,
                                1.0,
                                84.49889999999999,
                                -53.4784,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                10.0,
                                0.0,
                                1000.0,
                                602.0,
                                2.0,
                                26.263199999999998,
                                -96.4896,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                100.0,
                                0.0,
                            ],
                        },
                    ],
                },
                "plotData": {"version": CURRENT_VERSION.PLOT_DATA, "data": []},
            },
        ),
        # 3D
        (
            SmoldynData(
                meta_data=MetaData(
                    box_size=np.array([100.0, 100.0, 100.0]),
                ),
                smoldyn_file=InputFileData(
                    file_contents=(
                        "0 0\n"
                        "green(solution) 23.4545 49.2404 12.29 130\n"
                        "green(solution) 83.9871 56.5501 33.9238 129\n"
                        "red(solution) 20 30 20 100\n"
                        "red(solution) 20 30 20 99\n"
                        "0.01 0\n"
                        "green(solution) 23.4969 49.2821 12.5752 130\n"
                        "red(solution) 20.0684 30.3008 20.2782 100\n"
                        "red(solution) 20.2498 29.916 19.949 99\n"
                        "0.02 0\n"
                        "green(solution) 23.5342 49.3372 12.6891 130\n"
                        "red(solution) 20.5348 30.1101 19.7543 100\n"
                        "\n"
                    ),
                ),
                display_data={
                    "green(solution)": DisplayData(
                        name="Green",
                        radius=2.0,
                        color="#dfdacd",
                    ),
                },
                spatial_units=UnitData("m"),
            ),
            {
                "trajectoryInfo": {
                    "version": CURRENT_VERSION.TRAJECTORY_INFO,
                    "timeUnits": {
                        "magnitude": 1.0,
                        "name": "s",
                    },
                    "timeStepSize": 0.01,
                    "totalSteps": 3,
                    "spatialUnits": {
                        "magnitude": 1,
                        "name": "m",
                    },
                    "size": {"x": 100.0, "y": 100.0, "z": 100.0},
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
                            "name": "Green",
                            "geometry": {
                                "displayType": "SPHERE",
                                "color": "#dfdacd",
                            },
                        },
                        "1": {
                            "name": "red(solution)",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                    },
                },
                "spatialData": {
                    "version": CURRENT_VERSION.SPATIAL_DATA,
                    "msgType": 1,
                    "bundleStart": 0,
                    "bundleSize": 3,
                    "bundleData": [
                        {
                            "frameNumber": 0,
                            "time": 0.0,
                            "data": [
                                1000.0,
                                130.0,
                                0.0,
                                23.4545,
                                49.2404,
                                12.29,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
                                0.0,
                                1000.0,
                                129.0,
                                0.0,
                                83.9871,
                                56.5501,
                                33.9238,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
                                0.0,
                                1000.0,
                                100.0,
                                1.0,
                                20,
                                30,
                                20,
                                0.0,
                                0.0,
                                0.0,
                                1.0,
                                0.0,
                                1000.0,
                                99.0,
                                1.0,
                                20,
                                30,
                                20,
                                0.0,
                                0.0,
                                0.0,
                                1.0,
                                0.0,
                            ],
                        },
                        {
                            "frameNumber": 1,
                            "time": 0.01,
                            "data": [
                                1000.0,
                                130.0,
                                0.0,
                                23.4969,
                                49.2821,
                                12.5752,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
                                0.0,
                                1000.0,
                                100.0,
                                1.0,
                                20.0684,
                                30.3008,
                                20.2782,
                                0.0,
                                0.0,
                                0.0,
                                1.0,
                                0.0,
                                1000.0,
                                99.0,
                                1.0,
                                20.2498,
                                29.916,
                                19.949,
                                0.0,
                                0.0,
                                0.0,
                                1.0,
                                0.0,
                            ],
                        },
                        {
                            "frameNumber": 2,
                            "time": 0.02,
                            "data": [
                                1000.0,
                                130.0,
                                0.0,
                                23.5342,
                                49.3372,
                                12.6891,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
                                0.0,
                                1000.0,
                                100.0,
                                1.0,
                                20.5348,
                                30.1101,
                                19.7543,
                                0.0,
                                0.0,
                                0.0,
                                1.0,
                                0.0,
                            ],
                        },
                    ],
                },
                "plotData": {"version": CURRENT_VERSION.PLOT_DATA, "data": []},
            },
        ),
    ],
)
def test_smoldyn_converter(trajectory, expected_data):
    converter = SmoldynConverter(trajectory)
    buffer_data = converter._read_trajectory_data(converter._data)
    assert expected_data == buffer_data
    assert converter._check_agent_ids_are_unique_per_frame(buffer_data)
