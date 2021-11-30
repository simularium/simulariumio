#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import numpy as np

from simulariumio.orientations import ParticleRotationCalculator, OrientationData
from simulariumio.tests.conftest import actin_zero_orientations


@pytest.mark.parametrize(
    "particle_type_name, particle_position, neighbor_type_names, "
    "neighbor_positions, zero_orientations, box_size, expected_rotation_degrees",
    [
        (
            "A",
            np.array([0, 0, 0]),
            ["B", "C", "D"],
            [np.array([0, 0, 1]), np.array([-1.4, 1.4, 0]), np.array([1.4, 1.4, 0])],
            [
                OrientationData(
                    type_name_substrings=["A"],
                    neighbor1_type_name_substrings=["C"],
                    neighbor1_relative_position=np.array([-1, 0, 0]),
                    neighbor2_type_name_substrings=["D"],
                    neighbor2_relative_position=np.array([0, 1, 0]),
                ),
            ],
            np.array([1000, 1000, 1000]),
            np.array([0, 0, -45]),
        ),
        (
            "A",
            np.array([0, 0, 0]),
            ["B", "C", "D"],
            [np.array([0, 0, 1]), np.array([-1, 0, 0]), np.array([0, 1, 0])],
            [
                OrientationData(
                    type_name_substrings=["A"],
                    neighbor1_type_name_substrings=["C"],
                    neighbor1_relative_position=np.array([-1.4, 1.4, 0]),
                    neighbor2_type_name_substrings=["D"],
                    neighbor2_relative_position=np.array([1.4, 1.4, 0]),
                ),
            ],
            np.array([1000, 1000, 1000]),
            np.array([0, 0, 45]),
        ),
        (
            "actin#ATP_2",
            np.array([21.847, 24.171, 27.148]),
            ["actin#pointed_ATP_1", "actin#3"],
            [np.array([19.126, 20.838, 27.757]), np.array([24.738, 20.881, 26.671])],
            actin_zero_orientations,
            np.array([1000, 1000, 1000]),
            np.array([0, 0, 0]),
        ),
        (
            "actin#3",
            np.array([24.738, 20.881, 26.671]),
            ["actin#ATP_2", "actin#ATP_1"],
            [np.array([21.847, 24.171, 27.148]), np.array([27.609, 24.061, 27.598])],
            actin_zero_orientations,
            np.array([1000, 1000, 1000]),
            np.array([-166.6038468, -6.3759819, -1.3937068]),
        ),
        (
            "actin#ATP_1",
            np.array([27.609, 24.061, 27.598]),
            ["actin#3", "actin#ATP_2"],
            [np.array([24.738, 20.881, 26.671]), np.array([30.382, 21.190, 25.725])],
            actin_zero_orientations,
            np.array([1000, 1000, 1000]),
            np.array([26.0148045, -1.0522464, -1.9967026]),
        ),
        (
            "actin#ATP_2",
            np.array([30.382, 21.190, 25.725]),
            ["actin#ATP_1", "actin#3"],
            [np.array([27.609, 24.061, 27.598]), np.array([33.374, 23.553, 27.951])],
            actin_zero_orientations,
            np.array([1000, 1000, 1000]),
            np.array([-140.6174016, -5.077777, 0.536663]),
        ),
        (
            "actin#3",
            np.array([33.374, 23.553, 27.951]),
            ["actin#ATP_2", "actin#ATP_1"],
            [np.array([30.382, 21.190, 25.725]), np.array([36.075, 21.642, 25.060])],
            actin_zero_orientations,
            np.array([1000, 1000, 1000]),
            np.array([51.224489, -3.2825276, -3.419032]),
        ),
        (
            "actin#ATP_1",
            np.array([36.075, 21.642, 25.060]),
            ["actin#3", "actin#ATP_2"],
            [np.array([33.374, 23.553, 27.951]), np.array([39.005, 22.861, 27.970])],
            actin_zero_orientations,
            np.array([1000, 1000, 1000]),
            np.array([-116.8663939, -4.646753, 1.5364412]),
        ),
        (
            "arp2#branched",
            np.array([28.087, 30.872, 26.657]),
            ["arp3", "actin#branch_1"],
            [np.array([29.275, 27.535, 23.944]), np.array([29.821, 33.088, 23.356])],
            actin_zero_orientations,
            np.array([1000, 1000, 1000]),
            np.array([0, 0, 0]),
        ),
        (
            "arp3",
            np.array([29.275, 27.535, 23.944]),
            ["arp2#branched", "actin#ATP_2"],
            [np.array([28.087, 30.872, 26.657]), np.array([30.382, 21.190, 25.725])],
            actin_zero_orientations,
            np.array([1000, 1000, 1000]),
            np.array([0, 0, 0]),
        ),
        (
            "actin#branch_1",
            np.array([29.821, 33.088, 23.356]),
            ["arp2#branched", "actin#ATP_2"],
            [np.array([28.087, 30.872, 26.657]), np.array([30.476, 36.034, 26.528])],
            actin_zero_orientations,
            np.array([1000, 1000, 1000]),
            np.array([0.0, 0.0, 0.0]),
        ),
        (
            "actin#ATP_2",
            np.array([30.476, 36.034, 26.528]),
            ["actin#branch_1", "actin#barbed_3"],
            [np.array([29.821, 33.088, 23.356]), np.array([30.897, 38.584, 23.014])],
            actin_zero_orientations,
            np.array([1000, 1000, 1000]),
            np.array([95.1894872, 67.7454082, -8.9182859]),
        ),
    ],
)
def test_rotation_calculator(
    particle_type_name,
    particle_position,
    neighbor_type_names,
    neighbor_positions,
    zero_orientations,
    box_size,
    expected_rotation_degrees,
):
    rotation = np.rad2deg(
        ParticleRotationCalculator.calculate_rotation(
            particle_type_name,
            particle_position,
            neighbor_type_names,
            neighbor_positions,
            zero_orientations,
            box_size,
        )
    )
    np.testing.assert_almost_equal(rotation, expected_rotation_degrees)


@pytest.mark.parametrize(
    "vector1, vector2, expected",
    [
        (
            np.array([1.0, 0.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
            True,
        ),
        (
            np.array([30.476, 36.034, 26.528]),
            np.array([304.76, 360.34, 265.28]),
            True,
        ),
        (
            np.array([0.0, 1.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
            False,
        ),
        (
            np.array([1.0, 0.0, 0.0]),
            np.array([-1.0, 0.0, 0.0]),
            True,
        ),
        (
            np.array([-0.3013853, 0.5702147, -0.7642134]),
            np.array([0.3013853, -0.5702147, 0.7642134]),
            True,
        ),
        (
            np.array([-0.3013853, 0.5702147, -0.7642134]),
            np.array([5.46372266, 7.60125865, 3.51690213]),
            False,
        ),
    ],
)
def test_vectors_colinear(vector1, vector2, expected):
    assert (
        ParticleRotationCalculator._vectors_are_colinear(vector1, vector2) == expected
    )
