#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np

from simulariumio.nerdss import (
    NerdssConverter,
    NerdssData,
)
from simulariumio import MetaData, UnitData, DisplayData, JsonWriter
from simulariumio.constants import (
    DEFAULT_BOX_SIZE,
    DEFAULT_CAMERA_SETTINGS,
    DISPLAY_TYPE,
    VIZ_TYPE,
)

data = NerdssData(path_to_pdb_files="simulariumio/tests/data/nerdss/virus_pdb")
converter = NerdssConverter(data)
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
                    "name": "IL#COM",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "1": {
                    "name": "gag#COM",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "2": {
                    "name": "gag#mem",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "3": {
                    "name": "gag#hom",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "4": {
                    "name": "gag#hx1",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "5": {
                    "name": "gag#hx2",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "6": {
                    "name": "gag#ref",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "7": {
                    "name": "bonds",
                    "geometry": {
                        "displayType": "FIBER",
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
expected_spatial_units = UnitData("m", 1.0)


@pytest.mark.parametrize(
    "spatialUnits, expected_spatialUnits",
    [
        (
            results["trajectoryInfo"]["spatialUnits"],
            {
                "magnitude": expected_spatial_units.magnitude,
                "name": expected_spatial_units.name,
            },
        )
    ],
)
def test_spatialUnits_default(spatialUnits, expected_spatialUnits):
    assert spatialUnits == expected_spatialUnits


box_size = 2.0
data_with_meta_data = NerdssData(
    path_to_pdb_files="simulariumio/tests/data/nerdss/virus_pdb",
    meta_data=MetaData(
        box_size=np.array([box_size, box_size, box_size]),
    ),
)
converter_meta_data = NerdssConverter(data_with_meta_data)
results_meta_data = JsonWriter.format_trajectory_data(converter_meta_data._data)


# test box size provided
@pytest.mark.parametrize(
    "box_size, expected_box_size",
    [
        (
            results_meta_data["trajectoryInfo"]["size"],
            {
                "x": box_size,
                "y": box_size,
                "z": box_size,
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
data_with_unit_data = NerdssData(
    path_to_pdb_files="simulariumio/tests/data/nerdss/virus_pdb",
    time_units=UnitData(time_unit_name, time_unit_value),
    spatial_units=UnitData(spatial_unit_name),
)
converter_unit_data = NerdssConverter(data_with_unit_data)
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
expected_spatial_units = UnitData(spatial_unit_name, 1.0)


@pytest.mark.parametrize(
    "spatialUnits, expected_spatialUnits",
    [
        (
            results_unit_data["trajectoryInfo"]["spatialUnits"],
            {
                "magnitude": expected_spatial_units.magnitude,
                "name": expected_spatial_units.name,
            },
        )
    ],
)
def test_spatialUnits_provided(spatialUnits, expected_spatialUnits):
    assert spatialUnits == expected_spatialUnits


g_radius = 0.01
g_color = "#dfdacd"
gag_mem_color = "#0080ff"

data_with_display_data = NerdssData(
    path_to_pdb_files="simulariumio/tests/data/nerdss/virus_pdb",
    meta_data=MetaData(
        box_size=np.array([box_size, box_size, box_size]),
    ),
    display_data={
        "gag#COM": DisplayData(
            name="GAG - Center of Mass",
            display_type=DISPLAY_TYPE.SPHERE,
            color=g_color,
            radius=g_radius,
        ),
        "gag#mem": DisplayData(
            name="GAG - mem",
            display_type=DISPLAY_TYPE.SPHERE,
            color=gag_mem_color,
        ),
        "bonds": DisplayData(
            name="Bond",
            display_type=DISPLAY_TYPE.FIBER,
        ),
    },
)
converter_display_data = NerdssConverter(data_with_display_data)
results_display_data = JsonWriter.format_trajectory_data(converter_display_data._data)


# test type mapping with display data provided
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results_display_data["trajectoryInfo"]["typeMapping"]["1"],
            {
                "name": "GAG - Center of Mass",
                "geometry": {
                    "displayType": "SPHERE",
                    "color": g_color,
                },
            },
        ),
        (
            results_display_data["trajectoryInfo"]["typeMapping"]["2"],
            {
                "name": "GAG - mem",
                "geometry": {
                    "displayType": "SPHERE",
                    "color": gag_mem_color,
                },
            },
        ),
        (
            results_display_data["trajectoryInfo"]["typeMapping"]["7"],
            {
                "name": "Bond",
                "geometry": {
                    "displayType": "FIBER",
                },
            },
        ),
    ],
)
def test_typeMapping_with_display_data(typeMapping, expected_typeMapping):
    assert expected_typeMapping == typeMapping


def test_agent_ids():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)


@pytest.mark.parametrize(
    "bundleData, expected_bundleData",
    [
        (
            # just testing the first few agents of the first frame
            results_display_data["spatialData"]["bundleData"][0],
            [
                VIZ_TYPE.DEFAULT,  # first agent
                0.0,  # id
                0.0,  # type
                134.02,  # x
                134.02,  # y
                134.02,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                1.0,  # radius
                0.0,  # number of subpoints
                VIZ_TYPE.DEFAULT,  # second agent
                1.0,
                1.0,
                134.02,
                134.02,
                134.02,
                0.0,
                0.0,
                0.0,
                g_radius,
                0.0,
                VIZ_TYPE.DEFAULT,  # third agent
                2.0,
                1.0,
                126.49,
                68.071,
                40.818,
                0.0,
                0.0,
                0.0,
                g_radius,
                0.0,
                VIZ_TYPE.DEFAULT,  # forth agent
                3.0,
                2.0,
                128.32,
                68.104,
                40.012,
                0.0,
                0.0,
                0.0,
                1.0,
                0.0,
            ],
        )
    ],
)
def test_bundleData(bundleData, expected_bundleData):
    assert np.isclose(expected_bundleData, bundleData["data"][0:44]).all()
