#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, List, Any

import numpy as np

from ..exceptions import MissingDataError
from .reader import Reader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CustomTrajectoryReader(Reader):

    def _get_spatial_bundle_data_subpoints(
        self, 
        data: Dict[str, Any],
        type_ids: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Return the spatialData's bundleData for a simulation 
        of agents with subpoints, packing buffer with jagged data is slower
        """
        bundleData: List[Dict[str, Any]] = []

        for t in range(len(data['times'])):

            frame_data = {}
            frame_data['frameNumber'] = t
            frame_data['time'] = data['times'][t]
            n_agents = int(data['n_agents'][t])

            i = 0
            buffer_size = 10 * n_agents
            for n in range(n_agents): 
                buffer_size += 3 * len(data['subpoints'][t][n])
            local_buf = np.zeros(buffer_size)

            for n in range(n_agents): 

                local_buf[i] = data['viz_types'][t, n]
                local_buf[i + 1] = type_ids[t, n]
                local_buf[i + 2:i + 5] = data['positions'][t, n]
                local_buf[i + 8] = data['radii'][t, n]

                n_subpoints = len(data['subpoints'][t][n])
                if n_subpoints > 0:
                    subpoints = [3 * n_subpoints]
                    for p in range(n_subpoints):
                        for d in range(3):
                            subpoints.append(data['subpoints'][t][n][p][d])
                    local_buf[i + 9:i + 10 + 3 * n_subpoints] = subpoints
                    i += 10 + 3 * n_subpoints
                else:
                    local_buf[i + 9] = 0.0
                    i += 10

            frame_data['data'] = local_buf.tolist()
            bundleData.append(frame_data)

        return bundleData

    def _get_spatial_bundle_data_no_subpoints(
        self, 
        data: Dict[str, Any],
        type_ids: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Return the spatialData's bundleData for a simulation 
        of agents without subpoints, using list slicing for speed
        """
        bundleData: List[Dict[str, Any]] = []

        max_n_agents = int(np.amax(data['n_agents'], 0))
        ix_particles = np.empty((3 * max_n_agents,), dtype=int)
        for i in range(max_n_agents):
            ix_particles[3 * i:3 * i + 3] = np.arange(i * 10 + 2, i * 10 + 2 + 3)

        frame_buf = np.zeros(10 * max_n_agents)
        for t in range(len(data['times'])):
            
            frame_data = {}
            frame_data['frameNumber'] = t
            frame_data['time'] = data['times'][t]
            n = int(data['n_agents'][t])
            local_buf = frame_buf[:10 * n]
            local_buf[0::10] = data['viz_types'][t, :n]
            local_buf[1::10] = type_ids[t, :n]
            local_buf[ix_particles[:3 * n]] = data['positions'][t, :n].flatten()
            local_buf[8::10] = data['radii'][t, :n]
            frame_data['data'] = local_buf.tolist()
            bundleData.append(frame_data)

        return bundleData

    def read(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """

        if 'box_size' not in data:
            raise MissingDataError('box_size')
        if 'times' not in data:
            raise MissingDataError('times')
        if 'n_agents' not in data:
            raise MissingDataError('n_agents')
        if 'viz_types' not in data:
            raise MissingDataError('viz_types')
        if 'positions' not in data:
            raise MissingDataError('positions')
        if 'types' not in data:
            raise MissingDataError('types')
        if 'radii' not in data:
            raise MissingDataError('radii')

        simularium_data = {}

        # trajectory info
        totalSteps = len(data['times'])
        traj_info = {
            'version' : 1,
            'timeStepSize' : (data['times'][1] - data['times'][0] 
                              if totalSteps > 1 else 0),
            'totalSteps' : totalSteps,
            'size' : {
                'x' : data['box_size'][0],
                'y' : data['box_size'][1],
                'z' : data['box_size'][2]
            }
        }

        # generate a unique ID for each agent type
        type_ids = []
        type_id_mapping = {}
        k = 0
        for t in range(totalSteps):
            type_ids.append([])
            for i in range(len(data['types'][t])):
                agent_type = data['types'][t][i]
                if agent_type not in type_id_mapping:
                    type_id_mapping[agent_type] = k
                    traj_info[str(k)] = {'name' : agent_type}
                    k += 1
                type_ids[t].append(type_id_mapping[agent_type])
        type_ids = np.array(type_ids)
        traj_info['nAgentTypes'] = k

        simularium_data['trajectoryInfo'] = traj_info

        # spatial data
        spatialData = {
            'version' : 1,
            'msgType' : 1,
            'bundleStart' : 0,
            'bundleSize' : totalSteps
        }
        if 'subpoints' in data:
            spatialData['bundleData'] = self._get_spatial_bundle_data_subpoints(
                data, type_ids
            )
        else:
            spatialData['bundleData'] = self._get_spatial_bundle_data_no_subpoints(
                data, type_ids
            )
        simularium_data["spatialData"] = spatialData

        simularium_data['plotData'] = {
            'version' : 1,
            'data' : data['plots'] if 'plots' in data else {}
        }

        return simularium_data
