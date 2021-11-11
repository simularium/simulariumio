#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import numpy as np

from simulariumio.orientations import ParticleRotationCalculator, OrientationData


@pytest.mark.parametrize(
    "particle_type_name, particle_position, neighbor_type_names, "
    "neighbor_positions, zero_orientations, box_size, expected_rotation",
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
    ],
)
def test_rotation_calculator(
    particle_type_name,
    particle_position,
    neighbor_type_names,
    neighbor_positions,
    zero_orientations,
    box_size,
    expected_rotation,
):
    rotation = ParticleRotationCalculator.calculate_rotation(
        particle_type_name,
        particle_position,
        neighbor_type_names,
        neighbor_positions,
        zero_orientations,
        box_size,
    )
    np.testing.assert_almost_equal(rotation, expected_rotation)
