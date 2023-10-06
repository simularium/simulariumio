#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pytest
from unittest.mock import Mock

from simulariumio.medyan import MedyanConverter, MedyanData
from simulariumio import MetaData, DisplayData, InputFileData, JsonWriter
from simulariumio.constants import (
    DEFAULT_BOX_SIZE,
    DEFAULT_CAMERA_SETTINGS,
    VIZ_TYPE,
    DISPLAY_TYPE,
    VIEWER_DIMENSION_RANGE,
)
from simulariumio.exceptions import InputDataError

data = MedyanData(
    snapshot_file=InputFileData(file_path="simulariumio/tests/data/medyan/test.traj"),
    center=False,
)
converter = MedyanConverter(data)
results = JsonWriter.format_trajectory_data(converter._data)

# value of automatically generated scale factor, so that position
# data fits within VIEWER_DIMENSION_RANGE
max_range = 868.5975965
auto_scale_factor = VIEWER_DIMENSION_RANGE.MAX / max_range


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
    center=False,
)
converter_meta_data = MedyanConverter(data_with_meta_data)
results_meta_data = JsonWriter.format_trajectory_data(converter_meta_data._data)


# test box data provided
@pytest.mark.parametrize(
    "box_size, expected_box_size",
    [
        (
            results_meta_data["trajectoryInfo"]["size"],
            {
                "x": x_size * auto_scale_factor,
                "y": y_size * auto_scale_factor,
                "z": z_size * auto_scale_factor,
            },
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
    center=False,
)
converter_display_data = MedyanConverter(data_with_display_data)
results_display_data = JsonWriter.format_trajectory_data(converter_display_data._data)
scale_factor_display_data = VIEWER_DIMENSION_RANGE.MAX / (max_range + 2 * linker_radius)


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
                actin_radius * scale_factor_display_data,  # radius
                6.0,  # number of subpoints
                454.3434234 * scale_factor_display_data,
                363.439226 * scale_factor_display_data,
                265.4405349 * scale_factor_display_data,
                519.7377041 * scale_factor_display_data,
                351.5737487 * scale_factor_display_data,
                180.312405 * scale_factor_display_data,
                VIZ_TYPE.FIBER,  # second agent
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                actin_radius * scale_factor_display_data,
                6.0,
                547.5943503 * scale_factor_display_data,
                280.3075619 * scale_factor_display_data,
                307.4127023 * scale_factor_display_data,
                535.194707 * scale_factor_display_data,
                173.0325428 * scale_factor_display_data,
                308.9355694 * scale_factor_display_data,
            ],
        )
    ],
)
def test_bundleData(bundleData, expected_bundleData):
    assert np.isclose(expected_bundleData, bundleData["data"]).all()


def test_agent_ids():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)


data_centered = MedyanData(
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
    center=True,
)
converter_centered = MedyanConverter(data_centered)
results_centered = JsonWriter.format_trajectory_data(converter_centered._data)
translation = [-338.15649125, -432.79879825, -189.62899875]


@pytest.mark.parametrize(
    "bundleData, expected_bundleData",
    [
        (
            # just testing the first frame
            results_centered["spatialData"]["bundleData"][0],
            [
                VIZ_TYPE.FIBER,  # first agent
                0.0,  # id
                0.0,  # type
                0,  # x
                0,  # y
                0,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                actin_radius * scale_factor_display_data,  # radius
                6.0,  # number of subpoints
                (454.3434234 + translation[0]) * scale_factor_display_data,
                (363.439226 + translation[1]) * scale_factor_display_data,
                (265.4405349 + translation[2]) * scale_factor_display_data,
                (519.7377041 + translation[0]) * scale_factor_display_data,
                (351.5737487 + translation[1]) * scale_factor_display_data,
                (180.312405 + translation[2]) * scale_factor_display_data,
                VIZ_TYPE.FIBER,  # second agent
                1.0,
                0.0,
                0,
                0,
                0,
                0.0,
                0.0,
                0.0,
                actin_radius * scale_factor_display_data,
                6.0,
                (547.5943503 + translation[0]) * scale_factor_display_data,
                (280.3075619 + translation[1]) * scale_factor_display_data,
                (307.4127023 + translation[2]) * scale_factor_display_data,
                (535.194707 + translation[0]) * scale_factor_display_data,
                (173.0325428 + translation[1]) * scale_factor_display_data,
                (308.9355694 + translation[2]) * scale_factor_display_data,
            ],
        )
    ],
)
def test_centered_data(bundleData, expected_bundleData):
    assert False not in np.isclose(expected_bundleData, bundleData["data"])


# add in drawing endpoints
scale_factor = 0.1
data_with_drawing_endpoints = MedyanData(
    meta_data=MetaData(
        box_size=np.array([x_size, y_size, z_size]),
        scale_factor=scale_factor,
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
    center=False,
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
                actin_radius * scale_factor,  # radius
                18.0,  # number of subpoints (18)
                443.3162276 * scale_factor,  # subpoint 1 x
                369.8644852 * scale_factor,  # subpoint 1 y
                293.1521372 * scale_factor,  # subpoint 1 z
                458.4600122 * scale_factor,  # subpoint 2 x
                366.5425284 * scale_factor,  # ...
                274.4414626 * scale_factor,
                525.5102849 * scale_factor,
                351.3129172 * scale_factor,
                191.1648549 * scale_factor,
                595.4174881 * scale_factor,
                336.6403217 * scale_factor,
                110.1741389 * scale_factor,
                672.5234407 * scale_factor,
                322.3132598 * scale_factor,
                35.94250437 * scale_factor,
                678.3129825 * scale_factor,
                321.2378855 * scale_factor,
                30.3779709 * scale_factor,
                VIZ_TYPE.FIBER,  # second agent
                1.0,  # id
                0.0,  # type - Actin
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                actin_radius * scale_factor,
                15.0,  # 15 subpoints
                549.7619454 * scale_factor,
                310.7627687 * scale_factor,
                302.0296124 * scale_factor,
                547.773019 * scale_factor,
                286.5808386 * scale_factor,
                303.3456815 * scale_factor,
                537.9496947 * scale_factor,
                179.2424416 * scale_factor,
                309.5407552 * scale_factor,
                518.8214547 * scale_factor,
                73.12680239 * scale_factor,
                314.8723733 * scale_factor,
                509.9893907 * scale_factor,
                28.15495189 * scale_factor,
                317.0372613 * scale_factor,
                VIZ_TYPE.FIBER,  # third agent
                2.0,  # id
                1.0,  # type - linker0
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0 * scale_factor,  # default radius * scale_factor
                6.0,  # 6 subpoints
                216.8006048 * scale_factor,
                854.8097767 * scale_factor,
                302.9108981 * scale_factor,
                191.2656514 * scale_factor,
                867.5975965 * scale_factor,
                281.4725825 * scale_factor,
                VIZ_TYPE.FIBER,  # 4th agent
                3.0,  # id
                2.0,  # type - Xlink
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                linker_radius * scale_factor,
                6.0,
                657.3317212 * scale_factor,
                421.4935263 * scale_factor,
                212.7250047 * scale_factor,
                662.1669685 * scale_factor,
                436.2944039 * scale_factor,
                182.6128889 * scale_factor,
                VIZ_TYPE.DEFAULT,  # 5th agent
                4.0,  # id
                3.0,  # type - Xlink End
                657.3317212 * scale_factor,
                421.4935263 * scale_factor,
                212.7250047 * scale_factor,
                0.0,
                0.0,
                0.0,
                1.0 * scale_factor,  # default radius
                0.0,
                VIZ_TYPE.DEFAULT,  # 6th agent
                5.0,  # id
                3.0,  # type - Xlink End
                662.1669685 * scale_factor,
                436.2944039 * scale_factor,
                182.6128889 * scale_factor,
                0.0,
                0.0,
                0.0,
                1.0 * scale_factor,  # default radius
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
                1.0 * scale_factor,  # default radius
                6.0,
                541.3878582 * scale_factor,
                216.8108805 * scale_factor,
                307.3724794 * scale_factor,
                584.5992533 * scale_factor,
                412.7637236 * scale_factor,
                381.2579975 * scale_factor,
            ],
        )
    ],
)
def test_bundleData_drawing_endpoints(bundleData, expected_bundleData):
    assert np.isclose(expected_bundleData, bundleData["data"]).all()


def test_agent_ids_drawing_endpoints():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_drawing_endpoints)


def test_input_file_error():
    # path to a file of the wrong format
    wrong_file = MedyanData(
        snapshot_file=InputFileData(file_path="simulariumio/tests/data/md/example.xyz"),
    )
    with pytest.raises(InputDataError):
        MedyanConverter(wrong_file)

    # file missing first frame start
    invalid_traj = MedyanData(
        snapshot_file=InputFileData(
            file_path="simulariumio/tests/data/malformed_data/malformed_medyan.traj"
        ),
    )
    with pytest.raises(InputDataError):
        MedyanConverter(invalid_traj)


def test_callback_fn():
    callback_fn_0 = Mock()
    call_interval = 0.000000001
    MedyanConverter(data, callback_fn_0, call_interval)
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
