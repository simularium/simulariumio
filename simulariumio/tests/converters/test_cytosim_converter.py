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
range = 0.00808633 - -0.39575567
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
                -0.00971748666 * auto_scale_factor,  # x
                0.11021733333 * auto_scale_factor,  # y
                -0.39195633333 * auto_scale_factor,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                radius_0 * auto_scale_factor,  # radius
                9.0,  # subpoints
                0.00600819666 * auto_scale_factor,
                -0.00005333333 * auto_scale_factor,
                -0.00809566666 * auto_scale_factor,
                0.00001211666 * auto_scale_factor,
                -0.00003333333 * auto_scale_factor,
                0.00000933333 * auto_scale_factor,
                -0.00602031333 * auto_scale_factor,
                0.00008666666 * auto_scale_factor,
                0.00808633333 * auto_scale_factor,
                VIZ_TYPE.FIBER,  # agent 2
                2.0,
                0.0,
                0.03558805 * auto_scale_factor,
                -0.03574496666 * auto_scale_factor,
                -0.3509275 * auto_scale_factor,
                0.0,
                0.0,
                0.0,
                radius_0 * auto_scale_factor,
                18.0,
                0.00385195 * auto_scale_factor,
                -0.02469013333 * auto_scale_factor,
                0.0059335 * auto_scale_factor,
                0.00229435 * auto_scale_factor,
                -0.01481503333 * auto_scale_factor,
                0.0035665 * auto_scale_factor,
                0.00073145 * auto_scale_factor,
                -0.00493523333 * auto_scale_factor,
                0.0012235 * auto_scale_factor,
                -0.00081075 * auto_scale_factor,
                0.00494096666 * auto_scale_factor,
                -0.0011495 * auto_scale_factor,
                -0.00232305 * auto_scale_factor,
                0.01481006666 * auto_scale_factor,
                -0.0035695 * auto_scale_factor,
                -0.00374395 * auto_scale_factor,
                0.02468936666 * auto_scale_factor,
                -0.0060045 * auto_scale_factor,
            ],
        ),
        (
            results_display_data["spatialData"]["bundleData"][1],
            [
                VIZ_TYPE.FIBER,
                1.0,
                0.0,
                -0.01528570666 * auto_scale_factor,
                0.12739133333 * auto_scale_factor,
                -0.39475566666 * auto_scale_factor,
                0.0,
                0.0,
                0.0,
                radius_0 * auto_scale_factor,
                9.0,
                0.00958788666 * auto_scale_factor,
                0.00257966666 * auto_scale_factor,
                0.00174766666 * auto_scale_factor,
                -0.00000499333 * auto_scale_factor,
                0.00004566666 * auto_scale_factor,
                -0.00004033333 * auto_scale_factor,
                -0.00958289333 * auto_scale_factor,
                -0.00262533333 * auto_scale_factor,
                -0.00170733333 * auto_scale_factor,
                VIZ_TYPE.FIBER,
                2.0,
                0.0,
                0.04326836666 * auto_scale_factor,
                -0.03629301666 * auto_scale_factor,
                -0.3474615 * auto_scale_factor,
                0.0,
                0.0,
                0.0,
                radius_0 * auto_scale_factor,
                18.0,
                -0.02417086666 * auto_scale_factor,
                -0.00833518333 * auto_scale_factor,
                0.0024295 * auto_scale_factor,
                -0.01452346666 * auto_scale_factor,
                -0.00492438333 * auto_scale_factor,
                0.0015135 * auto_scale_factor,
                -0.00485906666 * auto_scale_factor,
                -0.00156918333 * auto_scale_factor,
                0.0005705 * auto_scale_factor,
                0.00481903333 * auto_scale_factor,
                0.00172381666 * auto_scale_factor,
                -0.0004475 * auto_scale_factor,
                0.01451413333 * auto_scale_factor,
                0.00495721666 * auto_scale_factor,
                -0.0014945 * auto_scale_factor,
                0.02422023333 * auto_scale_factor,
                0.00814771666 * auto_scale_factor,
                -0.0025715 * auto_scale_factor,
            ],
        ),
    ],
)
def test_bundleData(bundleData, expected_bundleData):
    assert np.isclose(expected_bundleData, bundleData["data"]).all()


def test_agent_ids():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)


scale_factor_aster = 10
# test data extraction from aster_pull3D example
aster_pull3D_objects = CytosimData(
    meta_data=MetaData(
        scale_factor=scale_factor_aster
    ),
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


converter_aster = CytosimConverter(aster_pull3D_objects)
results_aster = JsonWriter.format_trajectory_data(converter_aster._data)


@pytest.mark.parametrize(
    "asterData, expected_asterData",
    [
        (
            results_aster["spatialData"]["bundleData"][0]["data"][0:49],
            [
                VIZ_TYPE.FIBER,  # agent 1
                1.0,  # id
                0.0,  # type
                0.24166 * scale_factor_aster,
                0.50934 * scale_factor_aster,
                0.22896 * scale_factor_aster,
                0.0,
                0.0,
                0.0,
                1.0 * scale_factor_aster,
                15.0,
                0.12764 * scale_factor_aster,
                -0.14133999999999997 * scale_factor_aster,
                -0.061160000000000006 * scale_factor_aster,
                0.06384 * scale_factor_aster,
                -0.07064000000000001 * scale_factor_aster,
                -0.03056000000000001 * scale_factor_aster,
                4.000000000000669e-05 * scale_factor_aster,
                -4.000000000000114e-05 * scale_factor_aster,
                4.0000000000005316e-05 * scale_factor_aster,
                -0.06385999999999999 * scale_factor_aster,
                0.07065999999999997 * scale_factor_aster,
                0.030540000000000005 * scale_factor_aster,
                -0.12766000000000002 * scale_factor_aster,
                0.14135999999999999 * scale_factor_aster,
                0.061140000000000014 * scale_factor_aster,
                VIZ_TYPE.FIBER,  # agent 2
                2.0,
                0.0,
                0.3733 * scale_factor_aster,
                0.2226 * scale_factor_aster,
                0.2044 * scale_factor_aster,
                0.0,
                0.0,
                0.0,
                1.0 * scale_factor_aster,
                12.0,
                -0.00399999999999999 * scale_factor_aster,
                0.1454 * scale_factor_aster,
                -0.036599999999999994 * scale_factor_aster,
                -0.0013000000000000095 * scale_factor_aster,
                0.048499999999999995 * scale_factor_aster,
                -0.012199999999999989 * scale_factor_aster,
                0.0012999999999999817 * scale_factor_aster,
                -0.04850000000000001 * scale_factor_aster,
                0.012199999999999989 * scale_factor_aster,
                0.004000000000000017 * scale_factor_aster,
                -0.1454 * scale_factor_aster,
                0.036599999999999994 * scale_factor_aster,
            ],
        ),
        (
            results_aster["spatialData"]["bundleData"][1]["data"][0:49],
            [
                VIZ_TYPE.FIBER,
                1.0,
                0.0,
                0.26803333333333335 * scale_factor_aster,
                0.48285 * scale_factor_aster,
                0.010500000000000002 * scale_factor_aster,
                0.0,
                0.0,
                0.0,
                1.0 * scale_factor_aster,
                18.0,
                0.17746666666666666 * scale_factor_aster,
                -0.14315 * scale_factor_aster,
                0.0781 * scale_factor_aster,
                0.09826666666666667 * scale_factor_aster,
                -0.10015000000000002 * scale_factor_aster,
                0.034600000000000006 * scale_factor_aster,
                0.02156666666666669 * scale_factor_aster,
                -0.05004999999999998 * scale_factor_aster,
                -0.005500000000000001 * scale_factor_aster,
                -0.04973333333333333 * scale_factor_aster,
                0.013249999999999984 * scale_factor_aster,
                -0.035699999999999996 * scale_factor_aster,
                -0.10803333333333334 * scale_factor_aster,
                0.09375 * scale_factor_aster,
                -0.046299999999999994 * scale_factor_aster,
                -0.13953333333333334 * scale_factor_aster,
                0.18635000000000002 * scale_factor_aster,
                -0.0252 * scale_factor_aster,
                VIZ_TYPE.FIBER,
                2.0,
                0.0,
                0.4225666666666667 * scale_factor_aster,
                0.23976666666666668 * scale_factor_aster,
                0.07003333333333334 * scale_factor_aster,
                0.0,
                0.0,
                0.0,
                1.0 * scale_factor_aster,
                9.0,
                0.019733333333333342 * scale_factor_aster,
                0.09583333333333334 * scale_factor_aster,
                0.02036666666666666 * scale_factor_aster,
                -0.0023666666666666636 * scale_factor_aster,
                0.0006333333333333236 * scale_factor_aster,
                -0.0008333333333333328 * scale_factor_aster,
                -0.01736666666666668 * scale_factor_aster,
                -0.09646666666666666 * scale_factor_aster,
                -0.01953333333333333 * scale_factor_aster,
            ],
        ),
    ],
)
def test_aster_data(asterData, expected_asterData):
    assert np.isclose(expected_asterData, asterData).all()


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
