#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pytest

from simulariumio.springsalad import SpringsaladConverter, SpringsaladData
from simulariumio import DisplayData, MetaData, InputFileData, JsonWriter
from simulariumio.constants import (
    DEFAULT_CAMERA_SETTINGS,
    DISPLAY_TYPE,
    DEFAULT_BOX_SIZE,
    VIZ_TYPE,
)


data = SpringsaladData(
    sim_view_txt_file=InputFileData(
        file_path=("simulariumio/tests/data/springsalad/test.txt"),
    ),
    draw_bonds=False,
)
converter = SpringsaladConverter(data)
results = JsonWriter.format_trajectory_data(converter._data)


# test box data default
@pytest.mark.parametrize(
    "box_size, expected_box_size",
    [
        (
            results["trajectoryInfo"]["size"],
            {
                "x": DEFAULT_BOX_SIZE[0],
                "y": DEFAULT_BOX_SIZE[1],
                "z": DEFAULT_BOX_SIZE[2],
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
        scale_factor=scale_factor,
        box_size=np.array([size_x, size_y, size_z]),
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
        scale_factor=scale_factor,
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
                -2.3515194000000004,  # x
                4.1677663,  # y
                -0.2872943,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                radius_0 * scale_factor,  # radius
                0.0,  # subpoints
                VIZ_TYPE.DEFAULT,  # second agent
                100010000.0,
                0.0,
                -1.1726563,
                3.7363461000000004,
                -0.47181300000000004,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                VIZ_TYPE.DEFAULT,  # third agent
                100200001.0,
                1.0,
                -0.3749313,
                0.6674895000000001,
                -0.5000000,
                0.0,
                0.0,
                0.0,
                0.2,
                0.0,
                VIZ_TYPE.DEFAULT,  # fourth agent
                100200000.0,
                2.0,
                -0.3749313,
                0.6674895000000001,
                0.000000,
                0.0,
                0.0,
                0.0,
                0.2,
                0.0,
            ],
        )
    ],
)
def test_bundleData(bundleData, expected_bundleData):
    assert expected_bundleData == bundleData["data"]


def test_agent_ids():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)


data_draw_bonds = SpringsaladData(
    sim_view_txt_file=InputFileData(
        file_path=("simulariumio/tests/data/springsalad/" "test.txt"),
    ),
    meta_data=MetaData(
        scale_factor=scale_factor,
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
                -2.3515194000000004,  # x
                4.1677663,  # y
                -0.2872943,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                radius_0 * scale_factor,  # radius
                0.0,  # subpoints
                VIZ_TYPE.DEFAULT,  # second agent
                100010000.0,
                0.0,
                -1.1726563,
                3.7363461000000004,
                -0.47181300000000004,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                VIZ_TYPE.DEFAULT,  # third agent
                100200001.0,
                1.0,
                -0.3749313,
                0.6674895000000001,
                -0.5000000,
                0.0,
                0.0,
                0.0,
                0.2,
                0.0,
                VIZ_TYPE.DEFAULT,  # fourth agent
                100200000.0,
                2.0,
                -0.3749313,
                0.6674895000000001,
                0.000000,
                0.0,
                0.0,
                0.0,
                0.2,
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
                1.0,
                6.0,
                -0.3749313,
                0.6674895000000001,
                0.000000,
                -0.3749313,
                0.6674895000000001,
                -0.5000000,
            ],
        )
    ],
)
def test_bundleData_bonds(bundleData, expected_bundleData):
    assert expected_bundleData == bundleData["data"]


def test_agent_ids_bonds():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)
