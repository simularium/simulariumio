#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import numpy as np

from simulariumio.readdy import (
    ParticleRotationCalculator,
    OrientationData,
    NeighborData,
)

from simulariumio.tests.conftest import test_zero_orientations


@pytest.mark.parametrize(
    "rotation_calculator, expected_rotation_degrees",
    [
        # Rotated 45 degrees clockwise
        #
        # Zero:
        # z = 0
        # y
        # ^         D
        # |         |
        # |    B -- C
        # |
        # |_ _ _ _ > x
        #
        # Current:
        # z = 0
        # y
        # ^    B      D
        # |     \    /
        # |      \  /
        # |       C
        # |_ _ _ _ > x
        (
            ParticleRotationCalculator(
                type_name="C",
                position=np.array([0, 0, 0]),
                neighbor_ids=[5, 1, 3],
                neighbor_type_names=["F", "B", "D"],
                neighbor_positions=[
                    np.array([0, 0, 1]),
                    np.array([-1.4, 1.4, 0]),
                    np.array([1.4, 1.4, 0]),
                ],
                zero_orientations=test_zero_orientations,
                box_size=np.array(3 * [np.inf]),
            ),
            np.array([0, 0, -45]),
        ),
        # Rotated 45 degrees counter-clockwise
        #
        # Zero:
        # z = 0
        # y
        # ^    B      D
        # |     \    /
        # |      \  /
        # |       C
        # |_ _ _ _ > x
        #
        # Current:
        # z = 0
        # y
        # ^         D
        # |         |
        # |    B -- C
        # |
        # |_ _ _ _ > x
        (
            ParticleRotationCalculator(
                type_name="C",
                position=np.array([0, 0, 0]),
                neighbor_ids=[5, 1, 3],
                neighbor_type_names=["F", "B", "D"],
                neighbor_positions=[
                    np.array([0, 0, 1]),
                    np.array([-1, 0, 0]),
                    np.array([0, 1, 0]),
                ],
                zero_orientations=[
                    OrientationData(
                        type_name_substrings=["C"],
                        neighbor_data=[
                            NeighborData(
                                type_name_substrings=["B"],
                                relative_position=np.array([-1.4, 1.4, 0]),
                            ),
                            NeighborData(
                                type_name_substrings=["D"],
                                relative_position=np.array([1.4, 1.4, 0]),
                            ),
                        ],
                    ),
                ],
                box_size=np.array(3 * [np.inf]),
            ),
            np.array([0, 0, 45]),
        ),
        # Rotated 45 degrees clockwise, with test particle not at origin
        #
        # Zero:
        # z = 0
        # y
        # ^
        # |    D -- E
        # |    |
        # |    C
        # |_ _ _ _ > x
        #
        # Current:
        # z = 0
        # y
        # ^       D
        # |      /  \
        # |     /    \
        # |    C      E
        # |_ _ _ _ > x
        (
            ParticleRotationCalculator(
                type_name="D",
                position=np.array([1.4, 1.4, 0]),
                neighbor_ids=[2, 4],
                neighbor_type_names=["C", "E"],
                neighbor_positions=[np.array([0, 0, 0]), np.array([2.8, 0, 0])],
                zero_orientations=test_zero_orientations,
                box_size=np.array(3 * [np.inf]),
            ),
            np.array([0, 0, -45]),
        ),
        # Rotated ~30 degrees clockwise, with test particle not at origin
        #
        # Zero:
        # z = 0
        # y
        # ^
        # |    D -- E
        # |    |
        # |    C
        # |_ _ _ _ > x
        #
        # Current:
        # z = 0
        # y
        # ^       D
        # |      /  \
        # |     /    \
        # |    C      E
        # |_ _ _ _ > x
        (
            ParticleRotationCalculator(
                type_name="D",
                position=np.array([0.5, 0.88, 0]),
                neighbor_ids=[2, 4],
                neighbor_type_names=["C", "E"],
                neighbor_positions=[
                    np.array([0, 0, 0]),
                    np.array([1.38, 0.38, 0]),
                ],
                zero_orientations=test_zero_orientations,
                box_size=np.array(3 * [np.inf]),
            ),
            np.array([0, 0, -29.6044507]),
        ),
    ],
)
def test_calculate_independent_rotations(
    rotation_calculator,
    expected_rotation_degrees,
):
    euler_angles = rotation_calculator.get_euler_angles()
    if euler_angles is None:
        assert expected_rotation_degrees is None
    else:
        assert expected_rotation_degrees is not None
        np.testing.assert_almost_equal(
            np.rad2deg(euler_angles), expected_rotation_degrees
        )
