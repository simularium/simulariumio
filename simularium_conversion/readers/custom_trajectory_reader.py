#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any

from ..exceptions import MissingDataError
from .reader import Reader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CustomTrajectoryReader(Reader):
    
    def get_spatial_bundle_data_with_subpoints(
        self, 
        data: Dict[str, Any],
        type_ids: np.ndarray
    ) -> List[Dict[str,Any]]:
        """
        Return the spatialData's bundleData for a simulation 
        of agents with subpoints, packing buffer with jagged data is slower
        """
        # TODO
    
    def get_spatial_bundle_data_without_subpoints(
        self, 
        data: Dict[str, Any],
        type_ids: np.ndarray
    ) -> List[Dict[str,Any]]:
        """
        Return the spatialData's bundleData for a simulation 
        of agents without subpoints, using list slicing for speed
        """
        bundleData: List[Dict[str,Any]] = []

        ix_particles = np.empty((3*data['max_n_agents'],), dtype=int)
        for i in range(data['max_n_agents']):
            ix_particles[3*i:3*i+3] = np.arange(i*10 + 2, i*10 + 2+3)

        frame_buf = np.zeros((data['max_n_agents'] * 10, ))
        frame_buf[::10] = 1000  # vis type
        for t in range(len(data['times'])):
            frame_data = {}
            frame_data['frameNumber'] = t
            frame_data['time'] = data['times'][t]
            n = int(n_entities[t])
            local_buf = frame_buf[:10*n]
            local_buf[1::10] = type_ids[t, :n]
            local_buf[ix_particles[:3*n]] = data['positions'][t, :n].flatten()
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
        if 'max_n_agents' not in data:
            raise MissingDataError('max_n_agents')
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
            'timeStepSize' : data['times'][1] - data['times'][0] if totalSteps > 1 else 0,
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
                    traj_info[k] = { 'name' : agent_type }
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
        has_subpoints = False
        if 'subpoints' in data:
            for t in range(len(data['subpoints'])):
                if len(data['subpoints'][t]) > 0:
                    has_subpoints = True
                    break
        if has_subpoints:
            spatialData['bundleData'] = get_spatial_bundle_data_with_subpoints(data, type_ids)
        else:
            spatialData['bundleData'] = get_spatial_bundle_data_without_subpoints(data, type_ids)
        simularium_data["spatialData"] = spatialData

        simularium_data['plotData'] = {
            'version' : 1,
            'data' : data['plots'] if 'plots' in data else {}
        }

        return simularium_data
        