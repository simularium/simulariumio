#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np
from MDAnalysis import Universe

from simulariumio.md import (
    MdConverter,
    MdData,
)
from simulariumio import MetaData, UnitData, DisplayData, JsonWriter
from simulariumio.constants import (
    DEFAULT_CAMERA_SETTINGS,
    DEFAULT_BOX_SIZE,
    VIZ_TYPE,
    DISPLAY_TYPE
)

data = MdData(md_universe=Universe("simulariumio/tests/data/md/example.xyz"))
converter = MdConverter(data)
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
                    "name": "T#type_27",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "1": {
                    "name": "H#H",
                    "geometry": {
                        "displayType": "SPHERE",
                        "color": "#FFFFFF",
                    },
                },
            },
        )
    ],
)
def test_typeMapping_default(typeMapping, expected_typeMapping):
    assert expected_typeMapping == typeMapping


time_unit_name = "ms"
time_unit_value = 2.0
spatial_unit_name = "nm"
spatial_unit_value = 1.0
data_with_unit_data = MdData(
    md_universe=Universe("simulariumio/tests/data/md/example.xyz"),
    time_units=UnitData(time_unit_name, time_unit_value),
    spatial_units=UnitData(spatial_unit_name, spatial_unit_value),
)
converter_unit_data = MdConverter(data_with_unit_data)
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
                "magnitude": spatial_unit_value,
                "name": spatial_unit_name,
            },
        )
    ],
)
def test_spatialUnits_provided(spatialUnits, expected_spatialUnits):
    assert spatialUnits == expected_spatialUnits


size_x = 200.0
size_y = 200.0
size_z = 100.0
data_with_meta_data = MdData(
    md_universe=Universe("simulariumio/tests/data/md/example.xyz"),
    meta_data=MetaData(box_size=np.array([size_x, size_y, size_z])),
)
converter_meta_data = MdConverter(data_with_meta_data)
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


type_27_name = "A"
type_27_radius = 2.0
type_27_color = "#dfdacd"
h_name = "Hydrogen"
data_with_display_data = MdData(
    md_universe=Universe("simulariumio/tests/data/md/example.xyz"),
    display_data={
        "type_27": DisplayData(
            name=type_27_name,
            display_type=DISPLAY_TYPE.SPHERE,
            radius=type_27_radius,
            color=type_27_color,
        ),
        "H": DisplayData(
            name=h_name,
            display_type=DISPLAY_TYPE.SPHERE,
        ),
    },
)
converter_display_data = MdConverter(data_with_display_data)
results_display_data = JsonWriter.format_trajectory_data(converter_display_data._data)


# test type mapping provided
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results_display_data["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": type_27_name,
                    "geometry": {
                        "displayType": "SPHERE",
                        "color": type_27_color,
                    },
                },
                "1": {
                    "name": h_name,
                    "geometry": {
                        "displayType": "SPHERE",
                        "color": "#FFFFFF",
                    },
                },
            },
        )
    ],
)
def test_typeMapping_provided(typeMapping, expected_typeMapping):
    assert expected_typeMapping == typeMapping


# same display data as above, except only displaying every other timestep
data_nth_timestep = MdData(
    md_universe=Universe("simulariumio/tests/data/md/example.xyz"),
    nth_timestep_to_read=2,
    display_data={
        "type_27": DisplayData(
            name=type_27_name,
            display_type=DISPLAY_TYPE.SPHERE,
            radius=type_27_radius,
            color=type_27_color,
        ),
        "H": DisplayData(
            name=h_name,
            display_type=DISPLAY_TYPE.SPHERE,
        ),
    },
)
converter_nth_timestep = MdConverter(data_nth_timestep)
results_nth_timestep = JsonWriter.format_trajectory_data(converter_nth_timestep._data)

first_frame_data = [
    VIZ_TYPE.DEFAULT,  # agent 1
    0.0,  # id
    0.0,  # type
    42.51536560058594,  # x
    -22.60795783996582,  # y
    61.29037857055664,  # z
    0.0,  # x rotation
    0.0,  # y rotation
    0.0,  # z rotation
    type_27_radius,  # radius
    0.0,  # subpoints
    VIZ_TYPE.DEFAULT,  # agent 2
    1.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    type_27_radius,
    0.0,
    VIZ_TYPE.DEFAULT,  # agent 3
    2.0,
    1.0,
    -50.82551574707031,
    74.92604064941406,
    15.793620109558105,
    0.0,
    0.0,
    0.0,
    1.1,
    0.0,
]

third_frame_data = [
    VIZ_TYPE.DEFAULT,  # first agent
    0.0,  # id
    0.0,  # type
    46.473079681396484,  # x
    -19.95725440979004,  # y
    62.311668395996094,  # z
    0.0,  # x rotation
    0.0,  # y rotation
    0.0,  # z rotation
    type_27_radius,  # radius
    0.0,  # subpoints
    VIZ_TYPE.DEFAULT,
    1.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    0.0,
    type_27_radius,
    0.0,
    VIZ_TYPE.DEFAULT,
    2.0,
    1.0,
    -21.319805145263672,
    -76.14720153808594,
    -13.58427906036377,
    0.0,
    0.0,
    0.0,
    1.1,
    0.0,
]


@pytest.mark.parametrize(
    "bundleData, expected_bundleData",
    [
        (results_display_data["spatialData"]["bundleData"][0], first_frame_data),
        (results_display_data["spatialData"]["bundleData"][2], third_frame_data),
        # test every nth timestep (n = 2)
        (results_nth_timestep["spatialData"]["bundleData"][0], first_frame_data),
        (results_nth_timestep["spatialData"]["bundleData"][1], third_frame_data),
    ],
)
def test_bundleData(bundleData, expected_bundleData):
    assert expected_bundleData == bundleData["data"]


def test_agent_ids():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_nth_timestep)
