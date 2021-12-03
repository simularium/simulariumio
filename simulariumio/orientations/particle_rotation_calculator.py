#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Tuple
from sys import float_info

import numpy as np
import scipy
import random

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
        (either parallel or anti-parallel)
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
    def _rotate(vector: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
        """
        rotate a vector around axis by angle (radians)
        """
        rotation = scipy.linalg.expm(np.cross(np.eye(3), ReaddyUtil.normalize(axis) * angle))
        return np.dot(rotation, np.copy(vector))

    @staticmethod
    def _get_random_perpendicular_vector(vector: np.ndarray) -> np.ndarray:
        """
        get a random unit vector perpendicular to vector
        """
        if vector[0] == 0 and vector[1] == 0:
            if vector[2] == 0:
                raise ValueError("zero vector")
            return np.array([0, 1, 0])
        unit_vector = ParticleRotationCalculator._normalize(np.array([-vector[1], vector[0], 0]))
        return ParticleRotationCalculator._rotate(unit_vector, vector, 2 * np.pi * random.random())

    @staticmethod
    def _get_rotation_matrix(vector1: np.ndarray, vector2: np.ndarray) -> np.ndarray:
        """
        create a rotation matrix given two basis vectors
        """
        # cross to get 3rd basis
        vector3 = np.cross(vector2, vector1)
        # create matrix with basis
        return np.array(
            [[vector1[0], vector2[0], vector3[0]], 
             [vector1[1], vector2[1], vector3[1]], 
             [vector1[2], vector2[2], vector3[2]]]
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
            return None
        # make orthogonal
        v2 = ParticleRotationCalculator._normalize(
            v2 - (np.dot(v1, v2) / np.dot(v1, v1)) * v1
        )
        return ParticleRotationCalculator._get_rotation_matrix(v1, v2)

    @staticmethod
    def _get_rotation_from_neighbor_transform(
        particle_type_name: str,
        matching_neighbor: int,
        neighbor_type_name: str,
        neighbor_position: np.ndarray,
        neighbor_rotation: np.ndarray,
        box_size: np.ndarray,
    ) -> np.ndarray:
        """
        Use the relative neighbor position and 
        either the neighbor's rotation or a random direction
        to calculate a rotation matrix
        """
        # get first basis vector from neighbor position
        v1 = ParticleRotationCalculator._normalize(
            ParticleRotationCalculator._get_non_periodic_boundary_position(
                current_relative_neighbor_position, box_size
            )
        )
        if neighbor_rotation is None:
            # neighbor's rotation is not set, so calculate 
            # a random rotation around the neighbor axis
            v2 = ParticleRotationCalculator._get_random_perpendicular_vector(v1)
        else:
            # TODO
            
            n_zero_orientation, n1_i, n2_i = ParticleRotationCalculator._get_matching_zero_rotation(
                particle_type_name,
                [neighbor_type_name],
                zero_orientations,
                neighbor_rotations is not None,
            )
            neighbor_number = 2 if n1_i is None else 1 # this particle is which neighbor to its neighbor
            neighbor_rotation
            matching_neighbor
            
            
            
            
            
            
        return ParticleRotationCalculator._get_rotation_matrix(v1, v2)

    @staticmethod
    def _get_rotation_matrix_with_1_neighbor(
        current_relative_neighbor_position: np.ndarray,
        current_neighbor_rotation: np.ndarray,
        matching_neighbor: int,
        zero_orientation: OrientationData,
        box_size: np.ndarray,
    ) -> np.ndarray:
        """
        Get the current rotation offset from the zero orientation 
        for a particle with 1 neighbor
        """
        zero_rotation = (
            ParticleRotationCalculator._get_rotation_from_neighbor_positions(
                zero_orientation.neighbor1_relative_position,
                zero_orientation.neighbor2_relative_position,
                box_size,
            )
        )
        current_rotation = ParticleRotationCalculator._get_rotation_from_neighbor_transform(
                current_relative_neighbor_position,
                current_neighbor_rotation,
                box_size,
        )

    @staticmethod
    def _get_rotation_matrix_with_2_neighbors(
        current_relative_neighbor1_position: np.ndarray,
        current_relative_neighbor2_position: np.ndarray,
        zero_orientation: OrientationData,
        box_size: np.ndarray,
    ) -> np.ndarray:
        """
        Get the current rotation offset from the zero orientation 
        for a particle with 2 neighbors
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
        return np.matmul(current_rotation, np.linalg.inv(zero_rotation))

    @staticmethod
    def _get_euler_angles(rotation_matrix: np.ndarray) -> np.ndarray:
        """
        Get a set of euler angles in radians representing a rotation matrix
        """
        rotation = scipy.spatial.transform.Rotation.from_matrix(rotation_matrix)
        result = rotation.as_euler("XYZ", degrees=False)
        return result

    @staticmethod
    def _get_matching_zero_rotation(
        particle_type_name: str,
        neighbor_type_names: List[str],
        zero_orientations: List[OrientationData],
        calculate_dependent_rotations: bool,
    ) -> Tuple[OrientationData, int, int]:
        """
        Get the matching zero orientation data 
        for the particle and neighbors of the given types
        """
        # check through the zero orientations for a match
        for zero_orientation in zero_orientations:
            if not zero_orientation.type_name_matches(particle_type_name):
                # this zero orientation is not for this type of particle
                continue
            # get all the matches with the neighbor1 types
            neighbor1_matches = [
                index
                for index, tn in enumerate(neighbor_type_names)
                if zero_orientation.neighbor1_type_name_matches(tn)
            ]
            if len(neighbor_type_names) == 1 and calculate_dependent_rotations:
                # if there's only one neighbor and we've already calculated independent rotations
                if len(neighbor1_matches) > 0:
                    # use the first match
                    return zero_orientation, neighbor1_matches[0], None
                else:
                    # if no match in neighbor1 types, check in the neighbor2 types
                    neighbor2_matches = [
                        index
                        for index, tn in enumerate(neighbor_type_names)
                        if zero_orientation.neighbor2_type_name_matches(tn)
                    ]
                    if len(neighbor2_matches) > 0:
                        # use the first match
                        return zero_orientation, None, neighbor2_matches[0]
            else:
                # if there's two or more neighbors
                for index1 in neighbor1_matches:
                    # check if another neighbor matches neighbor2 type
                    for index2, tn2 in enumerate(neighbor_type_names):
                        if index2 == index1:
                            continue
                        if not zero_orientation.neighbor2_type_name_matches(tn2):
                            continue
                        # use the first match
                        return zero_orientation, index1, index2
        print(
            f"Failed to find orientation data matching {particle_type_name} "
            f"with neighbors {neighbor_type_names}"
        )
        return None, None, None

    @staticmethod
    def calculate_rotation(
        particle_type_name: str,
        particle_position: np.ndarray,
        neighbor_type_names: List[str],
        neighbor_positions: List[np.ndarray],
        neighbor_rotations: List[np.ndarray],
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
        neighbor_rotations: List[np.ndarray]
            The rotations of the neighbors of the particle,
            in the same order as the type names.
            Note: this is only used for calculating relative rotations 
                of particles with one neighbor whose rotation is fixed 
                by its other neighbors. If this is None,
                don't calculate rotations for particles with one neighbor
        zero_orientations: List[OrientationData]
            A list of possible zero orientation definitions to be subtracted
            from the current orientation to get current rotation
        box_size: np.ndarray (shape = [3])
            The size of the reaction volume in X, Y, and Z
        """                    
        if len(neighbor_type_names) < 1:
            # TODO handle particles with no neighbors
            return None  
        zero_orientation, neighbor1_index, neighbor2_index = ParticleRotationCalculator._get_matching_zero_rotation(
            particle_type_name,
            neighbor_type_names,
            zero_orientations,
            neighbor_rotations is not None,
        )
        if zero_orientation is None:
            print(
                f"Failed to find orientation data matching {particle_type_name} "
                f"with neighbors {neighbor_type_names}"
            )
            return None
        if neighbor1_index is None or neighbor2_index is None:
            neighbor_index = neighbor2_index if neighbor1_index is None else neighbor1_index
            return ParticleRotationCalculator._get_euler_angles(
                    ParticleRotationCalculator._get_rotation_matrix_with_1_neighbor(
                        neighbor_positions[neighbor_index] - particle_position,
                        neighbor_rotations[neighbor_index],
                        2 if neighbor1_index is None else 1,
                        zero_orientation,
                        box_size,
                    )
                )
        else:
            return ParticleRotationCalculator._get_euler_angles(
                    ParticleRotationCalculator._get_rotation_matrix_with_2_neighbors(
                        neighbor_positions[neighbor1_index] - particle_position,
                        neighbor_positions[neighbor2_index] - particle_position,
                        zero_orientation,
                        box_size,
                    )
                )
