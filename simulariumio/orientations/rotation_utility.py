#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Tuple
from sys import float_info

import numpy as np
from scipy.linalg import expm
from scipy.spatial.transform import Rotation
import random

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class RotationUtility:
    """
    This object has helper functions for calculating rotations.
    """

    @staticmethod
    def _rotate(vector: np.ndarray, axis: np.ndarray, angle: float) -> np.ndarray:
        """
        rotate a vector around axis by angle (radians)
        """
        rotation_matrix = expm(np.cross(np.eye(3), RotationUtility.normalize(axis) * angle))
        return np.dot(rotation_matrix, np.copy(vector))

    @staticmethod
    def get_random_perpendicular_vector(vector: np.ndarray) -> np.ndarray:
        """
        Get a random unit vector perpendicular to a vector.

        Parameters
        ----------
        vector: np.ndarray
            A numpy array of the vector
        """
        if vector[0] == 0 and vector[1] == 0:
            if vector[2] == 0:
                raise ValueError("zero vector")
            return np.array([0, 1, 0])
        unit_vector = RotationUtility.normalize(np.array([-vector[1], vector[0], 0]))
        return RotationUtility._rotate(unit_vector, vector, 2 * np.pi * random.random())

    @staticmethod
    def get_non_periodic_boundary_position(
        relative_position: np.ndarray, box_size: np.ndarray
    ) -> np.ndarray:
        """
        If the magnitude of a difference in positions is greater than box size,
        move the it across the box.

        Parameters
        ----------
        relative_position: np.ndarray (shape=3)
            A numpy array of a difference in positions within the box
        box_size: np.ndarray (shape=3)
            A numpy array of the box size in X, Y, and Z dimensions
        """
        result = np.copy(relative_position)
        for dim in range(3):
            if relative_position is None:
                raise Exception("relative_position is None")
            if abs(relative_position[dim]) > box_size[dim] / 2.0:
                result[dim] -= (
                    relative_position[dim] / abs(relative_position[dim]) * box_size[dim]
                )
        return result

    @staticmethod
    def normalize(vector: np.ndarray) -> np.ndarray:
        """
        Normalize a vector.

        Parameters
        ----------
        vector: np.ndarray
            A numpy array to normalize
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
                    RotationUtility.normalize(vector1),
                    RotationUtility.normalize(vector2),
                )
            )
            >= 1 - float_info.epsilon
        )

    @staticmethod
    def get_rotation_matrix_from_bases(vector1: np.ndarray, vector2: np.ndarray) -> np.ndarray:
        """
        Create a rotation matrix given two basis vectors.

        Parameters
        ----------
        vector1: np.ndarray
            A numpy array for the first basis vector (already normalized)
        vector2: np.ndarray
            A numpy array for the second basis vector (already normalized)
        """
        # cross to get 3rd basis
        vector3 = np.cross(vector2, vector1)
        # create matrix with basis
        return np.array(
            [
                [vector1[0], vector2[0], vector3[0]],
                [vector1[1], vector2[1], vector3[1]],
                [vector1[2], vector2[2], vector3[2]],
            ]
        )

    @staticmethod
    def get_rotation_matrix_from_neighbor_positions(
        neighbor1_position: np.ndarray,
        neighbor2_position: np.ndarray,
        box_size: np.ndarray = np.array(3 * [np.inf]),
    ) -> np.ndarray:
        """
        Use the relative positions of neighbor agents to calculate a rotation matrix.

        Parameters
        ----------
        neighbor1_position: np.ndarray
            A numpy array of the relative position of a agent's first neighbor
        neighbor2_position: np.ndarray
            A numpy array of the relative position of a agent's second neighbor
        box_size: np.ndarray (shape=3) (optional)
            A numpy array of the box size in X, Y, and Z dimensions
                Default = [inf, inf, inf], don't account for periodic boundaries
        """
        # get 2 basis vectors
        v1 = RotationUtility.normalize(
            RotationUtility.get_non_periodic_boundary_position(
                neighbor1_position, box_size
            )
        )
        v2 = RotationUtility.normalize(
            RotationUtility.get_non_periodic_boundary_position(
                neighbor2_position, box_size
            )
        )
        if RotationUtility._vectors_are_colinear(v1, v2):
            # neighbor positions are colinear (try one neighbor method instead later)
            return None
        # make orthogonal
        v2 = RotationUtility.normalize(v2 - (np.dot(v1, v2) / np.dot(v1, v1)) * v1)
        return RotationUtility.get_rotation_matrix_from_bases(v1, v2)

    @staticmethod
    def get_euler_angles_for_rotation_matrix(rotation_matrix: np.ndarray) -> np.ndarray:
        """
        Get a set of euler angles in radians representing a rotation matrix.

        Parameters
        ----------
        rotation_matrix: np.ndarray (shape=(3,3))
            A numpy array of the rotation matrix for which to get euler angles
        """
        if rotation_matrix is None:
            return None
        return Rotation.from_matrix(rotation_matrix).as_euler("XYZ", degrees=False)

    @staticmethod
    def get_rotation_matrix_from_euler_angles(euler_angles: np.ndarray) -> np.ndarray:
        """
        Get a rotation matrix represented by a set of euler angles in radians.

        Parameters
        ----------
        euler_angles: np.ndarray (shape=(3))
            A numpy array of the euler angles
        """
        return Rotation.from_euler("XYZ", euler_angles, degrees=False).as_matrix()
