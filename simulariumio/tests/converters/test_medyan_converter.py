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
                487.04056375 * scale_factor_display_data,  # x
                357.50648735 * scale_factor_display_data,  # y
                222.87646995 * scale_factor_display_data,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                actin_radius * scale_factor_display_data,  # radius
                6.0,  # number of subpoints
                -32.69714035 * scale_factor_display_data,
                5.93273865 * scale_factor_display_data,
                42.56406495 * scale_factor_display_data,
                32.69714035 * scale_factor_display_data,
                -5.93273865 * scale_factor_display_data,
                -42.56406495 * scale_factor_display_data,
                VIZ_TYPE.FIBER,  # second agent
                1.0,
                0.0,
                541.39452865 * scale_factor_display_data,
                226.67005235 * scale_factor_display_data,
                308.17413585 * scale_factor_display_data,
                0.0,
                0.0,
                0.0,
                actin_radius * scale_factor_display_data,
                6.0,
                6.19982165 * scale_factor_display_data,
                53.63750955 * scale_factor_display_data,
                -0.76143355 * scale_factor_display_data,
                -6.19982165 * scale_factor_display_data,
                -53.63750955 * scale_factor_display_data,
                0.76143355 * scale_factor_display_data,
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
                (487.04056375 + translation[0]) * scale_factor_display_data,  # x
                (357.50648735 + translation[1]) * scale_factor_display_data,  # y
                (222.87646995 + translation[2]) * scale_factor_display_data,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                actin_radius * scale_factor_display_data,  # radius
                6.0,  # number of subpoints
                -32.69714035 * scale_factor_display_data,
                5.93273865 * scale_factor_display_data,
                42.56406495 * scale_factor_display_data,
                32.69714035 * scale_factor_display_data,
                -5.93273865 * scale_factor_display_data,
                -42.56406495 * scale_factor_display_data,
                VIZ_TYPE.FIBER,  # second agent
                1.0,
                0.0,
                (541.39452865 + translation[0]) * scale_factor_display_data,
                (226.67005235 + translation[1]) * scale_factor_display_data,
                (308.17413585 + translation[2]) * scale_factor_display_data,
                0.0,
                0.0,
                0.0,
                actin_radius * scale_factor_display_data,
                6.0,
                6.19982165 * scale_factor_display_data,
                53.63750955 * scale_factor_display_data,
                -0.76143355 * scale_factor_display_data,
                -6.19982165 * scale_factor_display_data,
                -53.63750955 * scale_factor_display_data,
                0.76143355 * scale_factor_display_data,
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
                562.256739333 * scale_factor,  # x
                344.651899633 * scale_factor,  # y
                155.875511478 * scale_factor,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                actin_radius * scale_factor,  # radius
                18.0,  # number of subpoints (18)
                -118.940511733 * scale_factor,  # subpoint 1 x
                25.2125855667 * scale_factor,  # subpoint 1 y
                137.276625722 * scale_factor,  # subpoint 1 z
                -103.796727133 * scale_factor,  # subpoint 2 x
                21.8906287667 * scale_factor,  # ...
                118.565951122 * scale_factor,
                -36.7464544333 * scale_factor,
                6.66101756667 * scale_factor,
                35.2893434217 * scale_factor,
                33.1607487667 * scale_factor,
                -8.01157793333 * scale_factor,
                -45.7013725783 * scale_factor,
                110.266701367 * scale_factor,
                -22.3386398333 * scale_factor,
                -119.933007108 * scale_factor,
                116.056243167 * scale_factor,
                -23.4140141333 * scale_factor,
                -125.497540578 * scale_factor,
                VIZ_TYPE.FIBER,  # second agent
                1.0,  # id
                0.0,  # type - Actin
                532.8591009 * scale_factor,
                175.573560636 * scale_factor,
                309.36513674 * scale_factor,
                0.0,
                0.0,
                0.0,
                actin_radius * scale_factor,
                15.0,  # 15 subpoints
                16.9028445 * scale_factor,
                135.189208064 * scale_factor,
                -7.33552434 * scale_factor,
                14.9139181 * scale_factor,
                111.007277964 * scale_factor,
                -6.01945524 * scale_factor,
                5.0905938 * scale_factor,
                3.668880964 * scale_factor,
                0.17561846 * scale_factor,
                -14.0376462 * scale_factor,
                -102.446758246 * scale_factor,
                5.50723656 * scale_factor,
                -22.8697102 * scale_factor,
                -147.418608746 * scale_factor,
                7.67212456 * scale_factor,
                VIZ_TYPE.FIBER,  # third agent
                2.0,  # id
                1.0,  # type - linker0
                204.0331281 * scale_factor,
                861.2036866 * scale_factor,
                292.1917403 * scale_factor,
                0.0,
                0.0,
                0.0,
                1.0 * scale_factor,  # default radius * scale_factor
                6.0,  # 6 subpoints
                12.7674767 * scale_factor,
                -6.3939099 * scale_factor,
                10.7191578 * scale_factor,
                -12.7674767 * scale_factor,
                6.3939099 * scale_factor,
                -10.7191578 * scale_factor,
                VIZ_TYPE.FIBER,  # 4th agent
                3.0,  # id
                2.0,  # type - Xlink
                659.74934485 * scale_factor,
                428.8939651 * scale_factor,
                197.6689468 * scale_factor,
                0.0,
                0.0,
                0.0,
                linker_radius * scale_factor,
                6.0,
                -2.41762365 * scale_factor,
                -7.4004388 * scale_factor,
                15.0560579 * scale_factor,
                2.41762365 * scale_factor,
                7.4004388 * scale_factor,
                -15.0560579 * scale_factor,
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
                562.99355575 * scale_factor,
                314.78730205 * scale_factor,
                344.31523845 * scale_factor,
                0.0,
                0.0,
                0.0,
                1.0 * scale_factor,  # default radius
                6.0,
                -21.60569755 * scale_factor,
                -97.97642155 * scale_factor,
                -36.94275905 * scale_factor,
                21.60569755 * scale_factor,
                97.97642155 * scale_factor,
                36.94275905 * scale_factor,
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
