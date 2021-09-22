#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import logging
from typing import Any, Dict

import numpy as np

from .camera_data import CameraData
from .model_meta_data import ModelMetaData
from ..constants import DEFAULT_BOX_SIZE

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class MetaData:
    box_size: np.ndarray
    camera_defaults: CameraData
    scale_factor: float
    trajectory_title: str
    model_meta_data: ModelMetaData

    def __init__(
        self,
        box_size: np.ndarray = None,
        camera_defaults: CameraData = None,
        scale_factor: float = 1.0,
        trajectory_title: str = "",
        model_meta_data: ModelMetaData = None,
    ):
        """
        This object holds metadata for simulation trajectories

        Parameters
        ----------
        box_size : np.ndarray (shape = [3]) (optional)
            A numpy ndarray containing the XYZ dimensions
            of the simulation bounding volume
            Default: np.array([100, 100, 100])
        camera_defaults: CameraData (optional)
            camera's initial settings
            which it also returns to when reset
            Default: CameraData()
        scale_factor : float (optional)
            A multiplier for the scene, use if
            visualization is too large or small
            Default: 1.0
        trajectory_title : str (optional)
            A title for this run of the model
        model_meta_data: ModelMetaData (optional)
            Metadata for the model that produced this trajectory
        """
        # box_size defaults to None here so that later,
        # when it's used to override box_size in data,
        # it's easy to test whether the user has specified it
        self.box_size = box_size
        self.camera_defaults = (
            camera_defaults if camera_defaults is not None else CameraData()
        )
        self.scale_factor = scale_factor
        self.trajectory_title = trajectory_title
        self.model_meta_data = (
            model_meta_data if model_meta_data is not None else ModelMetaData()
        )

    @classmethod
    def from_buffer_data(cls, buffer_data: Dict[str, Any]):
        """
        Create MetaData from a simularium JSON dict containing buffers
        """
        return cls(
            box_size=np.array(
                [
                    float(buffer_data["trajectoryInfo"]["size"]["x"]),
                    float(buffer_data["trajectoryInfo"]["size"]["y"]),
                    float(buffer_data["trajectoryInfo"]["size"]["z"]),
                ]
            ),
            camera_defaults=CameraData.from_buffer_data(buffer_data),
            trajectory_title=buffer_data["trajectoryInfo"]["trajectoryTitle"]
            if "trajectoryTitle" in buffer_data["trajectoryInfo"]
            else "",
            model_meta_data=ModelMetaData.from_buffer_data(buffer_data),
        )

    def _set_box_size(self, box_size: np.ndarray = None):
        """
        Set the box_size to the optional provided override value,
        or to the default value if it is currently None.
        If it's not set to the default value, multiply it by the scale_factor
        """
        if self.box_size is None:
            if box_size is not None:
                self.box_size = box_size * self.scale_factor
            else:
                self.box_size = DEFAULT_BOX_SIZE
        else:
            self.box_size *= self.scale_factor

    def __deepcopy__(self, memo):
        result = type(self)(
            box_size=np.copy(self.box_size),
            camera_defaults=copy.deepcopy(self.camera_defaults, memo),
            scale_factor=self.scale_factor,
            trajectory_title=self.trajectory_title,
            model_meta_data=copy.copy(self.model_meta_data),
        )
        return result
