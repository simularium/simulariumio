#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import numpy as np

from simulariumio.orientations import ParticleRotationCalculator
from simulariumio.tests.conftest import test_zero_orientations


@pytest.mark.parametrize(
    "rotation_calculator, particle_rot_calculators, expected_rotation_degrees",
    [
        (
            ParticleRotationCalculator(
                type_name="C",
                position=np.array([0, 0, 0]),
                neighbor_ids=[3],
                neighbor_type_names=["D"],
                neighbor_positions=[np.array([0.5, 0.88, 0])],
                zero_orientations=test_zero_orientations,
                box_size=np.array(3 * [np.inf]),
            ),
            {
                3: ParticleRotationCalculator(
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
                )
            },
            np.array([180, 0, -60.3955493]),
        )
    ],
)
def test_dependent_rotation_calculator(
    rotation_calculator,
    particle_rot_calculators,
    expected_rotation_degrees,
):
    if particle_rot_calculators is not None:
        rotation_calculator.calculate_dependent_rotation(particle_rot_calculators)
    euler_angles = rotation_calculator.get_euler_angles()
    if euler_angles is None:
        assert expected_rotation_degrees is None
    else:
        assert expected_rotation_degrees is not None
        np.testing.assert_almost_equal(
            np.rad2deg(euler_angles), expected_rotation_degrees
        )
