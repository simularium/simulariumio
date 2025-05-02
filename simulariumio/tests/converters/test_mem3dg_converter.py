#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np

from simulariumio.mem3dg import (
    Mem3dgConverter,
    Mem3dgData,
)
from simulariumio import MetaData, UnitData, JsonWriter
from simulariumio.constants import (
    DEFAULT_BOX_SIZE,
    DEFAULT_CAMERA_SETTINGS,
    VIZ_TYPE,
)

data = Mem3dgData(input_file_path="simulariumio/tests/data/mem3dg/traj.nc")
converter = Mem3dgConverter(data)
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
                    "name": "object#frame0",
                    "geometry": {
                        "displayType": "OBJ",
                        "url": "0.obj",
                    },
                },
                "1": {
                    "name": "object#frame1",
                    "geometry": {
                        "displayType": "OBJ",
                        "url": "1.obj",
                    },
                },
                "10": {
                    "name": "object#frame10",
                    "geometry": {
                        "displayType": "OBJ",
                        "url": "10.obj",
                    },
                },
                "11": {
                    "name": "object#frame11",
                    "geometry": {
                        "displayType": "OBJ",
                        "url": "11.obj",
                    },
                },
                "2": {
                    "name": "object#frame2",
                    "geometry": {
                        "displayType": "OBJ",
                        "url": "2.obj",
                    },
                },
                "3": {
                    "name": "object#frame3",
                    "geometry": {
                        "displayType": "OBJ",
                        "url": "3.obj",
                    },
                },
                "4": {
                    "name": "object#frame4",
                    "geometry": {
                        "displayType": "OBJ",
                        "url": "4.obj",
                    },
                },
                "5": {
                    "name": "object#frame5",
                    "geometry": {
                        "displayType": "OBJ",
                        "url": "5.obj",
                    },
                },
                "6": {
                    "name": "object#frame6",
                    "geometry": {
                        "displayType": "OBJ",
                        "url": "6.obj",
                    },
                },
                "7": {
                    "name": "object#frame7",
                    "geometry": {
                        "displayType": "OBJ",
                        "url": "7.obj",
                    },
                },
                "8": {
                    "name": "object#frame8",
                    "geometry": {
                        "displayType": "OBJ",
                        "url": "8.obj",
                    },
                },
                "9": {
                    "name": "object#frame9",
                    "geometry": {
                        "displayType": "OBJ",
                        "url": "9.obj",
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
data_with_meta_data = Mem3dgData(
    input_file_path="simulariumio/tests/data/mem3dg/traj.nc",
    meta_data=MetaData(
        box_size=np.array([box_size, box_size, box_size]),
    ),
)
converter_meta_data = Mem3dgConverter(data_with_meta_data)
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
data_with_unit_data = Mem3dgData(
    input_file_path="simulariumio/tests/data/mem3dg/traj.nc",
    time_units=UnitData(time_unit_name, time_unit_value),
    spatial_units=UnitData(spatial_unit_name),
)
converter_unit_data = Mem3dgConverter(data_with_unit_data)
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


color = "#dfdacd"
name = "testname"

data_with_optional_data = Mem3dgData(
    input_file_path="simulariumio/tests/data/mem3dg/traj.nc",
    meta_data=MetaData(
        box_size=np.array([box_size, box_size, box_size]),
    ),
    agent_color=color,
    agent_name=name,
)
converter_optional_data = Mem3dgConverter(data_with_optional_data)
results_optional_data = JsonWriter.format_trajectory_data(converter_optional_data._data)


# test type mapping with some optional data provided
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results_optional_data["trajectoryInfo"]["typeMapping"]["1"],
            {
                "name": f"{name}#frame1",
                "geometry": {"displayType": "OBJ", "color": color, "url": "1.obj"},
            },
        ),
        (
            results_optional_data["trajectoryInfo"]["typeMapping"]["7"],
            {
                "name": f"{name}#frame7",
                "geometry": {"displayType": "OBJ", "color": color, "url": "7.obj"},
            },
        ),
    ],
)
def test_typeMapping_with_display_data(typeMapping, expected_typeMapping):
    assert expected_typeMapping == typeMapping


def test_agent_ids():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_optional_data)


@pytest.mark.parametrize(
    "bundleData, expected_bundleData",
    [
        (
            results_optional_data["spatialData"]["bundleData"][0],
            [
                VIZ_TYPE.DEFAULT,  # first agent
                0.0,  # id
                0.0,  # type
                0.0,  # x
                0.0,  # y
                0.0,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                1.0,  # radius
                0.0,  # number of subpoints
            ],
        )
    ],
)
def test_bundleData(bundleData, expected_bundleData):
    assert np.isclose(expected_bundleData, bundleData["data"]).all()


# test the generated .obj file
vertices = []
faces = []
with open("1.obj", "r") as f:
    for line in f:
        if line.startswith("v "):
            vertex = list(map(float, line.strip().split()[1:]))
            vertices.append(vertex)
        if line.startswith("f"):
            face = list(map(int, line.strip().split()[1:]))
            faces.append(face)


# just test first 10 vertices and first 10 faces
@pytest.mark.parametrize(
    "objData, expected_objData",
    [
        (
            vertices[0:10],
            [
                [-0.044172474330887876, -0.03292575680180331, -1.4175751745389955],
                [-0.19121607468987623, -0.01397969566814584, -1.3875799727888973],
                [-0.11250378749193095, -0.17990264986600266, -1.379482681435413],
                [0.05576838982803812, -0.14570813108980143, -1.399674042301235],
                [0.15558132766053154, -0.25183807392352425, -1.3353307393866578],
                [0.18377789077849535, -0.058222036646119635, -1.3871295603540683],
                [-0.07103420756652815, 0.12890346705753208, -1.4027636325505357],
                [-0.21819128564743445, 0.1535233470313994, -1.3532338908453854],
                [0.08002216511514706, 0.05349158797718862, -1.414705819367836],
                [0.21652298025580569, 0.12117631622076441, -1.3635688485379431],
            ],
        ),
        (
            faces[0:10],
            [
                [3, 2, 1],
                [3, 1, 4],
                [3, 4, 18],
                [6, 5, 4],
                [7, 1, 2],
                [7, 2, 8],
                [1, 9, 4],
                [7, 9, 1],
                [6, 4, 9],
                [6, 9, 10],
            ],
        ),
    ],
)
def test_obj_data_values(objData, expected_objData):
    assert np.isclose(objData, expected_objData).all()


def test_obj_data_faces():
    # values in the faces list are 1 based indices to the vertices,
    # so all values should be between 1 and the size of vertices
    assert min(min(faces)) >= 1
    assert max(max(faces)) <= len(vertices)
