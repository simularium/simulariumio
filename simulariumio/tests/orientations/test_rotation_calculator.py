#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import numpy as np

from simulariumio.orientations import ParticleRotationCalculator, OrientationData


actin_zero_orientations = [
    OrientationData(
        type_name_substrings=["actin", "2"],
        neighbor1_type_name_substrings=["actin", "1"],
        neighbor1_relative_position=(
            np.array([19.126, 20.838, 27.757]) - np.array([21.847, 24.171, 27.148])
        ),
        neighbor2_type_name_substrings=["actin", "3"],
        neighbor2_relative_position=(
            np.array([24.738, 20.881, 26.671]) - np.array([21.847, 24.171, 27.148])
        ),
    ),
    OrientationData(
        type_name_substrings=["actin", "3"],
        neighbor1_type_name_substrings=["actin", "2"],
        neighbor1_relative_position=(
            np.array([19.126, 20.838, 27.757]) - np.array([21.847, 24.171, 27.148])
        ),
        neighbor2_type_name_substrings=["actin", "1"],
        neighbor2_relative_position=(
            np.array([24.738, 20.881, 26.671]) - np.array([21.847, 24.171, 27.148])
        ),
    ),
    OrientationData(
        type_name_substrings=["actin", "1"],
        neighbor1_type_name_substrings=["actin", "3"],
        neighbor1_relative_position=(
            np.array([19.126, 20.838, 27.757]) - np.array([21.847, 24.171, 27.148])
        ),
        neighbor2_type_name_substrings=["actin", "2"],
        neighbor2_relative_position=(
            np.array([24.738, 20.881, 26.671]) - np.array([21.847, 24.171, 27.148])
        ),
    ),
    OrientationData(
        type_name_substrings=["arp3"],
        neighbor1_type_name_substrings=["arp2"],
        neighbor1_relative_position=(
            np.array([28.087, 30.872, 26.657]) - np.array([29.275, 27.535, 23.944])
        ),
        neighbor2_type_name_substrings=["actin"],
        neighbor2_relative_position=(
            np.array([30.382, 21.190, 25.725]) - np.array([29.275, 27.535, 23.944])
        ),
    ),
    OrientationData(
        type_name_substrings=["arp2#branched"],
        neighbor1_type_name_substrings=["arp3"],
        neighbor1_relative_position=(
            np.array([29.275, 27.535, 23.944]) - np.array([28.087, 30.872, 26.657])
        ),
        neighbor2_type_name_substrings=["actin#branch"],
        neighbor2_relative_position=(
            np.array([29.821, 33.088, 23.356]) - np.array([28.087, 30.872, 26.657])
        ),
    ),
    OrientationData(
        type_name_substrings=["actin#branch"],
        neighbor1_type_name_substrings=["arp2#branched"],
        neighbor1_relative_position=(
            np.array([28.087, 30.872, 26.657]) - np.array([29.821, 33.088, 23.356])
        ),
        neighbor2_type_name_substrings=["actin", "2"],
        neighbor2_relative_position=(
            np.array([30.476, 36.034, 26.528]) - np.array([29.821, 33.088, 23.356])
        ),
    ),
]


@pytest.mark.parametrize(
    "particle_type_name, particle_position, neighbor_type_names, "
    "neighbor_positions, zero_orientations, box_size, expected_rotation_degrees",
    [
        # (
        #     "A",
        #     np.array([0, 0, 0]),
        #     ["B", "C", "D"],
        #     [np.array([0, 0, 1]), np.array([-1.4, 1.4, 0]), np.array([1.4, 1.4, 0])],
        #     [
        #         OrientationData(
        #             type_name_substrings=["A"],
        #             neighbor1_type_name_substrings=["C"],
        #             neighbor1_relative_position=np.array([-1, 0, 0]),
        #             neighbor2_type_name_substrings=["D"],
        #             neighbor2_relative_position=np.array([0, 1, 0]),
        #         ),
        #     ],
        #     np.array([1000, 1000, 1000]),
        #     np.array([0, 0, -45]),
        # ),
        # (
        #     "A",
        #     np.array([0, 0, 0]),
        #     ["B", "C", "D"],
        #     [np.array([0, 0, 1]), np.array([-1, 0, 0]), np.array([0, 1, 0])],
        #     [
        #         OrientationData(
        #             type_name_substrings=["A"],
        #             neighbor1_type_name_substrings=["C"],
        #             neighbor1_relative_position=np.array([-1.4, 1.4, 0]),
        #             neighbor2_type_name_substrings=["D"],
        #             neighbor2_relative_position=np.array([1.4, 1.4, 0]),
        #         ),
        #     ],
        #     np.array([1000, 1000, 1000]),
        #     np.array([0, 0, 45]),
        # ),
        # (
        #     "actin#ATP_2",
        #     np.array([21.847, 24.171, 27.148]),
        #     ["actin#pointed_ATP_1", "actin#3"],
        #     [np.array([19.126, 20.838, 27.757]), np.array([24.738, 20.881, 26.671])],
        #     actin_zero_orientations,
        #     np.array([1000, 1000, 1000]),
        #     np.array([0, 0, 0]),
        # ),
        # (
        #     "actin#3",
        #     np.array([24.738, 20.881, 26.671]),
        #     ["actin#ATP_2", "actin#ATP_1"],
        #     [np.array([21.847, 24.171, 27.148]), np.array([27.609, 24.061, 27.598])],
        #     actin_zero_orientations,
        #     np.array([1000, 1000, 1000]),
        #     np.array([-166.3801651, 5.8753012, -2.8454839]),
        # ),
        # (
        #     "actin#ATP_1",
        #     np.array([27.609, 24.061, 27.598]),
        #     ["actin#3", "actin#ATP_2"],
        #     [np.array([24.738, 20.881, 26.671]), np.array([30.382, 21.190, 25.725])],
        #     actin_zero_orientations,
        #     np.array([1000, 1000, 1000]),
        #     np.array([26.0345086, -0.0694231, 2.2558321]), 
        # ),
        # (
        #     "actin#ATP_2",
        #     np.array([30.382, 21.190, 25.725]),
        #     ["actin#ATP_1", "actin#3"],
        #     [np.array([27.609, 24.061, 27.598]), np.array([33.374, 23.553, 27.951])],
        #     actin_zero_orientations,
        #     np.array([1000, 1000, 1000]),
        #     np.array([-140.5365114, 4.2638799, -2.8115833]), 
        # ),
        # (
        #     "actin#3",
        #     np.array([33.374, 23.553, 27.951]),
        #     ["actin#ATP_2", "actin#ATP_1"],
        #     [np.array([30.382, 21.190, 25.725]), np.array([36.075, 21.642, 25.060])],
        #     actin_zero_orientations,
        #     np.array([1000, 1000, 1000]),
        #     np.array([51.297337, 0.6129577, 4.6986271]),
        # ),
        # (
        #     "actin#ATP_1",
        #     np.array([36.075, 21.642, 25.060]),
        #     ["actin#3", "actin#ATP_2"],
        #     [np.array([33.374, 23.553, 27.951]), np.array([39.005, 22.861, 27.970])],
        #     actin_zero_orientations,
        #     np.array([1000, 1000, 1000]),
        #     np.array([-116.8241174, 3.4694235, -3.4533274]),
        # ),
        # (
        #     "arp2#branched",
        #     np.array([28.087, 30.872, 26.657]),
        #     ["arp3", "actin#branch_1"],
        #     [np.array([29.275, 27.535, 23.944]), np.array([29.821, 33.088, 23.356])],
        #     actin_zero_orientations,
        #     np.array([1000, 1000, 1000]),
        #     np.array([0, 0, 0]),  # TODO
        # ),
        # (
        #     "arp3",
        #     np.array([29.275, 27.535, 23.944]),
        #     ["arp2#branched", "actin#ATP_2"],
        #     [np.array([28.087, 30.872, 26.657]), np.array([30.382, 21.190, 25.725])],
        #     actin_zero_orientations,
        #     np.array([1000, 1000, 1000]),
        #     np.array([0, 0, 0]),  # TODO
        # ),
        # (
        #     "actin#branch_1",
        #     np.array([29.821, 33.088, 23.356]),
        #     ["arp2#branched", "actin#ATP_2"],
        #     [np.array([28.087, 30.872, 26.657]), np.array([30.476, 36.034, 26.528])],
        #     actin_zero_orientations,
        #     np.array([1000, 1000, 1000]),
        #     np.array([-14.599, -99.121, 95.285]),  # TODO [-2.8582875e-15,  0.0000000e+00, -3.1298040e-15] 
        # ),
        (
            "actin#ATP_2",
            np.array([30.476, 36.034, 26.528]),
            ["actin#branch_1", "actin#barbed_3"],
            [np.array([29.821, 33.088, 23.356]), np.array([30.897, 38.584, 23.014])],
            actin_zero_orientations,
            np.array([1000, 1000, 1000]),
            np.array([21.08, 94.243, 87.19901]),  # TODO [ 91.9681411,   4.1110625, -67.9689272]
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
    rotation = ParticleRotationCalculator.calculate_rotation(
        particle_type_name,
        particle_position,
        neighbor_type_names,
        neighbor_positions,
        zero_orientations,
        box_size,
    )
    np.testing.assert_almost_equal(np.rad2deg(rotation), expected_rotation_degrees)
