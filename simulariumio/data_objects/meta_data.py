#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import logging
from typing import Any, Dict

import numpy as np

from .camera_data import CameraData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MetaData:
    box_size: np.ndarray
    camera_defaults: CameraData
    scale_factor: float

    def __init__(
        self,
        box_size: np.ndarray,
        camera_defaults: CameraData = CameraData(),
        scale_factor: float = 1.0,
    ):
        """
        This object holds metadata for simulation trajectories

        Parameters
        ----------
        box_size : np.ndarray (shape = [3])
            A numpy ndarray containing the XYZ dimensions
            of the simulation bounding volume
        camera_defaults: CameraData (optional)
            camera's initial settings
            which it also returns to when reset
            Default: CameraData()
        scale_factor : float (optional)
            A multiplier for the scene, use if
            visualization is too large or small
            Default: 1.0
        """
        self.box_size = box_size
        self.camera_defaults = camera_defaults
        self.scale_factor = scale_factor

    @classmethod
    def from_buffer_data(cls, buffer_data: Dict[str, Any]):
        """ """
        return cls(
            box_size=np.array(
                [
                    float(buffer_data["trajectoryInfo"]["size"]["x"]),
                    float(buffer_data["trajectoryInfo"]["size"]["y"]),
                    float(buffer_data["trajectoryInfo"]["size"]["z"]),
                ]
            ),
            camera_defaults=CameraData.from_buffer_data(buffer_data),
        )

    def __deepcopy__(self, memo):
        result = type(self)(
            box_size=np.copy(self.box_size),
            camera_defaults=copy.deepcopy(self.camera_defaults, memo),
            scale_factor=self.scale_factor,
        )
        return result
