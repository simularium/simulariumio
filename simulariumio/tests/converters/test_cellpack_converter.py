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
                1000.0,  # default type
                0.0,  # id
                0.0,  # number of subpoints
                25.0,  # 750 shifted by the bounding box and scaled down by 0.1
                25.0,
                4.95,  # 50 shifted by 0.5 and scaled down by 0.1
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


@pytest.mark.parametrize(
    "example_PDB, example_OBJ, example_FIBER",
    [
        (
            {
                "meshFile": "autoPACKserver/geometries/i1ysx_23kD_1.dae",
                "coordsystem": "left",
                "sphereFile": "autoPACKserver/collisionTrees/1ysx_23kD.sph",
                "encapsulatingRadius": 14.59,
                "name": "i1ysx_23kD",
                "Type": "MultiSphere",
                "meshName": "i1ysx_23kD",
                "source": {"pdb": "1ysx", "transform": {"center": "true"}},
                "use_mesh_rb": "false",
                "pdb": "1ysx",
            },
            {
                "color": [0.7843, 0.204, 0.204],
                "sphereFile": "autoPACKserver/collisionTrees/Bacteria_Rad25_1_2.sph",
                "encapsulatingRadius": 75,
                "useOrientBias": "true",
                "coordsystem": "left",
                "meshFile": "autoPACKserver/geometries/Bacteria_Rad25_1_4.dae",
                "meshName": "Bacteria_Rad25_1_3",
                "name": "Bacteria_Rad25_1_3",
                "Type": "MultiSphere",
            },
            {
                "color": [1, 0.498, 0.314],
                "coordsystem": "left",
                "radii": [[25]],
                "encapsulatingRadius": 75,
                "positions2": [[[0, 150, 0]]],
                "Type": "Grow",
                "useLength": "false",
                "uLength": 150,
                "source": {"pdb": "1ATZ", "transform": {"center": "true"}},
                "name": "snake",
                "positions": [[[0, 0, 0]]],
                "length": 8000,
                "walkingMode": "sphere",
            },
        )
    ],
)
def test_get_ingredient_display_data(example_PDB, example_OBJ, example_FIBER):
    result_pdb = CellpackConverter._get_ingredient_display_data(
        DISPLAY_TYPE.PDB, example_PDB, "url/"
    )
    result_obj = CellpackConverter._get_ingredient_display_data(
        DISPLAY_TYPE.OBJ, example_OBJ, "url/"
    )
    result_fiber = CellpackConverter._get_ingredient_display_data(
        DISPLAY_TYPE.FIBER, example_FIBER, "url/"
    )
    pdb_display_data = {"display_type": DISPLAY_TYPE.PDB, "url": "1ysx"}
    obj_display_data = {"display_type": DISPLAY_TYPE.OBJ, "url": "url/Bacteria_Rad25_1_4.obj"}
    fiber_display_data = {"display_type": DISPLAY_TYPE.FIBER, "url": "" }

    assert result_pdb == pdb_display_data
    assert result_obj == obj_display_data
    assert result_fiber == fiber_display_data
