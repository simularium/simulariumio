#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np

from simulariumio.smoldyn import (
    SmoldynConverter,
    SmoldynData,
)
from simulariumio import MetaData, UnitData, DisplayData, InputFileData, JsonWriter
from simulariumio.constants import (
    DEFAULT_BOX_SIZE,
    DEFAULT_CAMERA_SETTINGS,
    DISPLAY_TYPE,
    VIZ_TYPE,
)

data = SmoldynData(
    smoldyn_file=InputFileData(
        file_path="simulariumio/tests/data/smoldyn/example_data.txt"
    )
)
converter = SmoldynConverter(data)
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


# test type mapping default
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": "S(solution)",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "1": {
                    "name": "E(front)",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "2": {
                    "name": "ES(front)",
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


x_size = 2.0
y_size = 2.0
z_size = 0.1
scale_factor = 100
data_with_meta_data = SmoldynData(
    meta_data=MetaData(
        box_size=np.array([x_size, y_size, z_size]),
        scale_factor=scale_factor,
    ),
    smoldyn_file=InputFileData(
        file_path="simulariumio/tests/data/smoldyn/example_data.txt"
    ),
)
converter_meta_data = SmoldynConverter(data_with_meta_data)
results_meta_data = JsonWriter.format_trajectory_data(converter_meta_data._data)


# test box size provided
@pytest.mark.parametrize(
    "box_size, expected_box_size",
    [
        (
            results_meta_data["trajectoryInfo"]["size"],
            {
                "x": x_size * scale_factor,
                "y": y_size * scale_factor,
                "z": z_size * scale_factor,
            },
        )
    ],
)
def test_box_size_provided(box_size, expected_box_size):
    # if a box size is provided, we should use it
    assert box_size == expected_box_size


time_unit_name = "ns"
time_unit_value = 1.0
spatial_unit_name = "nm"
data_with_unit_data = SmoldynData(
    time_units=UnitData(time_unit_name, time_unit_value),
    spatial_units=UnitData(spatial_unit_name),
    smoldyn_file=InputFileData(
        file_path="simulariumio/tests/data/smoldyn/example_data.txt"
    ),
)
converter_unit_data = SmoldynConverter(data_with_unit_data)
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


s_radius = 0.01
s_url = "s.obj"
s_color = "#dfdacd"
e_radius = 0.1
e_color = "#0080ff"
data_with_display_data = SmoldynData(
    meta_data=MetaData(
        box_size=np.array([x_size, y_size, z_size]),
        scale_factor=scale_factor,
    ),
    smoldyn_file=InputFileData(
        file_path="simulariumio/tests/data/smoldyn/example_data.txt"
    ),
    display_data={
        "S(solution)": DisplayData(
            name="S",
            radius=s_radius,
            display_type=DISPLAY_TYPE.OBJ,
            url=s_url,
            color=s_color,
        ),
        "E(front)": DisplayData(
            name="E",
            display_type=DISPLAY_TYPE.SPHERE,
            radius=e_radius,
            color=e_color,
        ),
        "ES(front)": DisplayData(
            name="ES",
            display_type=DISPLAY_TYPE.SPHERE,
        ),
    },
)
converter_display_data = SmoldynConverter(data_with_display_data)
results_display_data = JsonWriter.format_trajectory_data(converter_display_data._data)


# test type mapping with display data provided
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results_display_data["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": "S",
                    "geometry": {
                        "displayType": "OBJ",
                        "url": s_url,
                        "color": s_color,
                    },
                },
                "1": {
                    "name": "E",
                    "geometry": {
                        "displayType": "SPHERE",
                        "color": e_color,
                    },
                },
                "2": {
                    "name": "ES",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
            },
        )
    ],
)
def test_typeMapping_with_display_data(typeMapping, expected_typeMapping):
    assert expected_typeMapping == typeMapping


@pytest.mark.parametrize(
    "bundleData, expected_bundleData",
    [
        (
            # just testing the first frame
            results_display_data["spatialData"]["bundleData"][0],
            [
                VIZ_TYPE.DEFAULT,  # first agent
                500.0,  # id
                0.0,  # type
                -87.48,  # x
                -45.101200000000006,  # y
                0.0,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                s_radius * scale_factor,  # radius
                0.0,  # number of subpoints
                VIZ_TYPE.DEFAULT,  # second agent
                600.0,
                1.0,
                84.49889999999999,
                -53.4784,
                0.0,
                0.0,
                0.0,
                0.0,
                e_radius * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,  # third agent
                606.0,
                2.0,
                66.6775,
                74.52590000000001,
                0.0,
                0.0,
                0.0,
                0.0,
                scale_factor,  # default radius = 1.0
                0.0,
            ],
        )
    ],
)
def test_bundleData(bundleData, expected_bundleData):
    assert expected_bundleData == bundleData["data"]


def test_agent_ids():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)


# test 3D data
size = 100.0
green_name = "Green"
green_radius = 2.0
green_color = "#dfdacd"
data_3D = SmoldynData(
    meta_data=MetaData(
        box_size=np.array([size, size, size]),
    ),
    smoldyn_file=InputFileData(
        file_path="simulariumio/tests/data/smoldyn/example_3D.txt"
    ),
    display_data={
        "green(solution)": DisplayData(
            name=green_name,
            display_type=DISPLAY_TYPE.SPHERE,
            radius=green_radius,
            color=green_color,
        ),
    },
    spatial_units=UnitData("m"),
)
converter_3D_data = SmoldynConverter(data_3D)
results_3D_data = JsonWriter.format_trajectory_data(converter_3D_data._data)


# test type mapping with display data provided
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results_3D_data["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": green_name,
                    "geometry": {
                        "displayType": "SPHERE",
                        "color": green_color,
                    },
                },
                "1": {
                    "name": "red(solution)",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
            },
        )
    ],
)
def test_typeMapping_with_3D_data(typeMapping, expected_typeMapping):
    assert expected_typeMapping == typeMapping


@pytest.mark.parametrize(
    "bundleData, expected_bundleData",
    [
        (
            # just testing the first frame
            results_3D_data["spatialData"]["bundleData"][0],
            [
                VIZ_TYPE.DEFAULT,  # first agent
                130.0,  # id
                0.0,  # type
                23.4545,  # x
                49.2404,  # y
                12.29,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                green_radius,  # radius
                0.0,  # subpoints
                VIZ_TYPE.DEFAULT,  # second agent
                129.0,
                0.0,
                83.9871,
                56.5501,
                33.9238,
                0.0,
                0.0,
                0.0,
                green_radius,
                0.0,
                VIZ_TYPE.DEFAULT,  # third agent
                100.0,
                1.0,
                20,
                30,
                20,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
                VIZ_TYPE.DEFAULT,  # fourth agent
                99.0,
                1.0,
                20,
                30,
                20,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
            ],
        )
    ],
)
def test_bundleData_3D(bundleData, expected_bundleData):
    assert expected_bundleData == bundleData["data"]
