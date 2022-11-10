#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np

from simulariumio import JsonWriter
from simulariumio.cytosim import (
    CytosimConverter,
    CytosimData,
    CytosimObjectInfo,
)
from simulariumio import MetaData, DisplayData, InputFileData
from simulariumio.constants import (
    DISPLAY_TYPE,
    DEFAULT_BOX_SIZE,
    VIZ_TYPE,
)

data = CytosimData(
    object_info={
        "fibers": CytosimObjectInfo(
            cytosim_file=InputFileData(
                file_path=(
                    "simulariumio/tests/data/cytosim/3_fibers_3_frames/test.txt"
                ),
            ),
        )
    },
)
converter = CytosimConverter(data)
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
                    "name": "fiber0",
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


# xyz dimensions represented as array
box_x = 0.5
box_y = 0.3
box_z = 0.4
scale_factor = 1000
data_with_metadata = CytosimData(
    meta_data=MetaData(
        box_size=np.array([box_x, box_y, box_z]),
        scale_factor=scale_factor,
    ),
    object_info={
        "fibers": CytosimObjectInfo(
            cytosim_file=InputFileData(
                file_path=(
                    "simulariumio/tests/data/cytosim/3_fibers_3_frames/test.txt"
                ),
            ),
        )
    },
)
converter_meta_data = CytosimConverter(data_with_metadata)
results_meta_data = JsonWriter.format_trajectory_data(converter_meta_data._data)


# test box data provided
@pytest.mark.parametrize(
    "box_size, expected_box_size",
    [
        (
            results_meta_data["trajectoryInfo"]["size"],
            {
                "x": box_x * scale_factor,
                "y": box_y * scale_factor,
                "z": box_z * scale_factor,
            },
        )
    ],
)
def test_box_size_provided(box_size, expected_box_size):
    assert box_size == expected_box_size


name_0 = "fiber"
radius_0 = 0.001
color_0 = "#d71f5f"
data_with_display_data = CytosimData(
    meta_data=MetaData(
        box_size=np.array([box_x, box_y, box_z]),
        scale_factor=scale_factor,
    ),
    object_info={
        "fibers": CytosimObjectInfo(
            cytosim_file=InputFileData(
                file_path=(
                    "simulariumio/tests/data/cytosim/3_fibers_3_frames/test.txt"
                ),
            ),
            display_data={
                0: DisplayData(
                    name=name_0,
                    radius=radius_0,
                    display_type=DISPLAY_TYPE.FIBER,
                    color=color_0,
                )
            },
        )
    },
)
converter_display_data = CytosimConverter(data_with_display_data)
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
                        "displayType": "FIBER",
                        "color": color_0,
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
                VIZ_TYPE.FIBER,  # agent 1
                1.0,  # id
                0.0,  # type
                0.0,  # x
                0.0,  # y
                0.0,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                radius_0 * scale_factor,  # radius
                9.0,  # subpoints
                -3.70929,
                110.164,
                -400.052,
                -009.70537,
                110.184,
                -391.947,
                -15.7378,
                110.304,
                -383.87,
                VIZ_TYPE.FIBER,  # agent 2
                2.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                radius_0 * scale_factor,
                18.0,
                39.440000000000005,
                -60.4351,
                -344.994,
                37.8824,
                -50.56,
                -347.361,
                36.3195,
                -40.6802,
                -349.704,
                34.7773,
                -30.804000000000002,
                -352.077,
                33.265,
                -20.9349,
                -354.497,
                31.8441,
                -11.0556,
                -356.932,
            ],
        ),
        (
            results_display_data["spatialData"]["bundleData"][1],
            [
                VIZ_TYPE.FIBER,
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                radius_0 * scale_factor,
                9.0,
                -5.69782,
                129.971,
                -393.00800000000004,
                -15.290700000000001,
                127.437,
                -394.796,
                -24.8686,
                124.766,
                -396.463,
                VIZ_TYPE.FIBER,
                2.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                radius_0 * scale_factor,
                18.0,
                19.0975,
                -44.6282,
                -345.032,
                028.7449,
                -41.2174,
                -345.948,
                38.4093,
                -37.8622,
                -346.891,
                48.0874,
                -34.5692,
                -347.90900000000005,
                57.7825,
                -31.335799999999995,
                -348.95599999999996,
                67.48859999999999,
                -28.145300000000002,
                -350.03299999999996,
            ],
        ),
    ],
)
def test_bundleData(bundleData, expected_bundleData):
    assert expected_bundleData == bundleData["data"]


def test_agent_ids():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)


# test data extraction from aster_pull3D example
aster_pull3D_objects = CytosimData(
    object_info={
        "fibers": CytosimObjectInfo(
            cytosim_file=InputFileData(
                file_path=(
                    "simulariumio/tests/data/cytosim/aster_pull3D"
                    "_couples_actin_solid_3_frames/fiber_points.txt"
                ),
            ),
        ),
        "solids": CytosimObjectInfo(
            cytosim_file=InputFileData(
                file_path=(
                    "simulariumio/tests/data/cytosim/"
                    "aster_pull3D_couples_actin_solid_3_frames/solids.txt"
                ),
            ),
        ),
        "singles": CytosimObjectInfo(
            cytosim_file=InputFileData(
                file_path=(
                    "simulariumio/tests/data/cytosim/"
                    "aster_pull3D_couples_actin_solid_3_frames/singles.txt"
                ),
            ),
        ),
        "couples": CytosimObjectInfo(
            cytosim_file=InputFileData(
                file_path=(
                    "simulariumio/tests/data/cytosim/"
                    "aster_pull3D_couples_actin_solid_3_frames/couples.txt"
                ),
            ),
        ),
    },
)
# load the data from Cytosim output .txt files
cytosim_data = {}
for object_type in aster_pull3D_objects.object_info:
    cytosim_data[object_type] = (
        aster_pull3D_objects.object_info[object_type]
        .cytosim_file.get_contents()
        .split("\n")
    )


def test_parse_dimensions():
    dimension_data = CytosimConverter._parse_dimensions(cytosim_data)
    assert dimension_data.total_steps == 3
    assert dimension_data.max_agents == 19
    assert dimension_data.max_subpoints == 18
