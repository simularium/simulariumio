#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pytest

from simulariumio.readdy import ReaddyConverter, ReaddyData
from simulariumio import UnitData, MetaData, DisplayData, JsonWriter
from simulariumio.constants import (
    DEFAULT_CAMERA_SETTINGS,
    DISPLAY_TYPE,
    DEFAULT_BOX_SIZE,
    VIZ_TYPE,
)


data = ReaddyData(
    timestep=0.1,
    path_to_readdy_h5="simulariumio/tests/data/readdy/test.h5",
)
converter = ReaddyConverter(data)
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


# test time units default
@pytest.mark.parametrize(
    "timeUnits, expected_timeUnits",
    [
        (
            results["trajectoryInfo"]["timeUnits"],
            {
                "magnitude": 1.0,
                "name": "s",
            },
        )
    ],
)
def test_timeUnits_default(timeUnits, expected_timeUnits):
    assert timeUnits == expected_timeUnits


# test spatial units default
@pytest.mark.parametrize(
    "spatialUnits, expected_spatialUnits",
    [
        (
            results["trajectoryInfo"]["spatialUnits"],
            {
                "magnitude": 1.0,
                "name": "m",
            },
        )
    ],
)
def test_spatialUnits_default(spatialUnits, expected_spatialUnits):
    assert spatialUnits == expected_spatialUnits


# test type mapping default
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": "A",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "1": {
                    "name": "B",
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


time_unit_name = "ns"
time_unit_value = 1.0
spatial_unit_name = "nm"
data_with_unit_data = ReaddyData(
    timestep=0.1,
    path_to_readdy_h5="simulariumio/tests/data/readdy/test.h5",
    time_units=UnitData(time_unit_name, time_unit_value),
    spatial_units=UnitData(spatial_unit_name),
)
converter_unit_data = ReaddyConverter(data_with_unit_data)
results_unit_data = JsonWriter.format_trajectory_data(converter_unit_data._data)


# test time units provided
@pytest.mark.parametrize(
    "timeUnits, expected_timeUnits",
    [
        (
            results_unit_data["trajectoryInfo"]["timeUnits"],
            {
                "magnitude": time_unit_value,
                "name": time_unit_name,
            },
        )
    ],
)
def test_timeUnits_provided(timeUnits, expected_timeUnits):
    assert timeUnits == expected_timeUnits


# test spatial units provided
@pytest.mark.parametrize(
    "spatialUnits, expected_spatialUnits",
    [
        (
            results_unit_data["trajectoryInfo"]["spatialUnits"],
            {
                "magnitude": 1.0,
                "name": spatial_unit_name,
            },
        )
    ],
)
def test_spatialUnits_provided(spatialUnits, expected_spatialUnits):
    assert spatialUnits == expected_spatialUnits


size_x = 20.0
size_y = 20.0
size_z = 10.0
data_with_meta_data = ReaddyData(
    meta_data=MetaData(
        box_size=np.array([size_x, size_y, size_z]),
    ),
    timestep=0.1,
    path_to_readdy_h5="simulariumio/tests/data/readdy/test.h5",
)
converter_meta_data = ReaddyConverter(data_with_meta_data)
results_meta_data = JsonWriter.format_trajectory_data(converter_meta_data._data)


# test box data provided
@pytest.mark.parametrize(
    "box_size, expected_box_size",
    [
        (
            results_meta_data["trajectoryInfo"]["size"],
            {"x": size_x, "y": size_y, "z": size_z},
        )
    ],
)
def test_box_size_provided(box_size, expected_box_size):
    assert box_size == expected_box_size


radius_0 = 3.0
radius_1 = 2.0
name_0 = "C"
name_1 = "B"
color_0 = "#0080ff"
color_1 = "#dfdacd"
data_with_display_data = ReaddyData(
    timestep=0.1,
    path_to_readdy_h5="simulariumio/tests/data/readdy/test.h5",
    display_data={
        "A": DisplayData(
            name=name_0,
            display_type=DISPLAY_TYPE.SPHERE,
            radius=radius_0,
            color=color_0,
        ),
        "B": DisplayData(
            name=name_1,
            radius=radius_1,
            display_type=DISPLAY_TYPE.OBJ,
            url="c.obj",
            color=color_1,
        ),
        "D": DisplayData(
            name=name_0,
            display_type=DISPLAY_TYPE.SPHERE,
            radius=radius_0,
            color=color_0,
        ),
    },
)
converter_display_data = ReaddyConverter(data_with_display_data)
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
                        "displayType": "SPHERE",
                        "color": color_0,
                    },
                },
                "1": {
                    "name": name_1,
                    "geometry": {
                        "displayType": "OBJ",
                        "url": "c.obj",
                        "color": color_1,
                    },
                },
            },
        )
    ],
)
def test_typeMapping_provided(typeMapping, expected_typeMapping):
    assert expected_typeMapping == typeMapping


data_with_ignore_type = ReaddyData(
    timestep=0.1,
    path_to_readdy_h5="simulariumio/tests/data/readdy/test.h5",
    display_data={
        "A": DisplayData(
            name=name_0,
            display_type=DISPLAY_TYPE.SPHERE,
            radius=radius_0,
            color=color_0,
        ),
        "B": DisplayData(
            name=name_1,
            radius=radius_1,
            display_type=DISPLAY_TYPE.OBJ,
            url="c.obj",
            color=color_1,
        ),
        "D": DisplayData(
            name=name_0,
            display_type=DISPLAY_TYPE.SPHERE,
            radius=radius_0,
            color=color_0,
        ),
    },
    ignore_types=[name_1],
)
converter_ignore_type = ReaddyConverter(data_with_ignore_type)
results_ignore_types = JsonWriter.format_trajectory_data(converter_ignore_type._data)


@pytest.mark.parametrize(
    "bundleData, expected_bundleData",
    [
        (
            results_display_data["spatialData"]["bundleData"][0],
            [
                VIZ_TYPE.DEFAULT,  # first agent
                0.0,  # id
                0.0,  # type
                -4.076107488021348,  # x
                3.9849372168961708,  # y
                7.892235671222785,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                radius_0,  # radius
                0.0,  # subpoints
                VIZ_TYPE.DEFAULT,
                1.0,
                1.0,
                -2.780407911074236,
                4.762366216929244,
                9.202490133610398,
                0.0,
                0.0,
                0.0,
                radius_1,
                0.0,
                VIZ_TYPE.DEFAULT,
                2.0,
                0.0,
                8.19869797660185,
                1.4425866729829266,
                6.215047907498356,
                0.0,
                0.0,
                0.0,
                radius_0,
                0.0,
                VIZ_TYPE.DEFAULT,
                3.0,
                1.0,
                8.66544980756901,
                1.97558947182814,
                8.08535556794141,
                0.0,
                0.0,
                0.0,
                radius_1,
                0.0,
            ],
        )
    ],
)
def test_bundleData(bundleData, expected_bundleData):
    assert expected_bundleData == bundleData["data"]


def test_agent_ids():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)


# test type mapping with ignore types
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results_ignore_types["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": name_0,
                    "geometry": {
                        "displayType": "SPHERE",
                        "color": color_0,
                    },
                },
            },
        )
    ],
)
def test_typeMapping_ignore_types(typeMapping, expected_typeMapping):
    assert expected_typeMapping == typeMapping


@pytest.mark.parametrize(
    "bundleData, expected_bundleData",
    [
        (
            results_ignore_types["spatialData"]["bundleData"][0],
            [
                VIZ_TYPE.DEFAULT,  # first agent
                0.0,  # id
                0.0,  # type
                -4.076107488021348,  # x
                3.9849372168961708,  # y
                7.892235671222785,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                radius_0,  # radius
                0.0,  # subpoints
                VIZ_TYPE.DEFAULT,
                2.0,
                0.0,
                8.19869797660185,
                1.4425866729829266,
                6.215047907498356,
                0.0,
                0.0,
                0.0,
                radius_0,
                0.0,
            ],
        )
    ],
)
def test_bundleData_ignored_types(bundleData, expected_bundleData):
    assert expected_bundleData == bundleData["data"]


def test_agent_ids_ignored_types():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)
