#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import pytest

from simulariumio.physicell import PhysicellConverter, PhysicellData
from simulariumio import MetaData, DisplayData, JsonWriter, UnitData
from simulariumio.constants import (
    DEFAULT_BOX_SIZE,
    DEFAULT_COLORS,
    DISPLAY_TYPE,
    VIZ_TYPE
)

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
scale_factor = 0.01
time_unit = "ms"
data_with_meta_data = PhysicellData(
    meta_data=MetaData(
        box_size=np.array([size_x, size_y, size_z]),
        scale_factor=scale_factor,
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
        ),
        (
            results_subcells["spatialData"]["bundleData"][0],
            [
                VIZ_TYPE.DEFAULT,  # first agent
                35,  # id
                0,  # type
                4.3983198,  # x
                2.7733247999999997,  # y
                0.16099999999999998,  # z
                0,  # x rotation
                0,  # y rotation
                0,  # z rotation
                0.18837494593627718,  # radius
                0,  # number of subpoints
                VIZ_TYPE.DEFAULT,  # second agent
                36,
                0,
                4.701652200000001,
                2.7733247999999997,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                37,
                0,
                5.0049846,
                2.7733247999999997,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                38,
                0,
                5.308317000000001,
                2.7733247999999997,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                39,
                0,
                4.2466536,
                3.0441573,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                40,
                0,
                4.5499860000000005,
                3.0441573,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                41,
                0,
                4.8533184,
                3.0441573,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                42,
                0,
                5.1566508,
                3.0441573,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                43,
                0,
                4.3983198,
                3.3041565,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                44,
                0,
                4.701652200000001,
                3.3041565,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                45,
                0,
                5.0049846,
                3.3041565,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                46,
                0,
                5.308317000000001,
                3.3041565,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                47,
                0,
                4.2466536,
                3.5641557,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                48,
                0,
                4.5499860000000005,
                3.5641557,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                49,
                0,
                4.8533184,
                3.5641557,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                50,
                0,
                5.1566508,
                3.5641557,
                0.16099999999999998,
                0,
                0,
                0,
                0.18837494593627718,
                0,
                VIZ_TYPE.DEFAULT,
                10008,
                1,
                4.756803545454546,
                2.750673354545455,
                0.5169090909090909,
                0,
                0,
                0,
                1.0,
                44,
                -0.510149945454546,
                -0.1290147545454552,
                -0.09490909090909089,
                0.1869798113091103,
                -0.20681754545454556,
                -0.1290147545454552,
                -0.09490909090909089,
                0.1869798113091103,
                0.09651485454545394,
                -0.1290147545454552,
                -0.09490909090909089,
                0.1869798113091103,
                0.39984725454545433,
                -0.1290147545454552,
                -0.09490909090909089,
                0.1869798113091103,
                -0.35848374545454575,
                0.14181774545454484,
                -0.09490909090909089,
                0.1869798113091103,
                -0.055151345454545364,
                0.14181774545454484,
                -0.09490909090909089,
                0.1869798113091103,
                0.24818105454545414,
                0.14181774545454484,
                -0.09490909090909089,
                0.1869798113091103,
                -0.35848374545454575,
                0.02265144545454456,
                0.16609090909090907,
                0.1869798113091103,
                -0.055151345454545364,
                0.02265144545454456,
                0.16609090909090907,
                0.1869798113091103,
                0.24818105454545414,
                0.02265144545454456,
                0.16609090909090907,
                0.1869798113091103,
                0.5515134545454545,
                0.02265144545454456,
                0.16609090909090907,
                0.1869798113091103,
                VIZ_TYPE.DEFAULT,
                10014,
                2,
                4.774188208695653,
                3.3719823782608698,
                0.5468260869565217,
                0,
                0,
                0,
                1.0,
                92,
                -0.5275346086956532,
                -0.21949207826086958,
                -0.1248260869565217,
                0.1869798113091103,
                -0.22420220869565277,
                -0.21949207826086958,
                -0.1248260869565217,
                0.1869798113091103,
                0.07913019130434673,
                -0.21949207826086958,
                -0.1248260869565217,
                0.1869798113091103,
                0.3824625913043471,
                -0.21949207826086958,
                -0.1248260869565217,
                0.1869798113091103,
                -0.37586840869565297,
                0.040507121739130625,
                -0.1248260869565217,
                0.1869798113091103,
                -0.07253600869565258,
                0.040507121739130625,
                -0.1248260869565217,
                0.1869798113091103,
                0.23079639130434693,
                0.040507121739130625,
                -0.1248260869565217,
                0.1869798113091103,
                0.5341287913043473,
                0.040507121739130625,
                -0.1248260869565217,
                0.1869798113091103,
                -0.5275346086956532,
                0.3005063217391304,
                -0.1248260869565217,
                0.1869798113091103,
                -0.22420220869565277,
                0.3005063217391304,
                -0.1248260869565217,
                0.1869798113091103,
                0.07913019130434673,
                0.3005063217391304,
                -0.1248260869565217,
                0.1869798113091103,
                0.3824625913043471,
                0.3005063217391304,
                -0.1248260869565217,
                0.1869798113091103,
                -0.22420220869565277,
                -0.3278250782608696,
                0.13617391304347826,
                0.1869798113091103,
                0.07913019130434673,
                -0.3278250782608696,
                0.13617391304347826,
                0.1869798113091103,
                0.3824625913043471,
                -0.3278250782608696,
                0.13617391304347826,
                0.1869798113091103,
                -0.37586840869565297,
                -0.06782587826086983,
                0.13617391304347826,
                0.1869798113091103,
                -0.07253600869565258,
                -0.06782587826086983,
                0.13617391304347826,
                0.1869798113091103,
                0.23079639130434693,
                -0.06782587826086983,
                0.13617391304347826,
                0.1869798113091103,
                0.5341287913043473,
                -0.06782587826086983,
                0.13617391304347826,
                0.1869798113091103,
                -0.5275346086956532,
                0.19217332173913038,
                0.13617391304347826,
                0.1869798113091103,
                -0.22420220869565277,
                0.19217332173913038,
                0.13617391304347826,
                0.1869798113091103,
                0.07913019130434673,
                0.19217332173913038,
                0.13617391304347826,
                0.1869798113091103,
                0.3824625913043471,
                0.19217332173913038,
                0.13617391304347826,
                0.1869798113091103,
                VIZ_TYPE.DEFAULT,
                10025,
                3,
                4.2466536,
                3.0441573,
                0.6829999999999999,
                0,
                0,
                0,
                1.0,
                4,
                0,
                0,
                0,
                0.1869798113091103,
                VIZ_TYPE.DEFAULT,
                10002,
                4,
                0,
                0,
                0,
                0,
                0,
                0,
                1.0,
                4,
                0,
                0,
                0,
                0,
            ]
        )
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
                    scale_factor=0.01,
                ),
                "timestep": 360.0,
                "path_to_output_dir": "../simulariumio/tests/data/physicell/",
            },
            {},
            marks=pytest.mark.raises(exception=AttributeError),
        ),
    ],
)
def test_bad_path_to_output_dir(trajectory, expected_data):
    converter = PhysicellConverter(trajectory)
    buffer_data = JsonWriter.format_trajectory_data(converter._data)
    assert expected_data == buffer_data
