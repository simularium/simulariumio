#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import numpy as np

from simulariumio.mcell import McellConverter, McellData
from simulariumio import DisplayData, MetaData
from simulariumio.constants import (
    DEFAULT_CAMERA_SETTINGS,
    CURRENT_VERSION,
    DISPLAY_TYPE,
)


@pytest.mark.parametrize(
    "trajectory, expected_data",
    [
        # truncated data from organelle model example
        (
            McellData(
                path_to_data_model_json="simulariumio/tests/data/mcell/"
                "organelle_model_viz_output/Scene.data_model.00.json",
                path_to_binary_files="simulariumio/tests/data/mcell/"
                "organelle_model_viz_output",
                meta_data=MetaData(box_size=np.array([50.0, 50.0, 50.0])),
                display_data={
                    "a": DisplayData(
                        name="Kinesin",
                        radius=0.03,
                        display_type=DISPLAY_TYPE.PDB,
                        url="https://files.rcsb.org/download/3KIN.pdb",
                        color="#0080ff",
                    ),
                    "t2": DisplayData(
                        name="Transporter",
                        color="#ff1493",
                    ),
                },
                surface_mol_rotation_angle=0.0,
            ),
            {
                "trajectoryInfo": {
                    "version": CURRENT_VERSION.TRAJECTORY_INFO,
                    "timeUnits": {
                        "magnitude": 1.0,
                        "name": "µs",
                    },
                    "timeStepSize": 1.0,
                    "totalSteps": 3,
                    "spatialUnits": {
                        "magnitude": 1.0,
                        "name": "µm",
                    },
                    "size": {"x": 50.0, "y": 50.0, "z": 50.0},
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
                            "name": "b",
                            "geometry": {
                                "displayType": "SPHERE",
                            },
                        },
                        "1": {
                            "name": "Transporter",
                            "geometry": {
                                "displayType": "SPHERE",
                                "color": "#ff1493",
                            },
                        },
                        "2": {
                            "name": "Kinesin",
                            "geometry": {
                                "displayType": "PDB",
                                "url": "https://files.rcsb.org/download/3KIN.pdb",
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
                                0.12416012585163116,
                                -0.1974048614501953,
                                -0.10042950510978699,
                                0.0,
                                0.0,
                                0.0,
                                0.005,
                                0.0,
                                1000.0,
                                1.0,
                                1.0,
                                -0.027653440833091736,
                                0.1265464723110199,
                                -0.07352104783058167,
                                -160.8765121025542,
                                0.0,
                                -9.231996800714258,
                                0.005,
                                0.0,
                                1000.0,
                                2.0,
                                2.0,
                                0.3647538423538208,
                                0.1595117300748825,
                                0.3979622721672058,
                                0.0,
                                0.0,
                                0.0,
                                0.00015,
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
                                0.10336990654468536,
                                -0.20304752886295319,
                                -0.08513453602790833,
                                0.0,
                                0.0,
                                0.0,
                                0.005,
                                0.0,
                                1000.0,
                                1.0,
                                1.0,
                                -0.0269027017056942,
                                0.12665313482284546,
                                -0.07417202740907669,
                                -160.8765121025542,
                                0.0,
                                -9.231996800714258,
                                0.005,
                                0.0,
                                1000.0,
                                2.0,
                                2.0,
                                0.38411179184913635,
                                0.17711672186851501,
                                0.4012693464756012,
                                0.0,
                                0.0,
                                0.0,
                                0.00015,
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
                                0.11451153457164764,
                                -0.1880205273628235,
                                -0.08175600320100784,
                                0.0,
                                0.0,
                                0.0,
                                0.005,
                                0.0,
                                1000.0,
                                1.0,
                                1.0,
                                -0.024035021662712097,
                                0.12565766274929047,
                                -0.07266511768102646,
                                -160.8765121025542,
                                0.0,
                                -9.231996800714258,
                                0.005,
                                0.0,
                                1000.0,
                                2.0,
                                2.0,
                                0.39510709047317505,
                                0.17876243591308594,
                                0.3935079276561737,
                                0.0,
                                0.0,
                                0.0,
                                0.00015,
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
def test_mcell_converter(trajectory, expected_data):
    converter = McellConverter(trajectory)
    buffer_data = converter._read_trajectory_data(converter._data)
    expected_data == buffer_data
    assert converter._check_agent_ids_are_unique_per_frame(buffer_data)
