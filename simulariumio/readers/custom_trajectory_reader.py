#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any

import numpy as np

from .trajectory_reader import TrajectoryReader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CustomTrajectoryReader(TrajectoryReader):
    def read(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """
        simularium_data = {}

        # trajectory info
        totalSteps = len(data["times"])
        traj_info = {
            "version": 1,
            "timeStepSize": (
                float(data["times"][1] - data["times"][0]) if totalSteps > 1 else 0.0
            ),
            "totalSteps": totalSteps,
            "size": {
                "x": float(data["box_size"][0]),
                "y": float(data["box_size"][1]),
                "z": float(data["box_size"][2]),
            },
            "typeMapping": {},
        }

        # generate a unique type ID for each agent type
        type_ids = []
        type_id_mapping = {}
        k = 0
        for t in range(totalSteps):
            type_ids.append([])
            for i in range(len(data["types"][t])):
                agent_type = data["types"][t][i]
                if agent_type not in type_id_mapping:
                    type_id_mapping[agent_type] = k
                    traj_info["typeMapping"][str(k)] = {"name": agent_type}
                    k += 1
                type_ids[t].append(type_id_mapping[agent_type])
        data["type_ids"] = np.array(type_ids)

        simularium_data["trajectoryInfo"] = traj_info

        # spatial data
        spatialData = {
            "version": 1,
            "msgType": 1,
            "bundleStart": 0,
            "bundleSize": totalSteps,
        }
        if "subpoints" in data:
            spatialData["bundleData"] = self._get_spatial_bundle_data_subpoints(data)
        else:
            spatialData["bundleData"] = self._get_spatial_bundle_data_no_subpoints(data)
        simularium_data["spatialData"] = spatialData

        # plot data
        simularium_data["plotData"] = {
            "version": 1,
            "data": data["plots"] if "plots" in data else [],
        }

        return simularium_data
