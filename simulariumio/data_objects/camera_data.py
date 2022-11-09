#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict

import numpy as np

from ..constants import DEFAULT_CAMERA_SETTINGS

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CameraData:
    position: np.ndarray
    look_at_position: np.ndarray
    up_vector: np.ndarray
    fov_degrees: float

    def __init__(
        self,
        position: np.ndarray = np.array(DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION),
        look_at_position: np.ndarray = np.array(
            DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION
        ),
        up_vector: np.ndarray = np.array(DEFAULT_CAMERA_SETTINGS.UP_VECTOR),
        fov_degrees: float = np.array(DEFAULT_CAMERA_SETTINGS.FOV_DEGREES),
    ):
        """
        This object holds parameters that define
        a camera view of the 3D scene

        Parameters
        ----------
        position : np.ndarray (shape = [3]) (optional)
            3D position of the camera itself
            Default: np.array([0.0, 0.0, 120.0])
        look_at_position : np.ndarray (shape = [3]) (optional)
            position the camera looks at
            Default: np.zeros(3)
        up_vector : np.ndarray (shape = [3]) (optional)
            the vector that defines which direction
            is "up" in the camera's view
            Default: np.array([0.0, 1.0, 0.0])
        fov_degrees : float (optional)
            the angle defining the extent of the 3D world
            that is seen from bottom to top of the camera view
            Default: 75.0
        """
        self.position = position
        self.look_at_position = look_at_position
        self.up_vector = up_vector
        self.fov_degrees = fov_degrees

    @classmethod
    def from_dict(cls, buffer_data: Dict[str, Any]):
        """ """
        camera_default = buffer_data.get("cameraDefault")
        if camera_default is None:
            return cls()
        return cls(
            position=CameraData._unpack_position_vector(
                camera_default["position"],
                DEFAULT_CAMERA_SETTINGS.CAMERA_POSITION
            ),
            look_at_position=CameraData._unpack_position_vector(
                camera_default["lookAtPosition"],
                DEFAULT_CAMERA_SETTINGS.LOOK_AT_POSITION
            ),
            up_vector=CameraData._unpack_position_vector(
                camera_default["upVector"],
                DEFAULT_CAMERA_SETTINGS.UP_VECTOR
            ),
            fov_degrees=float(
                camera_default.get("fovDegrees", DEFAULT_CAMERA_SETTINGS.FOV_DEGREES)
            ),
        )

    def __deepcopy__(self, memo):
        result = type(self)(
            position=np.copy(self.position),
            look_at_position=np.copy(self.look_at_position),
            up_vector=np.copy(self.up_vector),
            fov_degrees=self.fov_degrees,
        )
        return result

    @staticmethod
    def _unpack_position_vector(
        vector_dict: Dict[str, str], defaults: np.ndarray
    ) -> np.ndarray:
        # if no vector information was given, go with the defaults
        if vector_dict is None:
            return defaults

        # use all positions given, but use defaults if any are missing
        return np.array(
            [
                float(vector_dict.get("x", defaults[0])),
                float(vector_dict.get("y", defaults[1])),
                float(vector_dict.get("z", defaults[2])),
            ]
        )
