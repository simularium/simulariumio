#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from unittest.mock import Mock
import numpy as np

from simulariumio.cellpack import CellpackConverter, HAND_TYPE, CellpackData
from simulariumio import InputFileData, UnitData, DisplayData, JsonWriter, MetaData
from simulariumio.constants import (
    DEFAULT_CAMERA_SETTINGS,
    DISPLAY_TYPE,
    VIEWER_DIMENSION_RANGE,
    VIZ_TYPE,
)
from simulariumio.exceptions import InputDataError


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
results = JsonWriter.format_trajectory_data(converter._data)

# value of automatically generated scale factor, so that position
# data fits within VIEWER_DIMENSION_RANGE
range = 200.0
auto_scale_factor = VIEWER_DIMENSION_RANGE.MAX / range


@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": "Sphere_radius_100",
                    "geometry": {
                        "color": "#7e7e7e",
                        "displayType": "SPHERE",
                    },
                },
            },
        )
    ],
)
def test_typeMapping(typeMapping, expected_typeMapping):
    assert expected_typeMapping == typeMapping


scale_factor = 100
data_with_display_data = CellpackData(
    results_file=InputFileData(
        file_path="simulariumio/tests/data/cellpack/mock_results.json"
    ),
    geometry_type=DISPLAY_TYPE.SPHERE,
    recipe_file_path="simulariumio/tests/data/cellpack/mock_recipe.json",  # noqa: E501
    time_units=UnitData("ns"),  # nanoseconds
    spatial_units=UnitData("nm"),  # nanometers
    geometry_url="https://aics-simularium-data.s3.us-east-2.amazonaws.com/meshes/obj/",  # noqa: E501
    display_data={
        "Sphere_radius_100": DisplayData(
            name="New_name", display_type=DISPLAY_TYPE.PDB, url="pdbid", color="#ff4741"
        ),
    },
    meta_data=MetaData(
        scale_factor=scale_factor,
    )
)

converter_display_data = CellpackConverter(data_with_display_data)
results_display_data = JsonWriter.format_trajectory_data(converter_display_data._data)


@pytest.mark.parametrize(
    "box_size, expected_box_size",
    [
        (
            results_display_data["trajectoryInfo"]["size"],
            {
                "x": 1000.0 * scale_factor * 0.1,
                "y": 1000.0 * scale_factor * 0.1,
                "z": 1.0 * scale_factor * 0.1,
            },
        )
    ],
)
def test_box_size_scale_factor(box_size, expected_box_size):
    # input data box was 1000, 1000, 1. should be scaled by
    # scale factor and then *0.1 for default cellpack to
    # simularium scaling
    assert box_size == expected_box_size


@pytest.mark.parametrize(
    "typeMapping_dd, expected_typeMapping_dd",
    [
        (
            results_display_data["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "geometry": {
                        "displayType": "PDB",
                        "color": "#ff4741",
                        "url": "pdbid",
                    },
                    "name": "New_name",
                },
            },
        )
    ],
)
def test_typeMapping_with_input_display_data(typeMapping_dd, expected_typeMapping_dd):
    assert typeMapping_dd == expected_typeMapping_dd


@pytest.mark.parametrize(
    "camera_settings, expected_camera_settings",
    [
        (
            results["trajectoryInfo"]["cameraDefault"],
            {
                "position": {
                    "x": 10.0,
                    "y": DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION[1],
                    "z": 100.0,
                },
                "lookAtPosition": {
                    "x": 10.0,
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
        )
    ],
)
def test_camera_setting(camera_settings, expected_camera_settings):
    assert camera_settings == expected_camera_settings


@pytest.mark.parametrize(
    "box_size, expected_box_size",
    [
        (
            results["trajectoryInfo"]["size"],
            {
                "x": 1000.0 * auto_scale_factor,
                "y": 1000.0 * auto_scale_factor,
                "z": 1.0 * auto_scale_factor,
            },
        )
    ],
)
def test_box_size(box_size, expected_box_size):
    # input data box was 1000, 1000, 1
    assert box_size == expected_box_size


@pytest.mark.parametrize(
    "bundleData, expected_bundleData_data",
    [
        (
            results["spatialData"]["bundleData"][0],
            [
                VIZ_TYPE.DEFAULT,
                0.0,  # id
                0.0,  # type
                250.0 * auto_scale_factor,  # x: 750 shifted by the box size and scaled
                250.0 * auto_scale_factor,  # y
                49.5 * auto_scale_factor,  # z: 50 shifted by 0.5 and scaled
                1.5707963267948966,  # xrot
                0.6435011087932847,  # yrot
                -1.5707963267948966,  # test data is left handed, negative Z
                100.0 * auto_scale_factor,  # cr
                0.0,  # number of subpoints
            ],
        )
    ],
)
def test_bundleData(bundleData, expected_bundleData_data):
    assert np.isclose(expected_bundleData_data, bundleData["data"]).all()


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
    pdb_display_data = {"color": "", "display_type": DISPLAY_TYPE.PDB, "url": "1ysx"}
    obj_display_data = {
        "color": "#c73434",
        "display_type": DISPLAY_TYPE.OBJ,
        "url": "url/Bacteria_Rad25_1_4.obj",
    }
    fiber_display_data = {
        "color": "#ff7e50",
        "display_type": DISPLAY_TYPE.FIBER,
        "url": "",
    }

    assert result_pdb == pdb_display_data
    assert result_obj == obj_display_data
    assert result_fiber == fiber_display_data


@pytest.mark.parametrize(
    "quat, matrix",
    [
        (
            [0.1464466, 0.3535534, 0.3535534, 0.8535534],
            [
                [0.5000000, -0.5000000, 0.7071068, 0],
                [0.7071068, 0.7071068, 0.0000000, 0],
                [-0.5000000, 0.5000000, 0.7071068, 0],
                [0, 0, 0, 1],
            ],
        )
    ],
)
def test_get_rotation(quat, matrix):
    # both represent euler angles of [0, 45deg, 45deg]
    from_quat_left = CellpackConverter._get_euler(quat, HAND_TYPE.LEFT)
    from_quat_right = CellpackConverter._get_euler(quat, HAND_TYPE.RIGHT)
    from_matrix_left = CellpackConverter._get_euler(matrix, HAND_TYPE.LEFT)
    from_matrix_right = CellpackConverter._get_euler(matrix, HAND_TYPE.RIGHT)

    assert round(from_quat_right[0], 2) == round(from_matrix_right[0], 2)
    assert round(from_quat_right[1], 2) == round(from_matrix_right[1], 2)
    assert round(from_quat_right[2], 2) == round(from_matrix_right[2], 2)

    assert round(from_quat_left[0], 2) == round(from_matrix_left[0], 2)
    assert round(from_quat_left[1], 2) == round(from_matrix_left[1], 2)
    assert round(from_quat_left[2], 2) == round(from_matrix_left[2], 2)


def test_input_file_error():
    wrong_recipe_file = CellpackData(
        results_file=InputFileData(
            file_path="simulariumio/tests/data/cellpack/mock_results.json"
        ),
        geometry_type=DISPLAY_TYPE.SPHERE,
        recipe_file_path="simulariumio/tests/data/cellpack/mock_results.json",
    )
    with pytest.raises(InputDataError):
        CellpackConverter(wrong_recipe_file)

    bad_file_type = CellpackData(
        results_file=InputFileData(
            file_path="simulariumio/tests/data/springsalad/broken_link.txt"
        ),
        geometry_type=DISPLAY_TYPE.SPHERE,
        recipe_file_path="simulariumio/tests/data/cellpack/mock_recipe.json",
    )
    with pytest.raises(InputDataError):
        CellpackConverter(bad_file_type)


data = CellpackData(
    results_file=InputFileData(
        file_path="simulariumio/tests/data/cellpack/two_ingredients_results.json"
    ),
    geometry_type=DISPLAY_TYPE.OBJ,
    recipe_file_path="simulariumio/tests/data/cellpack/two_ingredients_recipe.json",
    time_units=UnitData("ns"),
    spatial_units=UnitData("nm"),
    handedness=HAND_TYPE.LEFT,
    geometry_url="https://aics-simularium-data.s3.us-east-2.amazonaws.com/meshes/obj/",
)


def test_callback_fn():
    callback_fn = Mock()
    call_interval = 0.000000001
    CellpackConverter(data, callback_fn, call_interval)
    assert callback_fn.call_count > 1

    # calls to the callback function should be strictly increasing
    # and the value should never exceed 1.0 (100%)
    call_list = callback_fn.call_args_list
    last_call_val = 0.0
    for call in call_list:
        call_value = call.args[0]
        assert call_value > last_call_val
        assert call_value <= 1.0
        last_call_val = call_value
