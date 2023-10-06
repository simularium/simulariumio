#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pytest
from unittest.mock import Mock
from unittest import mock

from simulariumio.springsalad import SpringsaladConverter, SpringsaladData
from simulariumio import DisplayData, MetaData, InputFileData, JsonWriter
from simulariumio.constants import (
    DEFAULT_CAMERA_SETTINGS,
    DISPLAY_TYPE,
    DEFAULT_BOX_SIZE,
    VIEWER_DIMENSION_RANGE,
    VIZ_TYPE,
)
from simulariumio.exceptions import InputDataError


data = SpringsaladData(
    sim_view_txt_file=InputFileData(
        file_path=("simulariumio/tests/data/springsalad/test.txt"),
    ),
    draw_bonds=False,
)
converter = SpringsaladConverter(data)
results = JsonWriter.format_trajectory_data(converter._data)

# value of automatically generated scale factor, so that position
# data fits within VIEWER_DIMENSION_RANGE
range = 70.985562
auto_scale_factor = VIEWER_DIMENSION_RANGE.MAX / range


# test box data default
@pytest.mark.parametrize(
    "box_size, expected_box_size",
    [
        (
            results["trajectoryInfo"]["size"],
            {
                "x": DEFAULT_BOX_SIZE[0] * auto_scale_factor,
                "y": DEFAULT_BOX_SIZE[1] * auto_scale_factor,
                "z": DEFAULT_BOX_SIZE[2] * auto_scale_factor,
            },
        )
    ],
)
def test_box_size_default(box_size, expected_box_size):
    assert box_size == expected_box_size


# test default camera settings
@pytest.mark.parametrize(
    "camera_settings, expected_camera_settings",
    [
        (
            results["trajectoryInfo"]["cameraDefault"],
            {
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
        )
    ],
)
def test_camera_setting_default(camera_settings, expected_camera_settings):
    assert camera_settings == expected_camera_settings


# test type mapping default
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": "GREEN",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "1": {
                    "name": "RED",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "2": {
                    "name": "GRAY",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
            },
        )
    ],
)
def test_typeMapping_default(typeMapping, expected_typeMapping):
    assert expected_typeMapping == typeMapping


scale_factor = 0.1
size_x = 100.0
size_y = 100.0
size_z = 10.0
data_with_metadata = SpringsaladData(
    sim_view_txt_file=InputFileData(
        file_path=("simulariumio/tests/data/springsalad/" "test.txt"),
    ),
    meta_data=MetaData(
        box_size=np.array([size_x, size_y, size_z]),
        scale_factor=scale_factor,
    ),
)
converter_metadata = SpringsaladConverter(data_with_metadata)
results_metadata = JsonWriter.format_trajectory_data(converter_metadata._data)


# test box data provided
@pytest.mark.parametrize(
    "box_size, expected_box_size",
    [
        (
            results_metadata["trajectoryInfo"]["size"],
            {
                "x": size_x * scale_factor,
                "y": size_y * scale_factor,
                "z": size_z * scale_factor,
            },
        )
    ],
)
def test_box_size_provided(box_size, expected_box_size):
    assert box_size == expected_box_size


radius_0 = 10.0
name_0 = "A"
name_1 = "B"
color_0 = "#dfdacd"
color_1 = "#0080ff"
url_0 = "a.obj"
data_with_display_data = SpringsaladData(
    sim_view_txt_file=InputFileData(
        file_path=("simulariumio/tests/data/springsalad/" "test.txt"),
    ),
    meta_data=MetaData(
        box_size=np.array([size_x, size_y, size_z]),
        scale_factor=scale_factor,
    ),
    display_data={
        "GREEN": DisplayData(
            name=name_0,
            radius=radius_0,
            display_type=DISPLAY_TYPE.OBJ,
            url=url_0,
            color=color_0,
        ),
        "RED": DisplayData(
            name=name_1,
            display_type=DISPLAY_TYPE.SPHERE,
            color=color_1,
        ),
    },
    draw_bonds=False,
)
converter_display_data = SpringsaladConverter(data_with_display_data)
results_display_data = JsonWriter.format_trajectory_data(converter_display_data._data)


# test type mapping provided
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results_display_data["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": name_0,
                    "geometry": {
                        "displayType": "OBJ",
                        "url": url_0,
                        "color": color_0,
                    },
                },
                "1": {
                    "name": name_1,
                    "geometry": {
                        "displayType": "SPHERE",
                        "color": color_1,
                    },
                },
                "2": {
                    "name": "GRAY",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
            },
        )
    ],
)
def test_typeMapping_provided(typeMapping, expected_typeMapping):
    assert expected_typeMapping == typeMapping


@pytest.mark.parametrize(
    "bundleData, expected_bundleData",
    [
        (
            results_display_data["spatialData"]["bundleData"][0],
            [
                VIZ_TYPE.DEFAULT,  # first agent
                100000000.0,  # id
                0.0,  # type index
                -23.515194 * scale_factor,  # x
                41.677663 * scale_factor,  # y
                -2.872943 * scale_factor,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                radius_0 * scale_factor,  # radius
                0.0,  # subpoints
                VIZ_TYPE.DEFAULT,  # second agent
                100010000.0,
                0.0,
                -11.726563 * scale_factor,
                37.363461000000004 * scale_factor,
                -4.7181300000000004 * scale_factor,
                0.0,
                0.0,
                0.0,
                10.0 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,  # third agent
                100200001.0,
                1.0,
                -3.749313 * scale_factor,
                6.674895 * scale_factor,
                -5.000000 * scale_factor,
                0.0,
                0.0,
                0.0,
                2.0 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,  # fourth agent
                100200000.0,
                2.0,
                -3.749313 * scale_factor,
                6.674895 * scale_factor,
                0.000000 * scale_factor,
                0.0,
                0.0,
                0.0,
                2.0 * scale_factor,
                0.0,
            ],
        )
    ],
)
def test_bundleData(bundleData, expected_bundleData):
    assert np.isclose(expected_bundleData, bundleData["data"]).all()


def test_agent_ids():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)


data_draw_bonds = SpringsaladData(
    sim_view_txt_file=InputFileData(
        file_path=("simulariumio/tests/data/springsalad/" "test.txt"),
    ),
    meta_data=MetaData(
        box_size=np.array([size_x, size_y, size_z]),
    ),
    display_data={
        "GREEN": DisplayData(
            name=name_0,
            radius=radius_0,
            display_type=DISPLAY_TYPE.OBJ,
            url=url_0,
            color=color_0,
        ),
        "RED": DisplayData(
            name=name_1,
            display_type=DISPLAY_TYPE.SPHERE,
            color=color_1,
        ),
    },
)
converter_draw_bonds = SpringsaladConverter(data_draw_bonds)
results_draw_bonds = JsonWriter.format_trajectory_data(converter_draw_bonds._data)
auto_scale_factor_bonds = VIEWER_DIMENSION_RANGE.MAX / 78.985562


# test type mapping drawing bonds
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results_draw_bonds["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": name_0,
                    "geometry": {
                        "displayType": "OBJ",
                        "url": url_0,
                        "color": color_0,
                    },
                },
                "1": {
                    "name": name_1,
                    "geometry": {
                        "displayType": "SPHERE",
                        "color": color_1,
                    },
                },
                "2": {
                    "name": "GRAY",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "3": {
                    "name": "Link",
                    "geometry": {
                        "displayType": "FIBER",
                    },
                },
            },
        )
    ],
)
def test_typeMapping_bonds(typeMapping, expected_typeMapping):
    assert expected_typeMapping == typeMapping


@pytest.mark.parametrize(
    "bundleData, expected_bundleData",
    [
        (
            results_draw_bonds["spatialData"]["bundleData"][0],
            [
                VIZ_TYPE.DEFAULT,  # first agent
                100000000.0,  # id
                0.0,  # type index
                -23.515194 * auto_scale_factor_bonds,  # x
                41.677663 * auto_scale_factor_bonds,  # y
                -2.872943 * auto_scale_factor_bonds,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                radius_0 * auto_scale_factor_bonds,  # radius
                0.0,  # subpoints
                VIZ_TYPE.DEFAULT,  # second agent
                100010000.0,
                0.0,
                -11.726563 * auto_scale_factor_bonds,
                37.363461000000004 * auto_scale_factor_bonds,
                -4.7181300000000004 * auto_scale_factor_bonds,
                0.0,
                0.0,
                0.0,
                10.0 * auto_scale_factor_bonds,
                0.0,
                VIZ_TYPE.DEFAULT,  # third agent
                100200001.0,
                1.0,
                -3.749313 * auto_scale_factor_bonds,
                6.674895 * auto_scale_factor_bonds,
                -5.000000 * auto_scale_factor_bonds,
                0.0,
                0.0,
                0.0,
                2.0 * auto_scale_factor_bonds,
                0.0,
                VIZ_TYPE.DEFAULT,  # fourth agent
                100200000.0,
                2.0,
                -3.749313 * auto_scale_factor_bonds,
                6.674895 * auto_scale_factor_bonds,
                0.000000 * auto_scale_factor_bonds,
                0.0,
                0.0,
                0.0,
                2.0 * auto_scale_factor_bonds,
                0.0,
                VIZ_TYPE.FIBER,  # fifth agent (fiber)
                0.0,
                3.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0 * auto_scale_factor_bonds,
                6.0,
                -3.749313 * auto_scale_factor_bonds,
                6.674895 * auto_scale_factor_bonds,
                0.000000 * auto_scale_factor_bonds,
                -3.749313 * auto_scale_factor_bonds,
                6.674895 * auto_scale_factor_bonds,
                -5.000000 * auto_scale_factor_bonds,
            ],
        )
    ],
)
def test_bundleData_bonds(bundleData, expected_bundleData):
    assert np.isclose(expected_bundleData, bundleData["data"]).all()


def test_agent_ids_bonds():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)


def test_input_file_error():
    # springsalad_broken_link.txt is makes a link with an agent that doesn't exist
    data = SpringsaladData(
        sim_view_txt_file=InputFileData(
            file_path=(
                "simulariumio/tests/data/malformed_data/springsalad_broken_link.txt"
            )
        ),
        draw_bonds=True,
    )
    with pytest.raises(InputDataError):
        SpringsaladConverter(data)

    # also expect an error for a file of the wrong file type
    wrong_file = SpringsaladData(
        sim_view_txt_file=InputFileData(
            file_path="simulariumio/tests/data/readdy/test.h5"
        ),
        draw_bonds=False,
    )
    with pytest.raises(InputDataError):
        SpringsaladConverter(wrong_file)


def test_callback_fn():
    callback_fn_0 = Mock()
    callback_interval = 0.0000001
    SpringsaladConverter(data, callback_fn_0, callback_interval)
    assert callback_fn_0.call_count > 1

    # calls to the callback function should be strictly increasing
    # and the value should never exceed 1.0 (100%)
    call_list = callback_fn_0.call_args_list
    last_call_val = 0.0
    for call in call_list:
        call_value = call.args[0]
        assert call_value > last_call_val
        assert call_value <= 1.0
        last_call_val = call_value


@mock.patch("simulariumio.constants.VIEWER_DIMENSION_RANGE.MAX", 50)
def test_scaling():
    data = SpringsaladData(
        sim_view_txt_file=InputFileData(
            file_path=("simulariumio/tests/data/springsalad/test.txt"),
        ),
        draw_bonds=False,
    )
    converter = SpringsaladConverter(data)
    results = JsonWriter.format_trajectory_data(converter._data)
    auto_scale_factor = VIEWER_DIMENSION_RANGE.MAX / 70.985562
    assert results["trajectoryInfo"]["size"] == {
        "x": 100.0 * auto_scale_factor,
        "y": 100.0 * auto_scale_factor,
        "z": 100.0 * auto_scale_factor,
    }
    assert results["spatialData"]["bundleData"][0]["data"] == [
        VIZ_TYPE.DEFAULT,  # first agent
        100000000.0,  # id
        0.0,  # type index
        -23.515194 * auto_scale_factor,  # x
        41.677663 * auto_scale_factor,  # y
        -2.872943 * auto_scale_factor,  # z
        0.0,  # x rotation
        0.0,  # y rotation
        0.0,  # z rotation
        2.0 * auto_scale_factor,  # radius
        0.0,  # subpoints
        VIZ_TYPE.DEFAULT,  # second agent
        100010000.0,
        0.0,
        -11.726563 * auto_scale_factor,
        37.363461 * auto_scale_factor,
        -4.71813 * auto_scale_factor,
        0.0,
        0.0,
        0.0,
        2.0 * auto_scale_factor,
        0.0,
        VIZ_TYPE.DEFAULT,  # third agent
        100200001.0,
        1.0,
        -3.749313 * auto_scale_factor,
        6.674895 * auto_scale_factor,
        -5.0 * auto_scale_factor,
        0.0,
        0.0,
        0.0,
        2.0 * auto_scale_factor,
        0.0,
        VIZ_TYPE.DEFAULT,  # fourth agent
        100200000.0,
        2.0,
        -3.749313 * auto_scale_factor,
        6.674895 * auto_scale_factor,
        0.0,
        0.0,
        0.0,
        0.0,
        2.0 * auto_scale_factor,
        0.0,
    ]
