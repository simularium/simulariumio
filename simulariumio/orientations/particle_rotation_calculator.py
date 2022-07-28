#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import annotations
import logging
from typing import List, Dict, Tuple

import numpy as np

from .orientation_data import OrientationData
from .rotation_utility import RotationUtility

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class ParticleRotationCalculator:
    type_name: str
    position: np.ndarray
    neighbor_ids: List[int]
    neighbor_type_names: List[str]
    neighbor_positions: List[np.ndarray]
    neighbor1_index: int
    neighbor2_index: int
    zero_orientation: OrientationData
    box_size: np.ndarray

    def __init__(
        self,
        type_name: str,
        position: np.ndarray,
        neighbor_ids: List[int],
        neighbor_type_names: List[str],
        neighbor_positions: List[np.ndarray],
        zero_orientations: List[OrientationData],
        box_size: np.ndarray,
    ):
        """
        This object stores particle instance data needed
        to calculate rotations from neighbor positions and rotations.
        On init, it attempts to calculate rotation from two neighbors.
        Use calculate_dependent_rotation() to calculate rotation
        based on one neighbor if initial attempt failed.

        Parameters
        ----------
        type_name: str
            The type name of the particle
        position: np.ndarray
            The position of the particle
        neighbor_ids: List[int]
            The ids of the neighbors of the particle
        neighbor_type_names: List[str]
            The type names of the neighbors of the particle
        neighbor_positions: List[np.ndarray]
            The positions of the neighbors of the particle,
            in the same order as the type names
        zero_orientations: List[OrientationData]
            A list of possible zero orientation definitions
        box_size: np.ndarray (shape = [3])
            The size of the reaction volume in X, Y, and Z
        """
        self.type_name = type_name
        self.position = position
        self.neighbor_ids = neighbor_ids
        self.neighbor_type_names = neighbor_type_names
        self.neighbor_positions = neighbor_positions
        self.zero_orientations = zero_orientations
        self.box_size = box_size
        self.zero_orientation = None
        self.neighbor_index = -1
        self.neighbor1_index = -1
        self.neighbor2_index = -1
        self.zero_rot_matrix = None
        self.current_rot_matrix = None
        if len(self.neighbor_ids) > 1:
            # attempt to calculate rotation from two neighbors
            if self._match_orientation_data_with_two_neighbors():
                self._calculate_zero_rot_matrix()
                self._calculate_current_rot_matrix_with_two_neighbors()
        elif len(self.neighbor_ids) == 0:
            # calculate a random rotation
            self.current_rot_matrix = RotationUtility.get_random_rotation_matrix()

    def _match_orientation_data_with_two_neighbors(self) -> bool:
        """
        Set the matching orientation data
        for the particle and neighbors of the given types
        """
        # check through the orientations
        for orientation in self.zero_orientations:
            if not orientation.type_name_matches(self.type_name):
                # this orientation is not for this type of particle
                continue
            # get all the matches with the neighbor1 types
            neighbor1_matches = [
                index
                for index, tn in enumerate(self.neighbor_type_names)
                if orientation.neighbor_type_name_matches(0, tn)
            ]
            # check if another neighbor matches neighbor2 type
            for index1 in neighbor1_matches:
                for index2, tn2 in enumerate(self.neighbor_type_names):
                    if index2 == index1:
                        continue
                    if not orientation.neighbor_type_name_matches(1, tn2):
                        continue
                    # use the first match
                    self.zero_orientation = orientation
                    self.neighbor1_index = index1
                    self.neighbor2_index = index2
                    return True
        return False

    def _calculate_zero_rot_matrix(self):
        """
        Calculate the zero orientation rotation matrix
        """
        self.zero_rot_matrix = (
            RotationUtility.get_rotation_matrix_from_neighbor_positions(
                self.zero_orientation.get_neighbor_position(0),
                self.zero_orientation.get_neighbor_position(1),
                self.box_size,
            )
        )

    def _calculate_current_rot_matrix_with_two_neighbors(self):
        """
        Calculate the current rotation matrix for a particle with 2 neighbors
        """
        self.current_rot_matrix = (
            RotationUtility.get_rotation_matrix_from_neighbor_positions(
                self.neighbor_positions[self.neighbor1_index] - self.position,
                self.neighbor_positions[self.neighbor2_index] - self.position,
                self.box_size,
            )
        )

    def _calculate_current_rot_matrix_with_neighbor_rot(
        self, neighbor_rot_calculator: ParticleRotationCalculator
    ):
        """
        Use the neighbor's rotation matrix and the rotation offset
        from the orientation data to calculate the current rotation matrix
        """
        neighbor_type_name = self.neighbor_type_names[self.neighbor_index]
        (
            neighbor_zero_orientation,
            index1,
            _,
        ) = self._match_orientation_data_with_one_neighbor(
            neighbor_type_name, [self.type_name]
        )
        if neighbor_zero_orientation is None:
            # failed to find orientation data for neighbor using this particle
            return
        relative_rotation_matrix = (
            neighbor_zero_orientation.get_neighbor_relative_rotation_matrix(
                1 if index1 < 0 else 0
            )
        )
        if relative_rotation_matrix is not None:
            self.current_rot_matrix = np.matmul(
                np.matmul(
                    neighbor_rot_calculator._get_offset_rot_matrix(),
                    relative_rotation_matrix,
                ),
                self.zero_rot_matrix,
            )

    def _calculate_current_rot_matrix_randomly_from_neighbor(self):
        """
        Use the relative neighbor position and a random direction
        to calculate a rotation matrix
        """
        neighbor_position = self.neighbor_positions[self.neighbor_index]
        v1 = RotationUtility.normalize(
            RotationUtility.get_non_periodic_boundary_position(
                neighbor_position - self.position, self.box_size
            )
        )
        v2 = RotationUtility.get_random_perpendicular_vector(v1)
        self.current_rot_matrix = RotationUtility.get_rotation_matrix_from_bases(v1, v2)

    def _match_orientation_data_with_one_neighbor(
        self,
        particle_type_name: str,
        neighbor_type_names: List[str],
    ) -> Tuple[OrientationData, int, int]:
        """
        Set the matching orientation data
        for the particle and neighbor of the given type
        """
        # check through the orientations
        for orientation in self.zero_orientations:
            if not orientation.type_name_matches(particle_type_name):
                # this orientation is not for this type of particle
                continue
            # get all the matches with the neighbor1 types
            neighbor1_matches = [
                index
                for index, tn in enumerate(neighbor_type_names)
                if orientation.neighbor_type_name_matches(0, tn)
            ]
            if len(neighbor1_matches) > 0:
                # use the first match
                return orientation, neighbor1_matches[0], -1
            else:
                # if no match in neighbor1 types, check in the neighbor2 types
                neighbor2_matches = [
                    index
                    for index, tn in enumerate(neighbor_type_names)
                    if orientation.neighbor_type_name_matches(1, tn)
                ]
                if len(neighbor2_matches) > 0:
                    # use the first match
                    return orientation, -1, neighbor2_matches[0]
        return None, -1, -1

    def calculate_dependent_rotation(
        self, other_rotation_data: Dict[int, ParticleRotationCalculator]
    ):
        """
        If the current rotation matrix was not already set,
        try to set it relative to a neighbor's rotation or position

        Parameters
        ----------
        other_rotation_data: Dict[int, ParticleRotationCalculator]
            A dict mapping particle id to ParticleRotationCalculator
            for all the particles at the current timestep
        """
        if self.current_rot_matrix is not None:
            # rotation was already calculated from two neighbors
            return
        (
            self.zero_orientation,
            index1,
            index2,
        ) = self._match_orientation_data_with_one_neighbor(
            self.type_name, self.neighbor_type_names
        )
        if self.zero_orientation is None:
            print(
                f"Rotation calculation failed for {self.type_name}: "
                f"couldn't find matching neighbor in {self.neighbor_type_names}"
            )
            return
        self._calculate_zero_rot_matrix()
        self.neighbor_index = index2 if index1 < 0 else index1
        # get the neighbor's current rotation matrix
        neighbor_id = self.neighbor_ids[self.neighbor_index]
        neighbor_rot_calculator = other_rotation_data[neighbor_id]
        if neighbor_rot_calculator.current_rot_matrix is not None:
            # neighbor rotation matrix is set,
            # so try to use relative rotation matrix
            self._calculate_current_rot_matrix_with_neighbor_rot(
                neighbor_rot_calculator
            )
            if self.current_rot_matrix is None:
                neighbor_type_name = self.neighbor_type_names[self.neighbor_index]
                print(
                    f"Rotation calculation failed for {self.type_name}: "
                    f"neighbor {neighbor_type_name} couldn't find match"
                )
        else:
            # neighbor's rotation matrix is not set,
            # so calculate a random rotation matrix around the neighbor axis
            self._calculate_current_rot_matrix_randomly_from_neighbor()

    def _get_offset_rot_matrix(self) -> np.ndarray:
        """
        Get the current rotation matrix offset from the zero orientation
        """
        # return self.current_rot_matrix
        if self.zero_rot_matrix is None or self.current_rot_matrix is None:
            return None
        return np.matmul(self.current_rot_matrix, np.linalg.inv(self.zero_rot_matrix))

    def get_euler_angles(self) -> np.ndarray:
        """
        Calculate euler angles that represent the current rotation
        """
        return RotationUtility.get_euler_angles_for_rotation_matrix(
            self._get_offset_rot_matrix()
        )
