#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict

import numpy as np

from .converter import Converter
from .data_objects import CustomData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CustomConverter(Converter):
    def __init__(self, input_data: CustomData):
        """
        This object reads custom simulation trajectory outputs
        and plot data and writes them in the JSON format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : CustomData
            An object containing custom simulation trajectory outputs
            and plot data
        """
        self._data = self._read(input_data)
        self._check_agent_ids_are_unique_per_frame()

    def _read(self, input_data: CustomData) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """
        simularium_data = {}
        # trajectory info
        totalSteps = len(input_data.agent_data.times)
        traj_info = {
            "version": 1,
            "timeStepSize": (
                float(input_data.agent_data.times[1] - input_data.agent_data.times[0])
                if totalSteps > 1
                else 0.0
            ),
            "totalSteps": totalSteps,
            "size": {
                "x": float(input_data.box_size[0]),
                "y": float(input_data.box_size[1]),
                "z": float(input_data.box_size[2]),
            },
            "typeMapping": {},
        }
        # generate a unique type ID for each agent type
        type_ids = []
        type_id_mapping = {}
        k = 0
        for t in range(totalSteps):
            type_ids.append([])
            for i in range(len(input_data.agent_data.types[t])):
                agent_type = input_data.agent_data.types[t][i]
                if agent_type not in type_id_mapping:
                    type_id_mapping[agent_type] = k
                    traj_info["typeMapping"][str(k)] = {"name": agent_type}
                    k += 1
                type_ids[t].append(type_id_mapping[agent_type])
        input_data.agent_data.type_ids = np.array(type_ids)
        simularium_data["trajectoryInfo"] = traj_info
        # spatial data
        spatialData = {
            "version": 1,
            "msgType": 1,
            "bundleStart": 0,
            "bundleSize": totalSteps,
        }
        if input_data.agent_data.subpoints is not None:
            spatialData["bundleData"] = self._get_spatial_bundle_data_subpoints(
                input_data.agent_data
            )
        else:
            spatialData["bundleData"] = self._get_spatial_bundle_data_no_subpoints(
                input_data.agent_data
            )
        simularium_data["spatialData"] = spatialData
        # plot data
        simularium_data["plotData"] = {
            "version": 1,
            "data": input_data.plots,
        }
        return simularium_data
