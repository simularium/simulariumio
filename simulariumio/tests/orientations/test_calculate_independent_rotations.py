#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import numpy as np

from simulariumio.orientations import (
    ParticleRotationCalculator,
    OrientationData,
    NeighborData,
)

from simulariumio.tests.conftest import (
    test_zero_orientations,
    # actin_zero_orientations
)


@pytest.mark.parametrize(
    "rotation_calculator, expected_rotation_degrees",
    [
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
        # (
        #     "actin#ATP_2",
        #     np.array([21.847, 24.171, 27.148]),
        #     ["actin#pointed_ATP_1", "actin#3"],
        #     [np.array([19.126, 20.838, 27.757]), np.array([24.738, 20.881, 26.671])],
        #     None,
        #     actin_zero_orientations,
        #     np.array(3 * [np.inf]),
        #     np.array([-166.6038468, -6.3759819, -1.3937068]),
        # ),
        # (
        #     "actin#3",
        #     np.array([24.738, 20.881, 26.671]),
        #     ["actin#ATP_2", "actin#ATP_1"],
        #     [np.array([21.847, 24.171, 27.148]), np.array([27.609, 24.061, 27.598])],
        #     None,
        #     actin_zero_orientations,
        #     np.array(3 * [np.inf]),
        #     np.array([-166.6038468, -6.3759819, -1.3937068]),
        # ),
        # (
        #     "actin#ATP_1",
        #     np.array([27.609, 24.061, 27.598]),
        #     ["actin#3", "actin#ATP_2"],
        #     [np.array([24.738, 20.881, 26.671]), np.array([30.382, 21.190, 25.725])],
        #     None,
        #     actin_zero_orientations,
        #     np.array(3 * [np.inf]),
        #     np.array([26.0148045, -1.0522464, -1.9967026]),
        # ),
        # (
        #     "actin#ATP_2",
        #     np.array([30.382, 21.190, 25.725]),
        #     ["actin#ATP_1", "actin#3"],
        #     [np.array([27.609, 24.061, 27.598]), np.array([33.374, 23.553, 27.951])],
        #     None,
        #     actin_zero_orientations,
        #     np.array(3 * [np.inf]),
        #     np.array([-140.6174016, -5.077777, 0.536663]),
        # ),
        # (
        #     "actin#3",
        #     np.array([33.374, 23.553, 27.951]),
        #     ["actin#ATP_2", "actin#ATP_1"],
        #     [np.array([30.382, 21.190, 25.725]), np.array([36.075, 21.642, 25.060])],
        #     None,
        #     actin_zero_orientations,
        #     np.array(3 * [np.inf]),
        #     np.array([51.224489, -3.2825276, -3.419032]),
        # ),
        # (
        #     "actin#ATP_1",
        #     np.array([36.075, 21.642, 25.060]),
        #     ["actin#3", "actin#ATP_2"],
        #     [np.array([33.374, 23.553, 27.951]), np.array([39.005, 22.861, 27.970])],
        #     None,
        #     actin_zero_orientations,
        #     np.array(3 * [np.inf]),
        #     np.array([-116.8663939, -4.646753, 1.5364412]),
        # ),
        # (
        #     "arp2#branched",
        #     np.array([28.087, 30.872, 26.657]),
        #     ["arp3", "actin#branch_1"],
        #     [np.array([29.275, 27.535, 23.944]), np.array([29.821, 33.088, 23.356])],
        #     None,
        #     actin_zero_orientations,
        #     np.array(3 * [np.inf]),
        #     None,
        # ),
        # (
        #     "arp3",
        #     np.array([29.275, 27.535, 23.944]),
        #     ["arp2#branched", "actin#ATP_2"],
        #     [np.array([28.087, 30.872, 26.657]), np.array([30.382, 21.190, 25.725])],
        #     None,
        #     actin_zero_orientations,
        #     np.array(3 * [np.inf]),
        #     None,
        # ),
        # (
        #     "actin#branch_1",
        #     np.array([29.821, 33.088, 23.356]),
        #     ["arp2#branched", "actin#ATP_2"],
        #     [np.array([28.087, 30.872, 26.657]), np.array([30.476, 36.034, 26.528])],
        #     None,
        #     actin_zero_orientations,
        #     np.array(3 * [np.inf]),
        #     np.array([0.0, 0.0, 0.0]),
        # ),
        # (
        #     "actin#ATP_2",
        #     np.array([30.476, 36.034, 26.528]),
        #     ["actin#branch_1", "actin#barbed_3"],
        #     [np.array([29.821, 33.088, 23.356]), np.array([30.897, 38.584, 23.014])],
        #     None,
        #     actin_zero_orientations,
        #     np.array(3 * [np.inf]),
        #     np.array([95.1894872, 67.7454082, -8.9182859]),
        # ),
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
