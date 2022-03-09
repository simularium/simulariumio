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
    "typeMapping, expected_data",
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
def test_cellpack_converter(typeMapping, expected_data):
    assert expected_data == typeMapping
