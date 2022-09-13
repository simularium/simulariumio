#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pytest

from simulariumio.physicell import PhysicellConverter, PhysicellData
from simulariumio import MetaData, DisplayData, JsonWriter, UnitData
from simulariumio.constants import DEFAULT_BOX_SIZE, DEFAULT_CAMERA_SETTINGS, VIZ_TYPE


data = PhysicellData(
    timestep=360.0,
    path_to_output_dir="simulariumio/tests/data/physicell/output/",
)
converter = PhysicellConverter(data)
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
                    "name": "cell1#phase4",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "1": {
                    "name": "cell0#phase4",
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


size_x = 1000.0
size_y = 1000.0
size_z = 100.0
scale_factor = 0.01
time_unit = "ms"
data_with_meta_data = PhysicellData(
    meta_data=MetaData(
        box_size=np.array([size_x, size_y, size_z]),
        scale_factor=scale_factor,
    ),
    timestep=360.0,
    path_to_output_dir="simulariumio/tests/data/physicell/output/",
    time_units=UnitData(
        name=time_unit,
    ),
)
converter_meta_data = PhysicellConverter(data_with_meta_data)
results_meta_data = JsonWriter.format_trajectory_data(converter_meta_data._data)


# test box data provided
@pytest.mark.parametrize(
    "box_size, expected_box_size",
    [
        (
            results_meta_data["trajectoryInfo"]["size"],
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


# test time units provided
@pytest.mark.parametrize(
    "timeUnits, expected_timeUnits",
    [
        (
            results_meta_data["trajectoryInfo"]["timeUnits"],
            {
                "magnitude": 1.0,
                "name": time_unit,
            },
        )
    ],
)
def test_timeUnits_provided(timeUnits, expected_timeUnits):
    assert timeUnits == expected_timeUnits


test_name = "Sample name"
test_radius = 30.0
test_color = "#0080ff"
test_phase = "interphase"

data_with_display_data = PhysicellData(
    meta_data=MetaData(
        box_size=np.array([size_x, size_y, size_z]),
        scale_factor=scale_factor,
    ),
    timestep=360.0,
    path_to_output_dir="simulariumio/tests/data/physicell/output/",
    display_data={
        0: DisplayData(
            name=test_name,
            radius=test_radius,
            color=test_color,
        ),
    },
    phase_names={1: {4: test_phase}},
)
converter_display_data = PhysicellConverter(data_with_display_data)
results_display_data = JsonWriter.format_trajectory_data(converter_display_data._data)


# test type mapping provided
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results_display_data["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": f"cell1#{test_phase}",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "1": {
                    "name": f"{test_name}#phase4",
                    "geometry": {
                        "displayType": "SPHERE",
                        "color": test_color,
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
                0.0,  # id
                0.0,  # type
                -4.2700000000000005,  # x
                -2.5100000000000002,  # y
                0.0,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                0.08412710547954229,
                0.0,
                VIZ_TYPE.DEFAULT,
                1.0,
                1.0,
                -2.2800000000000002,
                4.3,
                0.0,
                0.0,
                0.0,
                0.0,
                test_radius * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                2.0,
                1.0,
                4.23,
                3.7800000000000002,
                0.0,
                0.0,
                0.0,
                0.0,
                test_radius * scale_factor,
                0.0,
            ],
        )
    ],
)
def test_bundleData(bundleData, expected_bundleData):
    assert expected_bundleData == bundleData["data"]


def test_agent_ids():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)
