#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from simulariumio import FileConverter, InputFileData, JsonWriter, DisplayData
from simulariumio.filters import TransformSpatialAxesFilter
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
            TransformSpatialAxesFilter(axes_mapping=["+X", "-Z", "+Y"]),
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
                        "magnitude": 1.0,
                        "name": "µm",
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
                                1.0,
                                15.0,
                                36.93,
                                -16.78,
                                36.8,
                                30.55,
                                -19.84,
                                43.87,
                                24.169999999999998,
                                -22.900000000000002,
                                50.93,
                                17.78,
                                -25.95,
                                57.99999999999999,
                                11.4,
                                -29.01,
                                65.07,
                                1000.0,
                                12.0,
                                1.0,
                                -73.8,
                                43.89,
                                -25.2,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
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
                                1.0,
                                18.0,
                                44.55,
                                -8.86,
                                33.97,
                                36.63,
                                -4.51,
                                38.269999999999996,
                                28.96,
                                -0.5,
                                43.28,
                                21.83,
                                2.52,
                                49.61,
                                16.0,
                                3.58,
                                57.66,
                                12.85,
                                1.47,
                                66.92,
                                1000.0,
                                12.0,
                                1.0,
                                -72.52,
                                43.59,
                                -21.9,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
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
                                1.0,
                                15.0,
                                44.55,
                                -8.86,
                                33.97,
                                36.63,
                                -4.51,
                                38.269999999999996,
                                28.96,
                                -0.5,
                                43.28,
                                21.83,
                                2.52,
                                49.61,
                                16.0,
                                3.58,
                                57.66,
                                1000.0,
                                12.0,
                                1.0,
                                -72.52,
                                43.59,
                                -21.9,
                                0.0,
                                0.0,
                                0.0,
                                2.0,
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
def test_transform_spatial_axes_filter(
    input_path, display_data, _filter, expected_data
):
    converter = FileConverter(
        input_file=InputFileData(file_path=input_path),
        display_data=display_data,
    )
    filtered_data = converter.filter_data([_filter])
    buffer_data = JsonWriter.format_trajectory_data(filtered_data)
    assert expected_data == buffer_data
    assert JsonWriter._check_agent_ids_are_unique_per_frame(buffer_data)
