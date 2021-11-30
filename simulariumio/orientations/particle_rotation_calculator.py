#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List
from sys import float_info

import numpy as np
from scipy.spatial.transform import Rotation

from .orientation_data import OrientationData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class ParticleRotationCalculator:
    """
    This object calculates orientations for particles connected by edges
    """

    @staticmethod
    def _get_non_periodic_boundary_position(
        relative_position: np.ndarray, box_size: np.ndarray
    ) -> np.ndarray:
        """
        If the magnitude of the relative position is greater than box_size,
        move the it across the box
        """
        result = np.copy(relative_position)
        for dim in range(3):
            if abs(relative_position[dim]) > box_size[dim] / 2.0:
                result[dim] -= (
                    relative_position[dim] / abs(relative_position[dim]) * box_size[dim]
                )
        return result

    @staticmethod
    def _normalize(vector: np.ndarray) -> np.ndarray:
        """
        Normalize a vector
        """
        return vector / np.linalg.norm(vector)

    @staticmethod
    def _vectors_are_colinear(vector1: np.ndarray, vector2: np.ndarray) -> bool:
        """
        Check if two vectors are colinear to each other
        """
        return (
            abs(
                np.dot(
                    ParticleRotationCalculator._normalize(vector1),
                    ParticleRotationCalculator._normalize(vector2),
                )
            )
            >= 1 - float_info.epsilon
        )

    @staticmethod
    def _vectors_are_perpendicular(vector1: np.ndarray, vector2: np.ndarray) -> bool:
        """
        Check if two vectors are perpendicular to each other
        """
        return (
            abs(
                np.dot(
                    ParticleRotationCalculator._normalize(vector1),
                    ParticleRotationCalculator._normalize(vector2),
                )
            )
            <= 1e-6
        )

    @staticmethod
    def _get_rotation_from_neighbor_positions(
        neighbor1_position: np.ndarray,
        neighbor2_position: np.ndarray,
        box_size: np.ndarray,
    ) -> np.ndarray:
        """
        Use the relative neighbor positions to calculate a rotation matrix
        """
        # get 2 basis vectors
        v1 = ParticleRotationCalculator._normalize(
            ParticleRotationCalculator._get_non_periodic_boundary_position(
                neighbor1_position, box_size
            )
        )
        v2 = ParticleRotationCalculator._normalize(
            ParticleRotationCalculator._get_non_periodic_boundary_position(
                neighbor2_position, box_size
            )
        )
        if ParticleRotationCalculator._vectors_are_colinear(v1, v2):
            # TODO handle parallel neighbor positions
            return np.identity(3)
        # make orthogonal
        v2 = ParticleRotationCalculator._normalize(
            v2 - (np.dot(v1, v2) / np.dot(v1, v1)) * v1
        )
        if not ParticleRotationCalculator._vectors_are_perpendicular(v1, v2):
            raise Exception(
                "Neighbor vectors are not perpendicular after normalization:"
                f"\n{v1}\n{v2}"
            )
        # cross to get 3rd basis
        v3 = np.cross(v2, v1)
        # v2 = np.cross(v1, v3) TODO maybe cross again?
        # create matrix with basis
        return np.array(
            [[v1[0], v2[0], v3[0]], [v1[1], v2[1], v3[1]], [v1[2], v2[2], v3[2]]]
        )

    @staticmethod
    def _get_rotation_offset(
        current_relative_neighbor1_position: np.ndarray,
        current_relative_neighbor2_position: np.ndarray,
        zero_orientation: OrientationData,
        box_size: np.ndarray,
    ) -> np.ndarray:
        """
        Get the current rotation offset from the zero orientation for a particle
        """
        zero_rotation = (
            ParticleRotationCalculator._get_rotation_from_neighbor_positions(
                zero_orientation.neighbor1_relative_position,
                zero_orientation.neighbor2_relative_position,
                box_size,
            )
        )
        current_rotation = (
            ParticleRotationCalculator._get_rotation_from_neighbor_positions(
                current_relative_neighbor1_position,
                current_relative_neighbor2_position,
                box_size,
            )
        )
        return np.matmul(
            current_rotation, np.linalg.inv(zero_rotation)
        )  # TODO try reverse order, invert

    @staticmethod
    def _get_euler_angles(rotation_matrix: np.ndarray) -> np.ndarray:
        """
        Get a set of euler angles representing a rotation matrix
        """
        rotation = Rotation.from_matrix(rotation_matrix)
        result = rotation.as_euler("xyz", degrees=False)
        return result

    @staticmethod
    def calculate_rotation(
        particle_type_name: str,
        particle_position: np.ndarray,
        neighbor_type_names: List[str],
        neighbor_positions: List[np.ndarray],
        zero_orientations: List[OrientationData],
        box_size: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate the difference in the particle's current orientation
        compared to the zero orientation and get euler angles
        representing the current rotation.

        Parameters
        ----------
        particle_type_name: str
            The type name of the particle
        particle_position: np.ndarray
            The position of the particle
        neighbor_type_names: List[str]
            The type names of the neighbors of the particle
        neighbor_positions: List[np.ndarray]
            The positions of the neighbors of the particle,
            in the same order as the type names
        zero_orientations: List[OrientationData]
            A list of possible zero orientation definitions to be subtracted
            from the current orientation to get current rotation
        box_size: np.ndarray (shape = [3])
            The size of the reaction volume in X, Y, and Z
        """
        if len(neighbor_type_names) < 2:
            # TODO handle particles with less than 2 neighbors
            return np.zeros(3)
        # check through the zero orientations for a match
        for zero_orientation in zero_orientations:
            if not zero_orientation.type_name_matches(particle_type_name):
                continue
            neighbor1_matches = [
                index
                for index, tn in enumerate(neighbor_type_names)
                if zero_orientation.neighbor1_type_name_matches(tn)
            ]
            for index1 in neighbor1_matches:
                for index2, tn2 in enumerate(neighbor_type_names):
                    if index2 == index1:
                        continue
                    if not zero_orientation.neighbor2_type_name_matches(tn2):
                        continue
                    # use the first match to calculate rotation
                    return ParticleRotationCalculator._get_euler_angles(
                        ParticleRotationCalculator._get_rotation_offset(
                            neighbor_positions[index1] - particle_position,
                            neighbor_positions[index2] - particle_position,
                            zero_orientation,
                            box_size,
                        )
                    )
        print(
            f"Failed to find orientation data matching {particle_type_name} "
            f"with neighbors {neighbor_type_names}"
        )
        return np.zeros(3)
