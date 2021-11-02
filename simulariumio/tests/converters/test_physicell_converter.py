#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pytest

from simulariumio.physicell import PhysicellConverter, PhysicellData
from simulariumio import MetaData, DisplayData
from simulariumio.constants import DEFAULT_CAMERA_SETTINGS, CURRENT_VERSION


@pytest.mark.parametrize(
    "trajectory, expected_data",
    [
        # 3 cells 3 frames
        (
            PhysicellData(
                meta_data=MetaData(
                    box_size=np.array([1000.0, 1000.0, 100.0]),
                    scale_factor=0.01,
                ),
                timestep=360.0,
                path_to_output_dir="simulariumio/tests/data/physicell/output/",
                display_data={
                    0: DisplayData(
                        name="Cancer cell",
                        radius=30.0,
                        color="#0080ff",
                    ),
                },
                phase_names={1: {4: "interphase"}},
            ),
            {
                "trajectoryInfo": {
                    "version": CURRENT_VERSION.TRAJECTORY_INFO,
                    "timeUnits": {
                        "magnitude": 1.0,
                        "name": "s",
                    },
                    "timeStepSize": 360.0,
                    "totalSteps": 3,
                    "spatialUnits": {
                        "magnitude": 100.0,
                        "name": "µm",
                    },
                    "size": {"x": 10.0, "y": 10.0, "z": 1.0},
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
                            "name": "cell1#interphase",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "1": {
                            "name": "Cancer cell#phase4",
                            "geometry": {
                                "displayType": "SPHERE",
                                "color": "#0080ff",
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
                                -4.2700000000000005,
                                -2.5100000000000002,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.08412710547954229,
                                0.0,
                                1000.0,
                                1.0,
                                1.0,
                                -2.2800000000000002,
                                4.3,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.3,
                                0.0,
                                1000.0,
                                2.0,
                                1.0,
                                4.23,
                                3.7800000000000002,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.3,
                                0.0,
                            ],
                        },
                        {
                            "frameNumber": 1,
                            "time": 360.0,
                            "data": [
                                1000.0,
                                0.0,
                                0.0,
                                -4.247925822013689,
                                -2.386576945662163,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.08412710547954229,
                                0.0,
                                1000.0,
                                1.0,
                                1.0,
                                -2.2800000000000002,
                                4.3,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.3,
                                0.0,
                                1000.0,
                                2.0,
                                1.0,
                                4.23,
                                3.7800000000000002,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.3,
                                0.0,
                            ],
                        },
                        {
                            "frameNumber": 2,
                            "time": 720.0,
                            "data": [
                                1000.0,
                                0.0,
                                0.0,
                                -3.993800168730208,
                                -2.5387508185531873,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.08412710547954229,
                                0.0,
                                1000.0,
                                1.0,
                                1.0,
                                -2.2800000000000002,
                                4.3,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.3,
                                0.0,
                                1000.0,
                                2.0,
                                1.0,
                                4.23,
                                3.7800000000000002,
                                0.0,
                                0.0,
                                0.0,
                                0.0,
                                0.3,
                                0.0,
                            ],
                        },
                    ],
                },
                "plotData": {"version": CURRENT_VERSION.PLOT_DATA, "data": []},
            },
        ),
        pytest.param(
            {
                "meta_data": MetaData(
                    box_size=np.array([1000.0, 1000.0, 100.0]),
                    scale_factor=0.01,
                ),
                "timestep": 360.0,
                "path_to_output_dir": "../simulariumio/tests/data/physicell/",
            },
            {},
            marks=pytest.mark.raises(exception=AttributeError),
            # path_to_output_dir is incorrect
        ),
    ],
)
def test_physicell_converter(trajectory, expected_data):
    converter = PhysicellConverter(trajectory)
    buffer_data = converter._read_trajectory_data(converter._data)
    assert expected_data == buffer_data
    assert converter._check_agent_ids_are_unique_per_frame(buffer_data)
