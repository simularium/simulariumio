#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from simulariumio import FileConverter, InputFileData, JsonWriter, DisplayData
from simulariumio.filters import MultiplySpaceFilter
from simulariumio.constants import (
    DEFAULT_CAMERA_SETTINGS,
    CURRENT_VERSION,
    DISPLAY_TYPE,
)


@pytest.mark.parametrize(
    "input_path, display_data, _filter, expected_data",
    [
        (
            "simulariumio/tests/data/cytosim/aster_pull3D_couples_actin_solid_3_frames"
            "/aster_pull3D_couples_actin_solid_3_frames_small.json",
            {
                1: DisplayData(
                    name="microtubule",
                    display_type=DISPLAY_TYPE.FIBER,
                ),
                2: DisplayData(
                    name="actin",
                    display_type=DISPLAY_TYPE.FIBER,
                ),
                3: DisplayData(
                    name="aster",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                4: DisplayData(
                    name="vesicle",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                5: DisplayData(
                    name="kinesin",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                6: DisplayData(
                    name="dynein",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                7: DisplayData(
                    name="motor complex",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
            },
            MultiplySpaceFilter(multiplier=10.0),
            {
                "trajectoryInfo": {
                    "version": CURRENT_VERSION.TRAJECTORY_INFO,
                    "timeUnits": {
                        "magnitude": 1.0,
                        "name": "s",
                    },
                    "timeStepSize": 0.05,
                    "totalSteps": 3,
                    "spatialUnits": {
                        "magnitude": 100.0,
                        "name": "nm",
                    },
                    "size": {"x": 2000.0, "y": 2000.0, "z": 2000.0},
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
                            "name": "microtubule",
                            "geometry": {
                                "displayType": "FIBER",
                            },
                        },
                        "1": {
                            "name": "motor complex",
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
                                1001.0,
                                1.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                10.0,
                                15.0,
                                369.3,
                                368.0,
                                167.8,
                                305.5,
                                438.7,
                                198.4,
                                241.69999999999998,
                                509.3,
                                229.00000000000002,
                                177.8,
                                579.9999999999999,
                                259.5,
                                114.0,
                                650.6999999999999,
                                290.1,
                                1000.0,
                                12.0,
                                1.0,
                                -738,
                                -252,
                                -438.9,
                                0.0,
                                0.0,
                                0.0,
                                20.0,
                                0.0,
                            ],
                        },
                        {
                            "frameNumber": 1,
                            "time": 0.05,
                            "data": [
                                1001.0,
                                1.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                10.0,
                                18.0,
                                445.5,
                                339.7,
                                88.6,
                                366.3,
                                382.69999999999996,
                                45.099999999999994,
                                289.6,
                                432.8,
                                5.0,
                                218.29999999999998,
                                496.1,
                                -25.2,
                                160.0,
                                576.5999999999999,
                                -35.8,
                                128.5,
                                669.2,
                                -14.7,
                                1000.0,
                                12.0,
                                1.0,
                                -725.1999999999999,
                                -219.0,
                                -435.90000000000003,
                                0.0,
                                0.0,
                                0.0,
                                20.0,
                                0.0,
                            ],
                        },
                        {
                            "frameNumber": 2,
                            "time": 0.1,
                            "data": [
                                1001.0,
                                1.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                10.0,
                                15.0,
                                445.5,
                                339.7,
                                88.6,
                                366.3,
                                382.69999999999996,
                                45.099999999999994,
                                289.6,
                                432.8,
                                5.0,
                                218.29999999999998,
                                496.1,
                                -25.2,
                                160.0,
                                576.5999999999999,
                                -35.8,
                                1000.0,
                                12.0,
                                1.0,
                                -725.1999999999999,
                                -219.0,
                                -435.90000000000003,
                                0.0,
                                0.0,
                                0.0,
                                20.0,
                                0.0,
                            ],
                        },
                    ],
                },
                "plotData": {
                    "version": CURRENT_VERSION.PLOT_DATA,
                    "data": [],
                },
            },
        ),
    ],
)
def test_multiply_space_filter(input_path, display_data, _filter, expected_data):
    converter = FileConverter(
        input_file=InputFileData(file_path=input_path),
        display_data=display_data,
    )
    filtered_data = converter.filter_data([_filter])
    buffer_data = JsonWriter.format_trajectory_data(filtered_data)
    assert expected_data == buffer_data
