#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pytest
from unittest.mock import Mock

from simulariumio.physicell import PhysicellConverter, PhysicellData
from simulariumio import MetaData, DisplayData, JsonWriter, UnitData
from simulariumio.constants import (
    DEFAULT_BOX_SIZE,
    DEFAULT_COLORS,
    DISPLAY_TYPE,
    VIEWER_DIMENSION_RANGE,
    VIZ_TYPE,
)
from simulariumio.exceptions import InputDataError

data = PhysicellData(
    timestep=360.0,
    path_to_output_dir="simulariumio/tests/data/physicell/default_output/",
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
range = 866.8254210959085
# value of automatically generated scale factor, so that position
# data fits within VIEWER_DIMENSION_RANGE
auto_scale_factor = VIEWER_DIMENSION_RANGE.MAX / range
time_unit = "ms"
data_with_meta_data = PhysicellData(
    meta_data=MetaData(
        box_size=np.array([size_x, size_y, size_z]),
    ),
    timestep=360.0,
    path_to_output_dir="simulariumio/tests/data/physicell/default_output/",
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
                "x": size_x * auto_scale_factor,
                "y": size_y * auto_scale_factor,
                "z": size_z * auto_scale_factor,
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
    ),
    timestep=360.0,
    path_to_output_dir="simulariumio/tests/data/physicell/default_output/",
    display_data={
        0: DisplayData(
            name=test_name,
            display_type=DISPLAY_TYPE.SPHERE,
            radius=test_radius,
            color=test_color,
        ),
    },
    phase_names={1: {4: test_phase}},
)
converter_display_data = PhysicellConverter(data_with_display_data)
results_display_data = JsonWriter.format_trajectory_data(converter_display_data._data)
scale_factor_display_data = VIEWER_DIMENSION_RANGE.MAX / (888.4127105479544)


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


# sphere groups for owner cells and subcells
substrate_name = "Substrate"
substrate_color = "#d0c5c8"
owner_cell_name = "Stem cell"
scale_factor = 0.01
data_subcells = PhysicellData(
    meta_data=MetaData(
        box_size=np.array([960.0, 640.0, 300.0]),
        scale_factor=scale_factor,
    ),
    timestep=36.0,
    path_to_output_dir="simulariumio/tests/data/physicell/subcell_output/",
    display_data={
        0: DisplayData(
            name=substrate_name,
            display_type=DISPLAY_TYPE.SPHERE,
            color=substrate_color,
        ),
    },
    phase_names={0: {18: "fixed"}},
    max_owner_cells=10000,
    owner_cell_display_name=owner_cell_name,
    time_units=UnitData("min"),
)
converter_subcells = PhysicellConverter(data_subcells)
results_subcells = JsonWriter.format_trajectory_data(converter_subcells._data)


# test type mapping provided
@pytest.mark.parametrize(
    "typeMapping, expected_typeMapping",
    [
        (
            results_subcells["trajectoryInfo"]["typeMapping"],
            {
                "0": {
                    "name": f"{substrate_name}#fixed",
                    "geometry": {
                        "displayType": "SPHERE",
                        "color": substrate_color,
                    },
                },
                "1": {
                    "name": f"{owner_cell_name}#8",
                    "geometry": {
                        "displayType": "SPHERE_GROUP",
                        "color": DEFAULT_COLORS[0],
                    },
                },
                "2": {
                    "name": f"{owner_cell_name}#14",
                    "geometry": {
                        "displayType": "SPHERE_GROUP",
                        "color": DEFAULT_COLORS[1],
                    },
                },
                "3": {
                    "name": f"{owner_cell_name}#25",
                    "geometry": {
                        "displayType": "SPHERE_GROUP",
                        "color": DEFAULT_COLORS[2],
                    },
                },
                "4": {
                    "name": f"{owner_cell_name}#2",
                    "geometry": {
                        "displayType": "SPHERE_GROUP",
                        "color": DEFAULT_COLORS[3],
                    },
                },
            },
        )
    ],
)
def test_typeMapping_subcells(typeMapping, expected_typeMapping):
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
                -427.0 * scale_factor_display_data,  # x
                -251.0 * scale_factor_display_data,  # y
                0.0,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                8.412710547954229 * scale_factor_display_data,
                0.0,
                VIZ_TYPE.DEFAULT,
                1.0,
                1.0,
                -228.0 * scale_factor_display_data,
                430.0 * scale_factor_display_data,
                0.0,
                0.0,
                0.0,
                0.0,
                test_radius * scale_factor_display_data,
                0.0,
                VIZ_TYPE.DEFAULT,
                2.0,
                1.0,
                423.0 * scale_factor_display_data,
                378.0 * scale_factor_display_data,
                0.0,
                0.0,
                0.0,
                0.0,
                test_radius * scale_factor_display_data,
                0.0,
            ],
        ),
        (
            results_subcells["spatialData"]["bundleData"][0],
            [
                VIZ_TYPE.DEFAULT,  # first agent
                35.0,  # id
                0.0,  # type
                439.83198 * scale_factor,  # x
                277.33248 * scale_factor,  # y
                16.1 * scale_factor,  # z
                0.0,  # x rotation
                0.0,  # y rotation
                0.0,  # z rotation
                18.837494593627718 * scale_factor,  # radius
                0.0,  # number of subpoints
                VIZ_TYPE.DEFAULT,  # second agent
                36.0,
                0.0,
                470.16522 * scale_factor,
                277.33248 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                37.0,
                0.0,
                500.49846 * scale_factor,
                277.33248 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                38.0,
                0.0,
                530.8317 * scale_factor,
                277.33247999999997 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                39.0,
                0.0,
                424.66536 * scale_factor,
                304.41573 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                40.0,
                0.0,
                454.9986 * scale_factor,
                304.41573 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                41.0,
                0.0,
                485.33184 * scale_factor,
                304.41573 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                42.0,
                0.0,
                515.66508 * scale_factor,
                304.41573 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                43.0,
                0.0,
                439.83198 * scale_factor,
                330.41565 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                44.0,
                0.0,
                470.16522 * scale_factor,
                330.41565 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                45.0,
                0.0,
                500.49846 * scale_factor,
                330.41565 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                46.0,
                0.0,
                530.8317 * scale_factor,
                330.41565 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                47.0,
                0.0,
                424.66536 * scale_factor,
                356.41557 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                48.0,
                0.0,
                454.9986 * scale_factor,
                356.41557 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                49.0,
                0.0,
                485.33184 * scale_factor,
                356.41557 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                50.0,
                0.0,
                515.66508 * scale_factor,
                356.41557 * scale_factor,
                16.1 * scale_factor,
                0.0,
                0.0,
                0.0,
                18.837494593627718 * scale_factor,
                0.0,
                VIZ_TYPE.DEFAULT,
                10008.0,
                1.0,
                475.6803545454546 * scale_factor,
                275.0673354545455 * scale_factor,
                51.69090909090909 * scale_factor,
                0.0,
                0.0,
                0.0,
                1.0,
                44.0,
                -51.0149945454546 * scale_factor,
                -12.90147545454552 * scale_factor,
                -9.490909090909089 * scale_factor,
                18.69798113091103 * scale_factor,
                -20.681754545454556 * scale_factor,
                -12.90147545454552 * scale_factor,
                -9.490909090909089 * scale_factor,
                18.69798113091103 * scale_factor,
                9.651485454545394 * scale_factor,
                -12.90147545454552 * scale_factor,
                -9.490909090909089 * scale_factor,
                18.69798113091103 * scale_factor,
                39.984725454545433 * scale_factor,
                -12.90147545454552 * scale_factor,
                -9.490909090909089 * scale_factor,
                18.69798113091103 * scale_factor,
                -35.848374545454575 * scale_factor,
                14.181774545454484 * scale_factor,
                -9.490909090909089 * scale_factor,
                18.69798113091103 * scale_factor,
                -5.5151345454545364 * scale_factor,
                14.181774545454484 * scale_factor,
                -9.490909090909089 * scale_factor,
                18.69798113091103 * scale_factor,
                24.818105454545414 * scale_factor,
                14.181774545454484 * scale_factor,
                -9.490909090909089 * scale_factor,
                18.69798113091103 * scale_factor,
                -35.848374545454575 * scale_factor,
                2.265144545454456 * scale_factor,
                16.609090909090907 * scale_factor,
                18.69798113091103 * scale_factor,
                -5.5151345454545364 * scale_factor,
                2.265144545454456 * scale_factor,
                16.609090909090907 * scale_factor,
                18.69798113091103 * scale_factor,
                24.818105454545414 * scale_factor,
                2.265144545454456 * scale_factor,
                16.609090909090907 * scale_factor,
                18.69798113091103 * scale_factor,
                55.15134545454545 * scale_factor,
                2.265144545454456 * scale_factor,
                16.609090909090907 * scale_factor,
                18.69798113091103 * scale_factor,
                VIZ_TYPE.DEFAULT,
                10014.0,
                2.0,
                477.4188208695653 * scale_factor,
                337.19823782608698 * scale_factor,
                54.68260869565217 * scale_factor,
                0.0,
                0.0,
                0.0,
                1.0,
                92.0,
                -52.75346086956532 * scale_factor,
                -21.949207826086958 * scale_factor,
                -12.48260869565217 * scale_factor,
                18.69798113091103 * scale_factor,
                -22.420220869565277 * scale_factor,
                -21.949207826086958 * scale_factor,
                -12.48260869565217 * scale_factor,
                18.69798113091103 * scale_factor,
                7.913019130434673 * scale_factor,
                -21.949207826086958 * scale_factor,
                -12.48260869565217 * scale_factor,
                18.69798113091103 * scale_factor,
                38.24625913043471 * scale_factor,
                -21.949207826086958 * scale_factor,
                -12.48260869565217 * scale_factor,
                18.69798113091103 * scale_factor,
                -37.586840869565297 * scale_factor,
                4.0507121739130625 * scale_factor,
                -12.48260869565217 * scale_factor,
                18.69798113091103 * scale_factor,
                -7.253600869565258 * scale_factor,
                4.0507121739130625 * scale_factor,
                -12.48260869565217 * scale_factor,
                18.69798113091103 * scale_factor,
                23.079639130434693 * scale_factor,
                4.0507121739130625 * scale_factor,
                -12.48260869565217 * scale_factor,
                18.69798113091103 * scale_factor,
                53.41287913043473 * scale_factor,
                4.0507121739130625 * scale_factor,
                -12.48260869565217 * scale_factor,
                18.69798113091103 * scale_factor,
                -52.75346086956532 * scale_factor,
                30.05063217391304 * scale_factor,
                -12.48260869565217 * scale_factor,
                18.69798113091103 * scale_factor,
                -22.420220869565277 * scale_factor,
                30.05063217391304 * scale_factor,
                -12.48260869565217 * scale_factor,
                18.69798113091103 * scale_factor,
                7.913019130434673 * scale_factor,
                30.05063217391304 * scale_factor,
                -12.48260869565217 * scale_factor,
                18.69798113091103 * scale_factor,
                38.24625913043471 * scale_factor,
                30.05063217391304 * scale_factor,
                -12.48260869565217 * scale_factor,
                18.69798113091103 * scale_factor,
                -22.420220869565277 * scale_factor,
                -32.78250782608696 * scale_factor,
                13.617391304347826 * scale_factor,
                18.69798113091103 * scale_factor,
                7.913019130434673 * scale_factor,
                -32.78250782608696 * scale_factor,
                13.617391304347826 * scale_factor,
                18.69798113091103 * scale_factor,
                38.24625913043471 * scale_factor,
                -32.78250782608696 * scale_factor,
                13.617391304347826 * scale_factor,
                18.69798113091103 * scale_factor,
                -37.586840869565297 * scale_factor,
                -6.782587826086983 * scale_factor,
                13.617391304347826 * scale_factor,
                18.69798113091103 * scale_factor,
                -7.253600869565258 * scale_factor,
                -6.782587826086983 * scale_factor,
                13.617391304347826 * scale_factor,
                18.69798113091103 * scale_factor,
                23.079639130434693 * scale_factor,
                -6.782587826086983 * scale_factor,
                13.617391304347826 * scale_factor,
                18.69798113091103 * scale_factor,
                53.41287913043473 * scale_factor,
                -6.782587826086983 * scale_factor,
                13.617391304347826 * scale_factor,
                18.69798113091103 * scale_factor,
                -52.75346086956532 * scale_factor,
                19.217332173913038 * scale_factor,
                13.617391304347826 * scale_factor,
                18.69798113091103 * scale_factor,
                -22.420220869565277 * scale_factor,
                19.217332173913038 * scale_factor,
                13.617391304347826 * scale_factor,
                18.69798113091103 * scale_factor,
                7.913019130434673 * scale_factor,
                19.217332173913038 * scale_factor,
                13.617391304347826 * scale_factor,
                18.69798113091103 * scale_factor,
                38.24625913043471 * scale_factor,
                19.217332173913038 * scale_factor,
                13.617391304347826 * scale_factor,
                18.69798113091103 * scale_factor,
                VIZ_TYPE.DEFAULT,
                10025.0,
                3.0,
                424.66536 * scale_factor,
                304.41573 * scale_factor,
                68.3 * scale_factor,
                0.0,
                0.0,
                0.0,
                1.0,
                4.0,
                0.0,
                0.0,
                0.0,
                18.69798113091103 * scale_factor,
                VIZ_TYPE.DEFAULT,
                10002.0,
                4.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                1.0,
                4.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ],
        ),
    ],
)
def test_bundleData(bundleData, expected_bundleData):
    assert False not in np.isclose(
        np.array(expected_bundleData),
        np.array(bundleData["data"]),
    )


def test_agent_ids():
    assert JsonWriter._check_agent_ids_are_unique_per_frame(results_display_data)


# path_to_output_dir is incorrect
@pytest.mark.parametrize(
    "trajectory, expected_data",
    [
        pytest.param(
            {
                "meta_data": MetaData(
                    box_size=np.array([1000.0, 1000.0, 100.0]),
                ),
                "timestep": 360.0,
                "path_to_output_dir": "../simulariumio/tests/data/physicell/",
            },
            {},
            marks=pytest.mark.raises(exception=InputDataError),
        ),
    ],
)
def test_bad_path_to_output_dir(trajectory, expected_data):
    converter = PhysicellConverter(trajectory)
    buffer_data = JsonWriter.format_trajectory_data(converter._data)
    assert expected_data == buffer_data


def test_input_file_error():
    # path to a file, not a directory
    invalid_data_0 = PhysicellData(
        timestep=360.0,
        path_to_output_dir=(
            "simulariumio/tests/data/physicell/default_output/output00000000.xml",
        ),
    )
    with pytest.raises(InputDataError):
        PhysicellConverter(invalid_data_0)

    # path to directory with no output files
    invalid_data_1 = PhysicellData(
        timestep=360.0,
        path_to_output_dir="simulariumio/tests/data/physicell/",
    )
    with pytest.raises(InputDataError):
        PhysicellConverter(invalid_data_1)


def test_callback_fn():
    callback_fn_0 = Mock()
    call_interval = 0.000000001
    PhysicellConverter(data, callback_fn_0, call_interval)
    assert callback_fn_0.call_count > 1

    # calls to the callback function should be strictly increasing
    # and the value should never exceed 1.0 (100%)
    call_list = callback_fn_0.call_args_list
    last_call_val = -1.0
    for call in call_list:
        call_value = call.args[0]
        assert call_value > last_call_val
        assert call_value <= 1.0 and call_value >= 0.0
        last_call_val = call_value
