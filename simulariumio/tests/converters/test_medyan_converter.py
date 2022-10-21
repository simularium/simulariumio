#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pytest

from simulariumio.medyan import MedyanConverter, MedyanData
from simulariumio import MetaData, DisplayData, InputFileData, JsonWriter
from simulariumio.constants import (
    DEFAULT_BOX_SIZE,
    DEFAULT_CAMERA_SETTINGS,
    VIZ_TYPE,
    DISPLAY_TYPE
)

data = MedyanData(
    snapshot_file=InputFileData(file_path="simulariumio/tests/data/medyan/test.traj"),
)
converter = MedyanConverter(data)
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
                    "name": "filament0",
                    "geometry": {
                        "displayType": "FIBER",
                    },
                },
                "1": {
                    "name": "linker0",
                    "geometry": {
                        "displayType": "FIBER",
                    },
                },
                "2": {
                    "name": "linker1",
                    "geometry": {
                        "displayType": "FIBER",
                    },
                },
                "3": {
                    "name": "motor1",
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


x_size = 1000.0
y_size = 1000.0
z_size = 500.0
data_with_meta_data = MedyanData(
    meta_data=MetaData(
        box_size=np.array([x_size, y_size, z_size]),
    ),
    snapshot_file=InputFileData(file_path="simulariumio/tests/data/medyan/test.traj"),
)
converter_meta_data = MedyanConverter(data_with_meta_data)
results_meta_data = JsonWriter.format_trajectory_data(converter_meta_data._data)


# test box data provided
@pytest.mark.parametrize(
    "box_size, expected_box_size",
    [
        (
            results_meta_data["trajectoryInfo"]["size"],
            {"x": x_size, "y": y_size, "z": z_size},
        )
    ],
)
def test_box_size_provided(box_size, expected_box_size):
    assert box_size == expected_box_size


actin_radius = 2.0
actin_color = "#d71f5f"
linker_radius = 0.5
linker_color = "#0080ff"
data_with_display_data = MedyanData(
    meta_data=MetaData(
        box_size=np.array([x_size, y_size, z_size]),
    ),
    snapshot_file=InputFileData(file_path="simulariumio/tests/data/medyan/test.traj"),
    filament_display_data={
        0: DisplayData(
            name="Actin",
            display_type=DISPLAY_TYPE.FIBER,
            radius=actin_radius,
            color=actin_color,
        ),
    },
    linker_display_data={
        1: DisplayData(
            name="Xlink",
            display_type=DISPLAY_TYPE.FIBER,
            radius=linker_radius,
            color=linker_color,
        ),
    },
)
converter_display_data = MedyanConverter(data_with_display_data)
results_display_data = JsonWriter.format_trajectory_data(converter_display_data._data)


# test type mapping with display data provided
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results_display_data["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": "Actin",
                    "geometry": {
                        "displayType": "FIBER",
                        "color": actin_color,
                    },
                },
                "1": {
                    "name": "linker0",
                    "geometry": {
                        "displayType": "FIBER",
                    },
                },
                "2": {
                    "name": "Xlink",
                    "geometry": {
                        "displayType": "FIBER",
                        "color": linker_color,
                    },
                },
                "3": {
                    "name": "motor1",
                    "geometry": {
                        "displayType": "FIBER",
                    },
                },
            },
        )
    ],
)
def test_typeMapping_with_display_data(typeMapping, expected_typeMapping):
    assert typeMapping == expected_typeMapping


@pytest.mark.parametrize(
    "bundleData, expected_bundleData",
    [
        (
            # just testing the first frame
            results_display_data["spatialData"]["bundleData"][0],
            [
                VIZ_TYPE.FIBER,  # first agent
                0.0,  # id
                0.0,  # type
                0.0,  # x
                0.0,  # y
                0.0,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                actin_radius,  # radius
                6.0,  # number of subpoints
                454.3434234,
                363.439226,
                265.4405349,
                519.7377041,
                351.5737487,
                180.312405,
                VIZ_TYPE.FIBER,  # second agent
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                actin_radius,
                6.0,
                547.5943503,
                280.3075619,
                307.4127023,
                535.194707,
                173.0325428,
                308.9355694,
            ],
        )
    ],
)
def test_bundleData(bundleData, expected_bundleData):
    assert expected_bundleData == bundleData["data"]


def test_agent_ids():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)


# add in drawing endpoints
data_with_drawing_endpoints = MedyanData(
    meta_data=MetaData(
        box_size=np.array([x_size, y_size, z_size]),
    ),
    snapshot_file=InputFileData(file_path="simulariumio/tests/data/medyan/test.traj"),
    filament_display_data={
        0: DisplayData(
            name="Actin",
            display_type=DISPLAY_TYPE.FIBER,
            radius=actin_radius,
            color=actin_color,
        ),
    },
    linker_display_data={
        1: DisplayData(
            name="Xlink",
            display_type=DISPLAY_TYPE.FIBER,
            radius=linker_radius,
            color=linker_color,
        ),
    },
    agents_with_endpoints=["Xlink"],
)
converter_drawing_endpoints = MedyanConverter(data_with_drawing_endpoints)
results_drawing_endpoints = JsonWriter.format_trajectory_data(
    converter_drawing_endpoints._data
)


@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results_drawing_endpoints["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": "Actin",
                    "geometry": {
                        "displayType": "FIBER",
                        "color": actin_color,
                    },
                },
                "1": {
                    "name": "linker0",
                    "geometry": {
                        "displayType": "FIBER",
                    },
                },
                "2": {
                    "name": "Xlink",
                    "geometry": {
                        "displayType": "FIBER",
                        "color": linker_color,
                    },
                },
                "3": {
                    "name": "Xlink End",
                    "geometry": {
                        "displayType": "SPHERE",
                    },
                },
                "4": {
                    "name": "motor1",
                    "geometry": {
                        "displayType": "FIBER",
                    },
                },
            },
        )
    ],
)
def test_typeMapping_with_drawing_endpoints(typeMapping, expected_typeMapping):
    assert typeMapping == expected_typeMapping


@pytest.mark.parametrize(
    "bundleData, expected_bundleData",
    [
        (
            # just testing the first frame
            results_drawing_endpoints["spatialData"]["bundleData"][1],
            [
                VIZ_TYPE.FIBER,  # first agent
                0.0,  # id
                0.0,  # type - Actin
                0.0,  # x
                0.0,  # y
                0.0,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                actin_radius,  # radius
                18.0,  # number of subpoints (18)
                443.3162276,  # subpoint 1 x
                369.8644852,  # subpoint 1 y
                293.1521372,  # subpoint 1 z
                458.4600122,  # subpoint 2 x
                366.5425284,  # ...
                274.4414626,
                525.5102849,
                351.3129172,
                191.1648549,
                595.4174881,
                336.6403217,
                110.1741389,
                672.5234407,
                322.3132598,
                35.94250437,
                678.3129825,
                321.2378855,
                30.3779709,
                VIZ_TYPE.FIBER,  # second agent
                1.0,  # id
                0.0,  # type - Actin
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                actin_radius,
                15.0,  # 15 subpoints
                549.7619454,
                310.7627687,
                302.0296124,
                547.773019,
                286.5808386,
                303.3456815,
                537.9496947,
                179.2424416,
                309.5407552,
                518.8214547,
                73.12680239,
                314.8723733,
                509.9893907,
                28.15495189,
                317.0372613,
                VIZ_TYPE.FIBER,  # third agent
                2.0,  # id
                1.0,  # type - linker0
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,  # default radius
                6.0,  # 6 subpoints
                216.8006048,
                854.8097767,
                302.9108981,
                191.2656514,
                867.5975965,
                281.4725825,
                VIZ_TYPE.FIBER,  # 4th agent
                3.0,  # id
                2.0,  # type - Xlink
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                linker_radius,
                6.0,
                657.3317212,
                421.4935263,
                212.7250047,
                662.1669685,
                436.2944039,
                182.6128889,
                VIZ_TYPE.DEFAULT,  # 5th agent
                4.0,  # id
                3.0,  # type - Xlink End
                657.3317212,
                421.4935263,
                212.7250047,
                0.0,
                0.0,
                0.0,
                1.0,  # default radius
                0.0,
                VIZ_TYPE.DEFAULT,  # 6th agent
                5.0,  # id
                3.0,  # type - Xlink End
                662.1669685,
                436.2944039,
                182.6128889,
                0.0,
                0.0,
                0.0,
                1.0,  # default radius
                0.0,
                VIZ_TYPE.FIBER,  # 7th agent
                6.0,  # id
                4.0,  # motor1
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,  # default radius
                6.0,
                541.3878582,
                216.8108805,
                307.3724794,
                584.5992533,
                412.7637236,
                381.2579975,
            ],
        )
    ],
)
def test_bundleData_drawing_endpoints(bundleData, expected_bundleData):
    assert expected_bundleData == bundleData["data"]


def test_agent_ids_drawing_endpoints():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_drawing_endpoints)
