#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict

import numpy as np

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MetaData:
    box_size: np.ndarray
    default_camera_position: np.ndarray
    default_camera_rotation: np.ndarray
    scale_factor: float

    def __init__(
        self,
        box_size: np.ndarray,
        default_camera_position: np.ndarray = np.array([0.0, 0.0, 120.0]),
        default_camera_rotation: np.ndarray = np.zeros(3),
        scale_factor: float = 1.0,
    ):
        """
        This object holds metadata for simulation trajectories

        Parameters
        ----------
        box_size : np.ndarray (shape = [3])
            A numpy ndarray containing the XYZ dimensions
            of the simulation bounding volume
        default_camera_position: np.ndarray (optional)
            camera's initial position
            which it also returns to when reset
            Default: np.array([0.0, 0.0, 120.0])
        default_camera_rotation: np.ndarray (optional)
            camera's initial rotation
            which it also returns to when reset
            Default: np.zeros(3)
        scale_factor : float (optional)
            A multiplier for the Cytosim scene, use if
            visualization is too large or small
            Default: 1.0
        """
        self.box_size = box_size
        self.default_camera_position = default_camera_position
        self.default_camera_rotation = default_camera_rotation
        self.scale_factor = scale_factor

    @classmethod
    def from_buffer_data(cls, buffer_data: Dict[str, Any]):
        """"""
        return cls(
            box_size=np.array(
                [
                    float(buffer_data["trajectoryInfo"]["size"]["x"]),
                    float(buffer_data["trajectoryInfo"]["size"]["y"]),
                    float(buffer_data["trajectoryInfo"]["size"]["z"]),
                ]
            ),
            default_camera_position=np.array(
                [
                    float(
                        buffer_data["trajectoryInfo"]["cameraDefault"]["position"]["x"]
                    ),
                    float(
                        buffer_data["trajectoryInfo"]["cameraDefault"]["position"]["y"]
                    ),
                    float(
                        buffer_data["trajectoryInfo"]["cameraDefault"]["position"]["z"]
                    ),
                ]
            ),
            default_camera_rotation=np.array(
                [
                    float(
                        buffer_data["trajectoryInfo"]["cameraDefault"]["rotation"]["x"]
                    ),
                    float(
                        buffer_data["trajectoryInfo"]["cameraDefault"]["rotation"]["y"]
                    ),
                    float(
                        buffer_data["trajectoryInfo"]["cameraDefault"]["rotation"]["z"]
                    ),
                ]
            ),
        )
