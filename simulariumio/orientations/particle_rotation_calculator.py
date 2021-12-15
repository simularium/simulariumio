#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import List, Tuple
from sys import float_info

import numpy as np

from .orientation_data import OrientationData
from .rotation_utility import RotationUtility

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class ParticleRotationCalculator:
    """
    This object calculates orientations for particles connected by edges
    """

    @staticmethod
    def _get_rotation_matrix_from_neighbor_transform(
        particle_type_name: str,
        particle_position: np.ndarray,
        neighbor_type_name: str,
        neighbor_position: np.ndarray,
        neighbor_rotation_matrix: np.ndarray,
        zero_orientations: List[OrientationData],
        box_size: np.ndarray = np.array(3 * [np.inf]),
    ) -> np.ndarray:
        """
        Use the relative neighbor position and
        either the neighbor's rotation matrix or a random direction
        to calculate a rotation matrix
        """
        if neighbor_rotation_matrix is not None:
            # neighbor rotation matrix is set,
            # so try to use relative rotation matrix
            (
                neighbor_zero_orientation, # D
                n1_i,
                n2_i,
            ) = ParticleRotationCalculator._get_matching_zero_rotation_matrix(
                neighbor_type_name,
                [particle_type_name],
                zero_orientations,
                calculate_dependent_rotations=True,
            )
            if neighbor_zero_orientation is None:
                return None
            neighbor_index = 1 if n1_i is None else 0
            # raise Exception(neighbor_index)
            relative_rotation_matrix = (
                neighbor_zero_orientation.get_neighbor_relative_rotation_matrix(neighbor_index)
            )
            return np.matmul(neighbor_rotation_matrix, relative_rotation_matrix)
        else:
            # neighbor's rotation matrix is not set,
            # so calculate a random rotation matrix around the neighbor axis
            v1 = RotationUtility.normalize(
                RotationUtility.get_non_periodic_boundary_position(
                    neighbor_position - particle_position, box_size
                )
            )
            v2 = RotationUtility.get_random_perpendicular_vector(v1)
            return RotationUtility.get_rotation_matrix_from_bases(v1, v2)

    @staticmethod
    def _get_rotation_matrix_with_1_neighbor(
        particle_type_name: str,
        particle_position: np.ndarray,
        neighbor_type_name: str,
        neighbor_position: np.ndarray,
        neighbor_rotation_matrix: np.ndarray,
        zero_orientation: OrientationData,
        zero_orientations: List[OrientationData],
        box_size: np.ndarray,
    ) -> np.ndarray:
        """
        Get the current rotation matrix offset from the zero orientation
        for a particle with 1 neighbor
        """
        # raise Exception(zero_orientation.type_name_substrings)
        zero_rotation_matrix = RotationUtility.get_rotation_matrix_from_neighbor_positions(
            zero_orientation.get_neighbor_position(0),
            zero_orientation.get_neighbor_position(1),
            box_size,
        )
        current_rotation_matrix = (
            ParticleRotationCalculator._get_rotation_matrix_from_neighbor_transform(
                particle_type_name,
                particle_position,
                neighbor_type_name,
                neighbor_position,
                neighbor_rotation_matrix,
                zero_orientations,
                box_size,
            )
        )
        if zero_rotation_matrix is None or current_rotation_matrix is None:
            return None
        return np.matmul(current_rotation_matrix, np.linalg.inv(zero_rotation_matrix))

    @staticmethod
    def _get_rotation_matrix_with_2_neighbors(
        relative_neighbor1_position: np.ndarray,
        relative_neighbor2_position: np.ndarray,
        zero_orientation: OrientationData,
        box_size: np.ndarray,
    ) -> np.ndarray:
        """
        Get the current rotation matrix offset from the zero orientation
        for a particle with 2 neighbors
        """
        zero_rotation_matrix = RotationUtility.get_rotation_matrix_from_neighbor_positions(
            zero_orientation.get_neighbor_position(0),
            zero_orientation.get_neighbor_position(1),
            box_size,
        )
        current_rotation_matrix = RotationUtility.get_rotation_matrix_from_neighbor_positions(
            relative_neighbor1_position,
            relative_neighbor2_position,
            box_size,
        )
        if zero_rotation_matrix is None or current_rotation_matrix is None:
            # if zero_rotation is None:
            #     raise Exception("zero_rotation is None")
            # if current_rotation is None:
            #     raise Exception("current_rotation is None")
            return None
        return np.matmul(current_rotation_matrix, np.linalg.inv(zero_rotation_matrix))

    @staticmethod
    def _get_matching_zero_rotation_matrix(
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
                if zero_orientation.neighbor_type_name_matches(0, tn)
            ]
            if len(neighbor_type_names) == 1 and calculate_dependent_rotations:
                # if there's only one neighbor and
                # we've already calculated independent rotations
                if len(neighbor1_matches) > 0:
                    # use the first match
                    return zero_orientation, neighbor1_matches[0], None
                else:
                    # if no match in neighbor1 types, check in the neighbor2 types
                    neighbor2_matches = [
                        index
                        for index, tn in enumerate(neighbor_type_names)
                        if zero_orientation.neighbor_type_name_matches(1, tn)
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
                        if not zero_orientation.neighbor_type_name_matches(1, tn2):
                            continue
                        # use the first match
                        return zero_orientation, index1, index2
        print(
            f"Failed to find orientation data matching {particle_type_name} "
            f"with neighbors {neighbor_type_names}"
        )
        return None, None, None

    @staticmethod
    def calculate_rotation_matrix(
        particle_type_name: str,
        particle_position: np.ndarray,
        neighbor_type_names: List[str],
        neighbor_positions: List[np.ndarray],
        neighbor_rotation_matrices: List[np.ndarray],
        zero_orientations: List[OrientationData],
        box_size: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate the difference in the particle's current orientation
        compared to its zero orientation using neighbor positions and rotations.
        Return 3x3 rotation matrix

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
        neighbor_rotation_matrices: List[np.ndarray]
            The rotation matrices of the neighbors of the particle,
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
            # raise Exception("no neighbors")
            return None
        # find the zero rotation definition matching the particle type names
        (
            zero_orientation,
            neighbor1_index,
            neighbor2_index,
        ) = ParticleRotationCalculator._get_matching_zero_rotation_matrix(
            particle_type_name,
            neighbor_type_names,
            zero_orientations,
            neighbor_rotation_matrices is not None,
        )
        if zero_orientation is None:
            # raise Exception("didn't find matching zero orientation")
            return None
        if neighbor1_index is not None and neighbor2_index is not None:
            # try to get the rotation using the two neighbors' positions
            rotation_matrix = ParticleRotationCalculator._get_rotation_matrix_with_2_neighbors(
                neighbor_positions[neighbor1_index] - particle_position,
                neighbor_positions[neighbor2_index] - particle_position,
                zero_orientation,
                box_size,
            )
            if rotation_matrix is not None:
                return rotation_matrix
        # particle only has one neighbor or failed to get rotation with two neighbors
        if neighbor_rotation_matrices is None:
            # particles with one neighbor are dependent on neighbor rotations
            # raise Exception("one neighbor")
            return None
        neighbor_index = neighbor2_index if neighbor1_index is None else neighbor1_index
        return ParticleRotationCalculator._get_rotation_matrix_with_1_neighbor(
            particle_type_name,
            particle_position,
            neighbor_type_names[neighbor_index],
            neighbor_positions[neighbor_index],
            neighbor_rotation_matrices[neighbor_index],
            zero_orientation,
            zero_orientations,
            box_size,
        )

    @staticmethod
    def get_euler_angles_for_rotation_matrices(
        rotation_matrices: np.ndarray,
        n_agents: np.ndarray,
        result: np.ndarray,
    ) -> np.ndarray:
        """
        Get a set of euler angles in radians representing each rotation matrix.

        Parameters
        ----------
        """
        for time_index in range(n_agents.shape[0]):
            for agent_index in range(int(n_agents[time_index])):
                result[time_index][new_agent_index] = RotationUtility.get_euler_angles_for_rotation_matrix(rotation_matrices[time_index][agent_index])
        return result