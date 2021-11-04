#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np
from MDAnalysis import Universe

from simulariumio.md import (
    MdConverter,
    MdData,
)
from simulariumio import MetaData, UnitData, DisplayData
from simulariumio.constants import (
    DEFAULT_CAMERA_SETTINGS,
    CURRENT_VERSION,
)


@pytest.mark.parametrize(
    "trajectory, expected_data",
    [
        # visualize every frame
        (
            MdData(
                md_universe=Universe("simulariumio/tests/data/md/example.xyz"),
                meta_data=MetaData(
                    box_size=np.array([200.0, 200.0, 200.0]),
                ),
                display_data={
                    "type_27": DisplayData(
                        name="A",
                        radius=2.0,
                        color="#dfdacd",
                    ),
                    "H": DisplayData(
                        name="Hydrogen",
                    ),
                },
                spatial_units=UnitData("nm"),
            ),
            {
                "trajectoryInfo": {
                    "version": CURRENT_VERSION.TRAJECTORY_INFO,
                    "timeUnits": {
                        "magnitude": 1.0,
                        "name": "s",
                    },
                    "timeStepSize": 1.0,
                    "totalSteps": 3,
                    "spatialUnits": {
                        "magnitude": 1,
                        "name": "nm",
                    },
                    "size": {"x": 200.0, "y": 200.0, "z": 200.0},
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
                            "name": "A",
                            "geometry": {
                                "displayType": "SPHERE",
                                "color": "#dfdacd",
                            },
                        },
                        "1": {
                            "name": "Hydrogen",
                            "geometry": {
                                "displayType": "SPHERE",
                                "color": "#FFFFFF",
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
                                0.0,
                                0.0,
                                42.51536560058594,
                                -22.60795783996582,
                                61.29037857055664,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
                                0.0,
                                1000.0,
                                1.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
                                0.0,
                                1000.0,
                                2.0,
                                1.0,
                                -50.82551574707031,
                                74.92604064941406,
                                15.793620109558105,
                                0.0,
                                0.0,
                                0.0,
                                1.1,
                                0.0,
                            ],
                        },
                        {
                            "frameNumber": 1,
                            "time": 1.0,
                            "data": [
                                1000.0,
                                0.0,
                                0.0,
                                46.06970977783203,
                                -23.434326171875,
                                62.29541015625,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
                                0.0,
                                1000.0,
                                1.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
                                0.0,
                                1000.0,
                                2.0,
                                1.0,
                                -53.94221115112305,
                                77.53073120117188,
                                15.477828979492188,
                                0.0,
                                0.0,
                                0.0,
                                1.1,
                                0.0,
                            ],
                        },
                        {
                            "frameNumber": 2,
                            "time": 2.0,
                            "data": [
                                1000.0,
                                0.0,
                                0.0,
                                46.473079681396484,
                                -19.95725440979004,
                                62.311668395996094,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
                                0.0,
                                1000.0,
                                1.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
                                0.0,
                                1000.0,
                                2.0,
                                1.0,
                                -21.319805145263672,
                                -76.14720153808594,
                                -13.58427906036377,
                                0.0,
                                0.0,
                                0.0,
                                1.1,
                                0.0,
                            ],
                        },
                    ],
                },
                "plotData": {"version": CURRENT_VERSION.PLOT_DATA, "data": []},
            },
        ),
        # visualize every other frame
        (
            MdData(
                md_universe=Universe("simulariumio/tests/data/md/example.xyz"),
                nth_timestep_to_read=2,
                meta_data=MetaData(
                    box_size=np.array([200.0, 200.0, 200.0]),
                ),
                display_data={
                    "type_27": DisplayData(
                        name="A",
                        radius=2.0,
                        color="#dfdacd",
                    ),
                    "H": DisplayData(
                        name="Hydrogen",
                    ),
                },
                spatial_units=UnitData("nm"),
            ),
            {
                "trajectoryInfo": {
                    "version": CURRENT_VERSION.TRAJECTORY_INFO,
                    "timeUnits": {
                        "magnitude": 1.0,
                        "name": "s",
                    },
                    "timeStepSize": 2.0,
                    "totalSteps": 2,
                    "spatialUnits": {
                        "magnitude": 1,
                        "name": "nm",
                    },
                    "size": {"x": 200.0, "y": 200.0, "z": 200.0},
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
                            "name": "A",
                            "geometry": {
                                "displayType": "SPHERE",
                                "color": "#dfdacd",
                            },
                        },
                        "1": {
                            "name": "Hydrogen",
                            "geometry": {
                                "displayType": "SPHERE",
                                "color": "#FFFFFF",
                            },
                        },
                    },
                },
                "spatialData": {
                    "version": CURRENT_VERSION.SPATIAL_DATA,
                    "msgType": 1,
                    "bundleStart": 0,
                    "bundleSize": 2,
                    "bundleData": [
                        {
                            "frameNumber": 0,
                            "time": 0.0,
                            "data": [
                                1000.0,
                                0.0,
                                0.0,
                                42.51536560058594,
                                -22.60795783996582,
                                61.29037857055664,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
                                0.0,
                                1000.0,
                                1.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
                                0.0,
                                1000.0,
                                2.0,
                                1.0,
                                -50.82551574707031,
                                74.92604064941406,
                                15.793620109558105,
                                0.0,
                                0.0,
                                0.0,
                                1.1,
                                0.0,
                            ],
                        },
                        {
                            "frameNumber": 1,
                            "time": 2.0,
                            "data": [
                                1000.0,
                                0.0,
                                0.0,
                                46.473079681396484,
                                -19.95725440979004,
                                62.311668395996094,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
                                0.0,
                                1000.0,
                                1.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
                                0.0,
                                1000.0,
                                2.0,
                                1.0,
                                -21.319805145263672,
                                -76.14720153808594,
                                -13.58427906036377,
                                0.0,
                                0.0,
                                0.0,
                                1.1,
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
def test_md_converter(trajectory, expected_data):
    converter = MdConverter(trajectory)
    buffer_data = converter._read_trajectory_data(converter._data)
    assert expected_data == buffer_data
    assert converter._check_agent_ids_are_unique_per_frame(buffer_data)
