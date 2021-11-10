#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List

import numpy as np

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
        relative_position: np.ndarray, box_size: float
    ) -> np.ndarray:
        """
        if the distance between two positions is greater than box_size,
        move the second position across the box
        """
        result = np.copy(relative_position)
        for dim in range(3):
            if abs(relative_position[dim]) > box_size / 2.0:
                result[dim] -= relative_position[dim] / abs(relative_position[dim]) * box_size
        return result

    @staticmethod
    def _normalize(vector: np.ndarray) -> np.ndarray:
        """
        normalize a vector
        """
        return vector / np.linalg.norm(vector)

    @staticmethod
    def _get_rotation_matrix(v1, v2) -> np.ndarray:
        """
        Cross the vectors and get a rotation matrix
        """
        v3 = np.cross(v2, v1)
        return np.array(
            [[v1[0], v2[0], v3[0]], [v1[1], v2[1], v3[1]], [v1[2], v2[2], v3[2]]]
        )

    @staticmethod
    def _get_rotation_matrix_for_neighbor_positions(
        neighbor1_position: np.ndarray,
        neighbor2_position: np.ndarray,
        box_size: np.ndarray,
    ) -> np.ndarray:
        """
        Use the neighbor positions from an OrientationData
        to calculate a rotation matrix
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
        # make orthogonal
        v2 = ParticleRotationCalculator._normalize(
            v2 - (np.dot(v1, v2) / np.dot(v1, v1)) * v1
        )
        return ParticleRotationCalculator._get_rotation_matrix(v1, v2)

    @staticmethod
    def _get_rotation_matrix_for_particle(
        current_neighbor1_position: np.ndarray,
        current_neighbor2_position: np.ndarray,
        zero_orientation: OrientationData,
        box_size: np.ndarray,
    ) -> np.ndarray:
        """
        Get the current rotation offset from the zero orientation for a particle
        """
        zero_rotation = ParticleRotationCalculator._get_rotation_matrix_for_neighbor_positions(
            zero_orientation.neighbor1_relative_position, 
            zero_orientation.neighbor2_relative_position, 
            box_size,
        )
        current_rotation = ParticleRotationCalculator._get_rotation_matrix_for_neighbor_positions(
            current_neighbor1_position, current_neighbor2_position, box_size
        )
        return np.matmul(
            current_rotation, np.linalg.inv(zero_rotation)
        )

    @staticmethod
    def _get_euler_angles_for_rotation_matrix(rotation: np.ndarray) -> np.ndarray:
        """
        get a set of euler angles from a rotation matrix
        """
        # TODO
        return np.zeros(3)

    @staticmethod
    def get_rotation(
        particle_type_name: str,
        particle_position: np.ndarray,
        neighbor_type_names: List[str],
        neighbor_positions: List[np.ndarray],
        zero_orientations: List[OrientationData], 
        box_size: np.ndarray,
    ) -> np.ndarray:
        """
        get the difference in the particle's current orientation
        compared to the zero orientation as a rotation matrix
        """
        if len(neighbor_type_names) < 2:
            # TODO handle particles with less than 2 neighbors
            return np.zeros(3)
        # check through the zero orientations for a match
        for zero_orientation in zero_orientations:
            if zero_orientation.type_name not in particle_type_name:
                continue
            neighbor1_matches = [index for index, tn in enumerate(neighbor_type_names) if zero_orientation.neighbor1_type_name in tn]
            neighbor2_matches = [index for index, tn in enumerate(neighbor_type_names) if zero_orientation.neighbor2_type_name in tn]
            for index1 in neighbor1_matches:
                for index2 in neighbor2_matches:
                    if index1 != index2:
                        # use the first match to calculate rotation
                        return ParticleRotationCalculator._get_euler_angles_for_rotation_matrix(
                            ParticleRotationCalculator._get_rotation_matrix_for_particle(
                                neighbor_positions[index1] - particle_position,
                                neighbor_positions[index2] - particle_position,
                                zero_orientation, 
                                box_size,
                            )
                        )
        print(f"Failed to find orientation data matching {particle_type_name} with neighbors {neighbor_type_names}")
        return np.zeros(3)
