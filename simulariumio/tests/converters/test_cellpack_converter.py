#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from simulariumio.cellpack import (
    CellpackConverter,
    HAND_TYPE,
    CellpackData,
)
from simulariumio import InputFileData, UnitData
from simulariumio.constants import (
    DEFAULT_CAMERA_SETTINGS,
    CURRENT_VERSION,
    DISPLAY_TYPE,
)


data = CellpackData(
    results_file=InputFileData(
        file_path="simulariumio/tests/data/cellpack/mock_results.json"
    ),
    geometry_type=DISPLAY_TYPE.SPHERE,
    recipe_file_path="simulariumio/tests/data/cellpack/mock_recipe.json",  # noqa: E501
    time_units=UnitData("ns"),  # nanoseconds
    spatial_units=UnitData("nm"),  # nanometers
    geometry_url="https://aics-simularium-data.s3.us-east-2.amazonaws.com/meshes/obj/",  # noqa: E501
)

converter = CellpackConverter(data)
results = converter._read_trajectory_data(converter._data)


@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": "Sphere_radius_100",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
            },
        )
    ],
)
def test_typeMapping(typeMapping, expected_typeMapping):
    assert expected_typeMapping == typeMapping


@pytest.mark.parametrize(
    "bundleData, expected_bundleData_data",
    [
        (
            results["spatialData"]["bundleData"][0],
            [
                1000.0, # default type
                0.0, # id
                0.0, # number of subpoints
                25.0, # 750 shifted by the bounding box and scaled down by 0.1
                25.0,
                4.95, # 50 shifted by 0.5 and scaled down by 0.1
                1.1496245959205158,
                0.17371416926080796,
                1.4795316553717273,
                10.0,
                0.0,
            ],
        )
    ],
)
def test_bundleData(bundleData, expected_bundleData_data):
    assert expected_bundleData_data == bundleData["data"]
