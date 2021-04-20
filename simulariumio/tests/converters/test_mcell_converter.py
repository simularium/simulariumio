#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from simulariumio.mcell import McellConverter, McellData


@pytest.mark.parametrize(
    "trajectory, expected_data",
    [
        # truncated data from organelle model example
        (
            McellData(
                path_to_data_model_json="simulariumio/tests/data/mcell/"
                    "organelle_model_viz_output/Scene.data_model.0.json",
                path_to_binary_files="simulariumio/tests/data/mcell/"
                    "organelle_model_viz_output",
            ),
            {
                "trajectoryInfo": {
                    "version": 2,
                    "timeUnits": {
                        "magnitude": 1.0,
                        "name": "s",
                    },
                    "timeStepSize": 1e-6,
                    "totalSteps": 3,
                    "spatialUnits": {
                        "magnitude": 1.0,
                        "name": "µm",
                    },
                    "size": {"x": 1.28, "y": 1.28, "z": 1.28},
                    "cameraDefault": {
                        "position": {"x": 0, "y": 0, "z": 120},
                        "lookAtPosition": {"x": 0, "y": 0, "z": 0},
                        "upVector": {"x": 0, "y": 1, "z": 0},
                        "fovDegrees": 50.0,
                    },
                    "typeMapping": {
                        "0": {"name": "a"},
                        "1": {"name": "t2"},
                    },
                },
                "spatialData": {
                    "version": 1,
                    "msgType": 1,
                    "bundleStart": 0,
                    "bundleSize": 3,
                    "bundleData": [
                        {
                            "frameNumber": 0,
                            "time": 0.0,
                            "data": [],
                        },
                        {
                            "frameNumber": 1,
                            "time": 1e-6,
                            "data": [],
                        },
                        {
                            "frameNumber": 1,
                            "time": 2e-6,
                            "data": [],
                        },
                    ],
                },
                "plotData": {"version": 1, "data": []},
            },
        ),
    ],
)
def test_mcell_converter(trajectory, expected_data):
    converter = McellConverter(trajectory)
    buffer_data = converter._read_trajectory_data(converter._data)
    assert expected_data["trajectoryInfo"] == buffer_data["trajectoryInfo"]
    # assert converter._check_agent_ids_are_unique_per_frame(buffer_data)
