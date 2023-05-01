#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from simulariumio import TrajectoryConverter, JsonWriter, DisplayData
from simulariumio.tests.conftest import (
    fiber_agents_type_mapping,
    minimal_custom_data,
    mixed_agents_type_mapping,
    mixed_agents,
    fiber_agents,
    minimal_custom_type_mappings,
    sphere_group_agents,
)
from simulariumio.constants import (
    DEFAULT_BOX_SIZE,
    DEFAULT_CAMERA_SETTINGS,
    CURRENT_VERSION,
    VIZ_TYPE,
    MAX_AGENT_ID,
    DISPLAY_TYPE,
)

from simulariumio.exceptions import DataError


def mixed_agents_invalid_agent_id():
    # Agent IDs are larger than a 32 bit int can represent
    result = mixed_agents()
    result.agent_data.unique_ids[0][0] = MAX_AGENT_ID + 1
    return result


# 3 default agents (radius 5-10) with all optional trajectory
# parameters left blank
default_agents_trajectory = minimal_custom_data()
default_agents_trajectory.meta_data._set_box_size()
default_agents_converter = TrajectoryConverter(default_agents_trajectory)
default_agents_data = JsonWriter.format_trajectory_data(default_agents_converter._data)

# 2 default agents (radius 5-10) and 3 fiber agents
# at given positions for 3 frames, no plots
mixed_agents_trajectory = mixed_agents()
mixed_agents_converter = TrajectoryConverter(mixed_agents_trajectory)
mixed_agents_data = JsonWriter.format_trajectory_data(mixed_agents_converter._data)

# 3 fiber agents with points drawn
# at given positions for 3 frames, no plots
fiber_agents_trajectory = fiber_agents()
fiber_agents_converter = TrajectoryConverter(fiber_agents_trajectory)
fiber_agents_data = JsonWriter.format_trajectory_data(fiber_agents_converter._data)

# 2 sphere group agents with 3 spheres each for 3 frames
sphere_group_trajectory = sphere_group_agents()
sphere_group_converter = TrajectoryConverter(sphere_group_trajectory)
sphere_group_data = JsonWriter.format_trajectory_data(sphere_group_converter._data)


# test trajectory info
@pytest.mark.parametrize(
    "trajectory_version, expected_version",
    [
        (
            default_agents_data["trajectoryInfo"]["version"],
            CURRENT_VERSION.TRAJECTORY_INFO,
        ),
        (
            mixed_agents_data["trajectoryInfo"]["version"],
            CURRENT_VERSION.TRAJECTORY_INFO,
        ),
        (
            fiber_agents_data["trajectoryInfo"]["version"],
            CURRENT_VERSION.TRAJECTORY_INFO,
        ),
        (
            sphere_group_data["trajectoryInfo"]["version"],
            CURRENT_VERSION.TRAJECTORY_INFO,
        ),
    ],
)
def test_versions_trajectory(trajectory_version, expected_version):
    assert trajectory_version == expected_version


# test time units
@pytest.mark.parametrize(
    "timeUnits, expected_timeUnits",
    [
        (
            # default time units: 1.0 sec
            default_agents_data["trajectoryInfo"]["timeUnits"],
            {"magnitude": 1.0, "name": "s"},
        ),
        (
            mixed_agents_data["trajectoryInfo"]["timeUnits"],
            {"magnitude": 2.0, "name": "s"},
        ),
        (
            fiber_agents_data["trajectoryInfo"]["timeUnits"],
            {"magnitude": 1.0, "name": "µs"},
        ),
        (
            sphere_group_data["trajectoryInfo"]["timeUnits"],
            {"magnitude": 1.0, "name": "s"},
        ),
    ],
)
def test_timeUnits(timeUnits, expected_timeUnits):
    assert timeUnits == expected_timeUnits


# test spatial units
@pytest.mark.parametrize(
    "spatialUnits, expected_spatialUnits",
    [
        (
            # default spatial units: 1.0 m
            default_agents_data["trajectoryInfo"]["spatialUnits"],
            {"magnitude": 1.0, "name": "m"},
        ),
        (
            mixed_agents_data["trajectoryInfo"]["spatialUnits"],
            {"magnitude": 1.0, "name": "µm"},
        ),
        (
            fiber_agents_data["trajectoryInfo"]["spatialUnits"],
            {"magnitude": 10.0, "name": "m"},
        ),
        (
            sphere_group_data["trajectoryInfo"]["spatialUnits"],
            {"magnitude": 1.0, "name": "m"},
        ),
    ],
)
def test_spatialUnits(spatialUnits, expected_spatialUnits):
    assert spatialUnits == expected_spatialUnits


# test box size
@pytest.mark.parametrize(
    "size, expected_size",
    [
        (
            default_agents_data["trajectoryInfo"]["size"],
            {
                "x": DEFAULT_BOX_SIZE[0],
                "y": DEFAULT_BOX_SIZE[1],
                "z": DEFAULT_BOX_SIZE[2],
            },
        ),
        (
            mixed_agents_data["trajectoryInfo"]["size"],
            {
                "x": DEFAULT_BOX_SIZE[0] * 10,
                "y": DEFAULT_BOX_SIZE[1] * 10,
                "z": DEFAULT_BOX_SIZE[2] * 10,
            },
        ),
        (
            fiber_agents_data["trajectoryInfo"]["size"],
            {
                "x": DEFAULT_BOX_SIZE[0] * 10,
                "y": DEFAULT_BOX_SIZE[1] * 10,
                "z": DEFAULT_BOX_SIZE[2] * 10,
            },
        ),
        (
            sphere_group_data["trajectoryInfo"]["size"],
            {
                "x": DEFAULT_BOX_SIZE[0],
                "y": DEFAULT_BOX_SIZE[1],
                "z": DEFAULT_BOX_SIZE[2],
            },
        ),
    ],
)
def test_box_size(size, expected_size):
    assert size == expected_size


# test camera
@pytest.mark.parametrize(
    "camera, expected_camera",
    [
        (
            default_agents_data["trajectoryInfo"]["cameraDefault"],
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
        ),
        (
            mixed_agents_data["trajectoryInfo"]["cameraDefault"],
            {
                "position": {
                    "x": 0.0,
                    "y": 120.0,
                    "z": 0.0,
                },
                "lookAtPosition": {
                    "x": 10.0,
                    "y": 0.0,
                    "z": 0.0,
                },
                "upVector": {
                    "x": 0.0,
                    "y": 0.0,
                    "z": 1.0,
                },
                "fovDegrees": 60.0,
            },
        ),
        (
            fiber_agents_data["trajectoryInfo"]["cameraDefault"],
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
        ),
        (
            sphere_group_data["trajectoryInfo"]["cameraDefault"],
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
        ),
    ],
)
def test_camera_defaults(camera, expected_camera):
    assert camera == expected_camera


# test type mapping
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            default_agents_data["trajectoryInfo"]["typeMapping"],
            minimal_custom_type_mappings(),
        ),
        (
            mixed_agents_data["trajectoryInfo"]["typeMapping"],
            mixed_agents_type_mapping(),
        ),
        (
            fiber_agents_data["trajectoryInfo"]["typeMapping"],
            fiber_agents_type_mapping(),
        ),
        (
            sphere_group_data["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": "A",
                    "geometry": {
                        "displayType": "SPHERE_GROUP",
                    },
                },
                "1": {
                    "name": "B",
                    "geometry": {
                        "displayType": "SPHERE_GROUP",
                    },
                },
            },
        ),
    ],
)
def test_type_mapping(typeMapping, expected_typeMapping):
    assert typeMapping == expected_typeMapping


# test model info
@pytest.mark.parametrize(
    "modelInfo, expected_modelInfo",
    [
        (
            default_agents_data["trajectoryInfo"].get("modelInfo", {}),
            {},
        ),
        (
            mixed_agents_data["trajectoryInfo"]["modelInfo"],
            {
                "title": "Some agent-based model",
                "version": "8.1",
                "authors": "A Modeler",
                "description": (
                    "An agent-based model started with " "low agent concentrations"
                ),
                "doi": "10.7554/eLife.49840",
                "inputDataUrl": "https://allencell.org",
            },
        ),
        (
            fiber_agents_data["trajectoryInfo"]["modelInfo"],
            {
                "title": "Some fibers",
                "authors": "A Modeler",
            },
        ),
        (
            sphere_group_data["trajectoryInfo"].get("modelInfo", {}),
            {},
        ),
    ],
)
def test_model_info(modelInfo, expected_modelInfo):
    assert modelInfo == expected_modelInfo


# test spatial data
@pytest.mark.parametrize(
    "spatial_version, expected_version",
    [
        (default_agents_data["spatialData"]["version"], CURRENT_VERSION.SPATIAL_DATA),
        (mixed_agents_data["spatialData"]["version"], CURRENT_VERSION.SPATIAL_DATA),
        (fiber_agents_data["spatialData"]["version"], CURRENT_VERSION.SPATIAL_DATA),
        (sphere_group_data["spatialData"]["version"], CURRENT_VERSION.SPATIAL_DATA),
    ],
)
def test_versions_spatial_data(spatial_version, expected_version):
    assert spatial_version == expected_version


# Each test trajectory has 3 frames
@pytest.mark.parametrize(
    "bundleSize, expected_bundleSize",
    [
        (default_agents_data["spatialData"]["bundleSize"], 3),
        (mixed_agents_data["spatialData"]["bundleSize"], 3),
        (fiber_agents_data["spatialData"]["bundleSize"], 3),
        (sphere_group_data["spatialData"]["bundleSize"], 3),
    ],
)
def test_bundle_size(bundleSize, expected_bundleSize):
    assert bundleSize == expected_bundleSize


# Each test trajectory starts at 0
@pytest.mark.parametrize(
    "bundleStart, expected_bundleStart",
    [
        (default_agents_data["spatialData"]["bundleStart"], 0),
        (mixed_agents_data["spatialData"]["bundleStart"], 0),
        (fiber_agents_data["spatialData"]["bundleStart"], 0),
        (sphere_group_data["spatialData"]["bundleStart"], 0),
    ],
)
def test_bundle_start(bundleStart, expected_bundleStart):
    assert bundleStart == expected_bundleStart


# Each test trajectory has msg type 1
@pytest.mark.parametrize(
    "msgType, expected_msgType",
    [
        (default_agents_data["spatialData"]["msgType"], 1),
        (mixed_agents_data["spatialData"]["msgType"], 1),
        (fiber_agents_data["spatialData"]["msgType"], 1),
        (sphere_group_data["spatialData"]["msgType"], 1),
    ],
)
def test_msg_type(msgType, expected_msgType):
    assert msgType == expected_msgType


@pytest.mark.parametrize(
    "data, expected_data",
    [
        (
            default_agents_data["spatialData"]["bundleData"][0],
            {
                "frameNumber": 0,
                "time": 0.0,
                "data": [
                    VIZ_TYPE.DEFAULT,  # agent 1
                    0.0,
                    0.0,
                    4.89610492,
                    -29.81564851,
                    40.77254057,
                    0.0,
                    0.0,
                    0.0,
                    8.38656327,
                    0.0,
                    VIZ_TYPE.DEFAULT,  # agent 2
                    1.0,
                    1.0,
                    43.43048197,
                    48.00424379,
                    -36.02881338,
                    0.0,
                    0.0,
                    0.0,
                    6.18568039,
                    0.0,
                    VIZ_TYPE.DEFAULT,  # agent 3
                    2.0,
                    0.0,
                    29.84924588,
                    -38.02769707,
                    2.46644825,
                    0.0,
                    0.0,
                    0.0,
                    6.61459206,
                    0.0,
                ],
            },
        ),
        (
            default_agents_data["spatialData"]["bundleData"][1],
            {
                "frameNumber": 1,
                "time": 0.5,
                "data": [
                    VIZ_TYPE.DEFAULT,
                    0.0,
                    1.0,
                    -43.37181102,
                    -13.41127423,
                    -17.31316927,
                    0.0,
                    0.0,
                    0.0,
                    5.26366739,
                    0.0,
                    VIZ_TYPE.DEFAULT,
                    1.0,
                    2.0,
                    9.62132397,
                    13.4774314,
                    -20.30846039,
                    0.0,
                    0.0,
                    0.0,
                    6.69209780,
                    0.0,
                    VIZ_TYPE.DEFAULT,
                    2.0,
                    3.0,
                    41.41039848,
                    -45.85543786,
                    49.06208485,
                    0.0,
                    0.0,
                    0.0,
                    9.88033853,
                    0.0,
                ],
            },
        ),
        (
            default_agents_data["spatialData"]["bundleData"][2],
            {
                "frameNumber": 2,
                "time": 1.0,
                "data": [
                    VIZ_TYPE.DEFAULT,
                    0.0,
                    4.0,
                    -24.91450698,
                    -44.79360525,
                    13.32273796,
                    0.0,
                    0.0,
                    0.0,
                    8.91022619,
                    0.0,
                    VIZ_TYPE.DEFAULT,
                    1.0,
                    5.0,
                    4.10861266,
                    43.86451151,
                    21.93697483,
                    0.0,
                    0.0,
                    0.0,
                    9.01379396,
                    0.0,
                    VIZ_TYPE.DEFAULT,
                    2.0,
                    6.0,
                    -7.16740679,
                    -13.06491594,
                    44.97026158,
                    0.0,
                    0.0,
                    0.0,
                    8.39880154,
                    0.0,
                ],
            },
        ),
    ],
)
def test_bundle_data_default_agents(data, expected_data):
    assert data == expected_data


@pytest.mark.parametrize(
    "data, expected_data",
    [
        (
            mixed_agents_data["spatialData"]["bundleData"][0],
            {
                "frameNumber": 0,
                "time": 0.0,
                "data": [
                    VIZ_TYPE.DEFAULT,
                    0.0,
                    0.0,
                    4.89610492,
                    -29.81564851,
                    40.77254057,
                    0.0,
                    0.0,
                    0.0,
                    8.38656327,
                    0.0,
                    VIZ_TYPE.FIBER,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    -243.14059805,
                    207.75566987,
                    -95.33921063,
                    -20.54663446,
                    475.97201603,
                    14.43506311,
                    -76.45581828,
                    -97.31170699,
                    -144.30184731,
                    VIZ_TYPE.FIBER,
                    2.0,
                    2.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    12.0,
                    108.28447939,
                    175.55049775,
                    -274.34792273,
                    13.44237701,
                    258.21483663,
                    -65.05452787,
                    224.55922362,
                    -455.56482869,
                    -351.23389958,
                    -286.95502659,
                    330.12683064,
                    183.79420473,
                    VIZ_TYPE.DEFAULT,
                    3.0,
                    3.0,
                    43.43048197,
                    48.00424379,
                    -36.02881338,
                    0.0,
                    0.0,
                    0.0,
                    6.18568039,
                    0.0,
                    VIZ_TYPE.FIBER,
                    4.0,
                    4.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    49.76236816,
                    -353.11708296,
                    226.84570983,
                    -234.5462914,
                    105.46507228,
                    17.16552317,
                ],
            },
        ),
        (
            mixed_agents_data["spatialData"]["bundleData"][1],
            {
                "frameNumber": 1,
                "time": 1.0,
                "data": [
                    VIZ_TYPE.FIBER,
                    0.0,
                    5.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    -442.27202981,
                    202.83568625,
                    -262.13407113,
                    -372.23130078,
                    217.21997368,
                    404.88561338,
                    171.37918011,
                    205.80515525,
                    -65.95336727,
                    VIZ_TYPE.DEFAULT,
                    1.0,
                    6.0,
                    -43.37181102,
                    -13.41127423,
                    -17.31316927,
                    0.0,
                    0.0,
                    0.0,
                    6.69209780,
                    0.0,
                    VIZ_TYPE.FIBER,
                    2.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    245.9111405,
                    372.15936027,
                    -261.94702214,
                    3.50037066,
                    441.92904046,
                    321.75701298,
                    146.23928574,
                    -315.3241668,
                    82.00405173,
                    VIZ_TYPE.FIBER,
                    3.0,
                    7.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    104.82606074,
                    -413.76671598,
                    366.66127719,
                    136.7228888,
                    -210.69313998,
                    -465.59967482,
                    VIZ_TYPE.DEFAULT,
                    4.0,
                    6.0,
                    9.62132397,
                    13.4774314,
                    -20.30846039,
                    0.0,
                    0.0,
                    0.0,
                    9.88033853,
                    0.0,
                ],
            },
        ),
        (
            mixed_agents_data["spatialData"]["bundleData"][2],
            {
                "frameNumber": 2,
                "time": 2.0,
                "data": [
                    VIZ_TYPE.DEFAULT,
                    0.0,
                    8.0,
                    -24.91450698,
                    -44.79360525,
                    13.32273796,
                    0.0,
                    0.0,
                    0.0,
                    8.91022619,
                    0.0,
                    VIZ_TYPE.DEFAULT,
                    1.0,
                    9.0,
                    4.10861266,
                    43.86451151,
                    21.93697483,
                    0.0,
                    0.0,
                    0.0,
                    9.01379396,
                    0.0,
                    VIZ_TYPE.FIBER,
                    2.0,
                    10.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    -148.70447678,
                    225.27562348,
                    -273.51318785,
                    -5.32043612,
                    -55.97783429,
                    413.32948686,
                    165.64239994,
                    322.63703294,
                    -2.2348818,
                    VIZ_TYPE.FIBER,
                    3.0,
                    10.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    -317.48515644,
                    -237.70246887,
                    238.69661676,
                    94.56942257,
                    346.13786088,
                    -7.93209392,
                    VIZ_TYPE.FIBER,
                    4.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    7.77508859,
                    260.16762947,
                    -171.02427873,
                    -20.46326319,
                    179.43194042,
                    485.07810635,
                ],
            },
        ),
    ],
)
def test_bundle_data_mixed_agents(data, expected_data):
    assert data == expected_data


@pytest.mark.parametrize(
    "data, expected_data",
    [
        (
            fiber_agents_data["spatialData"]["bundleData"][0],
            {
                "frameNumber": 0,
                "time": 0.0,
                "data": [
                    VIZ_TYPE.FIBER,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    -243.14059805,
                    207.75566987,
                    -95.33921063,
                    -20.54663446,
                    475.97201603,
                    14.43506311,
                    -76.45581828,
                    -97.31170699,
                    -144.30184731,
                    VIZ_TYPE.DEFAULT,
                    200.0,
                    0.0,
                    -243.14059805,
                    207.75566987,
                    -95.33921063,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    VIZ_TYPE.DEFAULT,
                    202.0,
                    0.0,
                    -76.45581828,
                    -97.31170699,
                    -144.30184731,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    VIZ_TYPE.FIBER,
                    2.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    12.0,
                    108.28447939,
                    175.55049775,
                    -274.34792273,
                    13.44237701,
                    258.21483663,
                    -65.05452787,
                    224.55922362,
                    -455.56482869,
                    -351.23389958,
                    -286.95502659,
                    330.12683064,
                    183.79420473,
                    VIZ_TYPE.DEFAULT,
                    300.0,
                    1.0,
                    108.28447939,
                    175.55049775,
                    -274.34792273,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    VIZ_TYPE.DEFAULT,
                    302.0,
                    1.0,
                    224.55922362,
                    -455.56482869,
                    -351.23389958,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    VIZ_TYPE.FIBER,
                    3.0,
                    2.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    49.76236816,
                    -353.11708296,
                    226.84570983,
                    -234.5462914,
                    105.46507228,
                    17.16552317,
                    VIZ_TYPE.DEFAULT,
                    400.0,
                    2.0,
                    49.76236816,
                    -353.11708296,
                    226.84570983,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                ],
            },
        ),
        (
            fiber_agents_data["spatialData"]["bundleData"][1],
            {
                "frameNumber": 1,
                "time": 1.00001,
                "data": [
                    VIZ_TYPE.FIBER,
                    1.0,
                    3.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    -442.27202981,
                    202.83568625,
                    -262.13407113,
                    -372.23130078,
                    217.21997368,
                    404.88561338,
                    171.37918011,
                    205.80515525,
                    -65.95336727,
                    VIZ_TYPE.DEFAULT,
                    200.0,
                    3.0,
                    -442.27202981,
                    202.83568625,
                    -262.13407113,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    VIZ_TYPE.DEFAULT,
                    202.0,
                    3.0,
                    171.37918011,
                    205.80515525,
                    -65.95336727,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    VIZ_TYPE.FIBER,
                    2.0,
                    4.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    245.9111405,
                    372.15936027,
                    -261.94702214,
                    3.50037066,
                    441.92904046,
                    321.75701298,
                    146.23928574,
                    -315.3241668,
                    82.00405173,
                    1000.0,
                    300.0,
                    4.0,
                    245.9111405,
                    372.15936027,
                    -261.94702214,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    VIZ_TYPE.DEFAULT,
                    302.0,
                    4.0,
                    146.23928574,
                    -315.3241668,
                    82.00405173,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    VIZ_TYPE.FIBER,
                    3.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    104.82606074,
                    -413.76671598,
                    366.66127719,
                    136.7228888,
                    -210.69313998,
                    -465.59967482,
                    VIZ_TYPE.DEFAULT,
                    400.0,
                    1.0,
                    104.82606074,
                    -413.76671598,
                    366.66127719,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                ],
            },
        ),
        (
            fiber_agents_data["spatialData"]["bundleData"][2],
            {
                "frameNumber": 2,
                "time": 2.00001,
                "data": [
                    VIZ_TYPE.FIBER,
                    1.0,
                    5.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    9.0,
                    -148.70447678,
                    225.27562348,
                    -273.51318785,
                    -5.32043612,
                    -55.97783429,
                    413.32948686,
                    165.64239994,
                    322.63703294,
                    -2.2348818,
                    VIZ_TYPE.DEFAULT,
                    200.0,
                    5.0,
                    -148.70447678,
                    225.27562348,
                    -273.51318785,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    VIZ_TYPE.DEFAULT,
                    202.0,
                    5.0,
                    165.64239994,
                    322.63703294,
                    -2.2348818,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    VIZ_TYPE.FIBER,
                    2.0,
                    5.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    -317.48515644,
                    -237.70246887,
                    238.69661676,
                    94.56942257,
                    346.13786088,
                    -7.93209392,
                    VIZ_TYPE.DEFAULT,
                    300.0,
                    5.0,
                    -317.48515644,
                    -237.70246887,
                    238.69661676,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                    VIZ_TYPE.FIBER,
                    3.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    6.0,
                    7.77508859,
                    260.16762947,
                    -171.02427873,
                    -20.46326319,
                    179.43194042,
                    485.07810635,
                    VIZ_TYPE.DEFAULT,
                    400.0,
                    1.0,
                    7.77508859,
                    260.16762947,
                    -171.02427873,
                    0.0,
                    0.0,
                    0.0,
                    0.5,
                    0.0,
                ],
            },
        ),
    ],
)
def test_bundle_data_fiber_agents(data, expected_data):
    assert data == expected_data


@pytest.mark.parametrize(
    "data, expected_data",
    [
        (
            sphere_group_data["spatialData"]["bundleData"][0],
            {
                "frameNumber": 0,
                "time": 0.0,
                "data": [
                    1000.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    12.0,
                    10.0,
                    12.0,
                    0.0,
                    2.0,
                    12.0,
                    9.0,
                    0.0,
                    1.0,
                    8.0,
                    9.0,
                    0.0,
                    1.0,
                    1000.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    12.0,
                    0.0,
                    10.0,
                    12.0,
                    1.0,
                    0.0,
                    12.0,
                    9.0,
                    2.0,
                    0.0,
                    8.0,
                    9.0,
                    2.0,
                ],
            },
        ),
        (
            sphere_group_data["spatialData"]["bundleData"][1],
            {
                "frameNumber": 1,
                "time": 0.5,
                "data": [
                    1000.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    12.0,
                    11.0,
                    13.0,
                    1.0,
                    2.0,
                    13.0,
                    10.0,
                    1.0,
                    1.0,
                    9.0,
                    10.0,
                    1.0,
                    1.0,
                    1000.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    12.0,
                    1.0,
                    10.0,
                    12.0,
                    1.0,
                    1.0,
                    12.0,
                    9.0,
                    2.0,
                    1.0,
                    8.0,
                    9.0,
                    2.0,
                ],
            },
        ),
        (
            sphere_group_data["spatialData"]["bundleData"][2],
            {
                "frameNumber": 2,
                "time": 1.0,
                "data": [
                    1000.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    12.0,
                    11.0,
                    13.0,
                    1.0,
                    2.0,
                    13.0,
                    10.0,
                    1.0,
                    1.0,
                    9.0,
                    10.0,
                    1.0,
                    1.0,
                    1000.0,
                    1.0,
                    1.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                    1.0,
                    12.0,
                    1.0,
                    10.0,
                    12.0,
                    1.0,
                    1.0,
                    12.0,
                    9.0,
                    2.0,
                    1.0,
                    8.0,
                    9.0,
                    2.0,
                ],
            },
        ),
    ],
)
def test_bundle_data_sphere_group(data, expected_data):
    assert data == expected_data


# test plot data
@pytest.mark.parametrize(
    "plot_version, expected_version",
    [
        (default_agents_data["plotData"]["version"], CURRENT_VERSION.PLOT_DATA),
        (mixed_agents_data["plotData"]["version"], CURRENT_VERSION.PLOT_DATA),
        (fiber_agents_data["plotData"]["version"], CURRENT_VERSION.PLOT_DATA),
        (sphere_group_data["plotData"]["version"], CURRENT_VERSION.PLOT_DATA),
    ],
)
def test_versions_plot_data(plot_version, expected_version):
    assert plot_version == expected_version


@pytest.mark.parametrize(
    "plot_data, expected_plot_data",
    [
        (default_agents_data["plotData"]["data"], []),
        (mixed_agents_data["plotData"]["data"], ["plot data goes here"]),
        (fiber_agents_data["plotData"]["data"], ["plot data goes here"]),
        (sphere_group_data["plotData"]["data"], ["plot data goes here"]),
    ],
)
def test_plot_data(plot_data, expected_plot_data):
    assert plot_data == expected_plot_data


def test_unique_ids_per_frame():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(default_agents_data)
    assert JsonWriter._check_agent_ids_are_unique_per_frame(mixed_agents_data)
    assert JsonWriter._check_agent_ids_are_unique_per_frame(fiber_agents_data)
    assert JsonWriter._check_agent_ids_are_unique_per_frame(sphere_group_data)


# Test invalid agent IDs errors
@pytest.mark.parametrize(
    "trajectory, expected_data",
    [
        pytest.param(
            mixed_agents_invalid_agent_id(),
            {},
            marks=pytest.mark.raises(exception=DataError),
        ),
    ],
)
def test_invalid_agent_id(trajectory, expected_data):
    converter = TrajectoryConverter(trajectory)
    buffer_data = JsonWriter.format_trajectory_data(converter._data)
    JsonWriter._validate_ids(converter._data)
    assert expected_data == buffer_data


data0 = DisplayData(name="Name 0", display_type=DISPLAY_TYPE.SPHERE)
data1 = DisplayData(name="Name 1", display_type=DISPLAY_TYPE.FIBER)
data2 = DisplayData(name="Name 2", display_type=DISPLAY_TYPE.OBJ)
key0 = "Red"
key1 = "Green"
key2 = "Blue"
display_dict = {key0: data0, key1: data1, key2: data2}


@pytest.mark.parametrize(
    "key, expected_data",
    [
        (
            key2.upper(),
            data2,
        ),
        (
            key0.lower(),
            data0,
        ),
        (
            key1,
            data1,
        ),
        (
            key0 + "x",
            None,
        ),
    ],
)
def test_get_display_data_for_agent(key, expected_data):
    assert expected_data == TrajectoryConverter._get_display_data_for_agent(
        key, display_dict
    )
