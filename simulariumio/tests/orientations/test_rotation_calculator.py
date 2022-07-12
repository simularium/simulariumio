#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import numpy as np

from simulariumio.orientations import (
    ParticleRotationCalculator,
    OrientationData,
    NeighborData,
    RotationUtility,
)

from simulariumio.tests.conftest import test_zero_orientations


@pytest.mark.parametrize(
    "particle_type_name, particle_position, neighbor_ids, "
    "neighbor_type_names, neighbor_positions, particle_rot_calculators, "
    "zero_orientations, box_size, expected_rotation_degrees",
    [
        (
            "C",                         # particle_type_name
            np.array([0, 0, 0]),         # particle_position
            [3],                         # neighbor_ids
            ["D"],                       # neighbor_type_names
            [np.array([0.5, 0.88, 0])],   # neighbor_positions
            {                            # particle_rot_calculators
                3: ParticleRotationCalculator(
                    "D",                                           # type_name
                    np.array([0.5, 0.88, 0]),                       # position
                    [2, 4],                                        # neighbor_ids
                    ["C", "E"],                                    # neighbor_type_names
                    [np.array([0, 0, 0]), np.array([1.38, 0.38, 0])],  # neighbor_positions
                    test_zero_orientations,                        # zero_orientations
                    np.array(3 * [np.inf]),                        # box_size
                )
            },
            test_zero_orientations,       # zero_orientations
            np.array(3 * [np.inf]),       # box_size
            np.array([180, 0, -60]),      # expected_rotation_degrees
        ),
    ],
)
def test_rotation_calculator(
    particle_type_name,
    particle_position,
    neighbor_ids,
    neighbor_type_names,
    neighbor_positions,
    particle_rot_calculators,
    zero_orientations,
    box_size,
    expected_rotation_degrees,
):
    rotation_calculator = ParticleRotationCalculator(
        particle_type_name,
        particle_position,
        neighbor_ids,
        neighbor_type_names,
        neighbor_positions,
        zero_orientations,
        box_size,
    )
    if particle_rot_calculators is not None:
        rotation_calculator.calculate_dependent_rotation(particle_rot_calculators)
    euler_angles = rotation_calculator.get_euler_angles()
    x = np.rad2deg(euler_angles)
    raise Exception(f"{x}\n\n{expected_rotation_degrees}")
    if euler_angles is None:
        assert expected_rotation_degrees is None
    else:
        assert expected_rotation_degrees is not None
        np.testing.assert_almost_equal(
            np.rad2deg(euler_angles), expected_rotation_degrees
        )

