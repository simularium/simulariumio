#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np
from unittest.mock import Mock

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
    VIEWER_DIMENSION_RANGE,
)
from simulariumio.exceptions import InputDataError

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


# value of automatically generated scale factor, so that position
# data fits within VIEWER_DIMENSION_RANGE
range = 0.400052 - -0.001
auto_scale_factor = VIEWER_DIMENSION_RANGE.MIN / range
name_0 = "fiber"
radius_0 = 0.001
color_0 = "#d71f5f"
data_with_display_data = CytosimData(
    meta_data=MetaData(
        box_size=np.array([box_x, box_y, box_z]),
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
                radius_0 * auto_scale_factor,  # radius
                9.0,  # subpoints
                -0.00370929 * auto_scale_factor,
                0.110164 * auto_scale_factor,
                -0.400052 * auto_scale_factor,
                -0.00970537 * auto_scale_factor,
                0.110184 * auto_scale_factor,
                -0.391947 * auto_scale_factor,
                -0.0157378 * auto_scale_factor,
                0.110304 * auto_scale_factor,
                -0.38387 * auto_scale_factor,
                VIZ_TYPE.FIBER,  # agent 2
                2.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                radius_0 * auto_scale_factor,
                18.0,
                0.03944 * auto_scale_factor,
                -0.0604351 * auto_scale_factor,
                -0.344994 * auto_scale_factor,
                0.0378824 * auto_scale_factor,
                -0.05056 * auto_scale_factor,
                -0.347361 * auto_scale_factor,
                0.0363195 * auto_scale_factor,
                -0.0406802 * auto_scale_factor,
                -0.349704 * auto_scale_factor,
                0.0347773 * auto_scale_factor,
                -0.030804 * auto_scale_factor,
                -0.352077 * auto_scale_factor,
                0.033265 * auto_scale_factor,
                -0.0209349 * auto_scale_factor,
                -0.354497 * auto_scale_factor,
                0.0318441 * auto_scale_factor,
                -0.0110556 * auto_scale_factor,
                -0.356932 * auto_scale_factor,
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
                radius_0 * auto_scale_factor,
                9.0,
                -0.00569782 * auto_scale_factor,
                0.129971 * auto_scale_factor,
                -0.393008 * auto_scale_factor,
                -0.0152907 * auto_scale_factor,
                0.127437 * auto_scale_factor,
                -0.394796 * auto_scale_factor,
                -0.0248686 * auto_scale_factor,
                0.124766 * auto_scale_factor,
                -0.396463 * auto_scale_factor,
                VIZ_TYPE.FIBER,
                2.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                radius_0 * auto_scale_factor,
                18.0,
                0.0190975 * auto_scale_factor,
                -0.0446282 * auto_scale_factor,
                -0.345032 * auto_scale_factor,
                0.0287449 * auto_scale_factor,
                -0.0412174 * auto_scale_factor,
                -0.345948 * auto_scale_factor,
                0.0384093 * auto_scale_factor,
                -0.0378622 * auto_scale_factor,
                -0.346891 * auto_scale_factor,
                0.0480874 * auto_scale_factor,
                -0.0345692 * auto_scale_factor,
                -0.347909 * auto_scale_factor,
                0.0577825 * auto_scale_factor,
                -0.0313358 * auto_scale_factor,
                -0.348956 * auto_scale_factor,
                0.0674886 * auto_scale_factor,
                -0.0281453 * auto_scale_factor,
                -0.350033 * auto_scale_factor,
            ],
        ),
    ],
)
def test_bundleData(bundleData, expected_bundleData):
    assert np.isclose(expected_bundleData, bundleData["data"]).all()


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


def test_input_file_error():
    # throws an error when the file is the right type, but is malformed
    malformed_data = CytosimData(
        object_info={
            "fibers": CytosimObjectInfo(
                cytosim_file=InputFileData(
                    file_path=(
                        "simulariumio/tests/data/malformed_data/malformed_cytosim.txt"
                    ),
                ),
            )
        },
    )
    with pytest.raises(InputDataError):
        CytosimConverter(malformed_data)

    # throws an error for a file type it can't read
    wrong_file = CytosimData(
        object_info={
            "fibers": CytosimObjectInfo(
                cytosim_file=InputFileData(
                    file_path=(
                        "simulariumio/tests/data/physicell/"
                        "default_output/initial_cells.mat"
                    ),
                ),
            )
        },
    )
    with pytest.raises(InputDataError):
        CytosimConverter(wrong_file)


def test_callback_fn():
    callback_fn_0 = Mock()
    call_interval = 0.000000001
    CytosimConverter(aster_pull3D_objects, callback_fn_0, call_interval)
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
