#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np

from simulariumio import FileConverter, InputFileData, JsonWriter, DisplayData
from simulariumio.filters import TranslateFilter
from simulariumio.constants import (
    DEFAULT_CAMERA_SETTINGS,
    CURRENT_VERSION,
    DISPLAY_TYPE,
)


@pytest.mark.parametrize(
    "input_path, display_data, _filter, expected_data",
    [
        # translate agents
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
            TranslateFilter(
                translation_per_type={"microtubule": np.array([10, 0, 50])}
            ),
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
                                46.93,
                                36.8,
                                66.78,
                                40.55,
                                43.87,
                                69.84,
                                34.17,
                                50.93,
                                72.900000000000002,
                                27.78,
                                57.99999999999999,
                                75.95,
                                21.4,
                                65.07,
                                79.01,
                                1000.0,
                                12.0,
                                1.0,
                                -73.8,
                                -25.2,
                                -43.89,
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
                                54.55,
                                33.97,
                                58.86,
                                46.63,
                                38.269999999999996,
                                54.51,
                                38.96,
                                43.28,
                                50.5,
                                31.83,
                                49.61,
                                47.48,
                                26.0,
                                57.66,
                                46.42,
                                22.85,
                                66.92,
                                48.53,
                                1000.0,
                                12.0,
                                1.0,
                                -72.519999999999996,
                                -21.9,
                                -43.59,
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
                                54.55,
                                33.97,
                                58.86,
                                46.63,
                                38.269999999999996,
                                54.51,
                                38.96,
                                43.28,
                                50.5,
                                31.83,
                                49.61,
                                47.48,
                                26.0,
                                57.66,
                                46.42,
                                1000.0,
                                12.0,
                                1.0,
                                -72.519999999999996,
                                -21.9,
                                -43.59,
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
def test_translate_filter(input_path, display_data, _filter, expected_data):
    converter = FileConverter(
        input_file=InputFileData(file_path=input_path),
        display_data=display_data,
    )
    filtered_data = converter.filter_data([_filter])
    buffer_data = JsonWriter.format_trajectory_data(filtered_data)
    assert expected_data == buffer_data
