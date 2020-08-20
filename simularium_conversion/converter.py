#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Tuple

from .exceptions import UnsupportedSourceEngineError
from .readers import (
    CustomReader,
)
from .readers.reader import Reader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################

SUPPORTED_READERS = {
    'custom' : CustomReader,
}

###############################################################################


class Converter:
    _reader: Reader = None

    def __init__(
        self,
        data: Dict[str, Any] = {}, 
        source_engine: string = 'custom'
    ):
        """
        This object reads simulation outputs from various engines (as well as custom data)
        and writes it in the JSON format used by the Simularium viewer

        Parameters
        ----------
        data: Dict[str, Any]
            Loaded data or path to data from a simulation engine. Fields for each engine:

                custom: 
                    times: np.ndarray (shape = [timesteps])
                        A numpy ndarray containing the elapsed simulated time at each timestep
                    max_n_agents: number
                        The maximum number of agents that exist at any one timestep
                    positions : np.ndarray (shape = [timesteps, agents, 3])
                        A numpy ndarray containing the XYZ position for each agent at each timestep
                    types: List[str] (list of shape [timesteps, agents])
                        A list containing the string name for the type of each agent at each timestep
                    radii : np.ndarray (shape = [timesteps, agents])
                        A numpy ndarray containing the radius for each agent at each timestep

            Default: {}

        source_engine: string
            A string specifying which simulation engine created these outputs. Current options:
                'custom' : outputs are from an engine not specifically supported
            Coming Soon:
                'cytosim' : outputs are from CytoSim (https://gitlab.com/f.nedelec/cytosim)
                'readdy' : outputs are from ReaDDy (https://readdy.github.io/)
                'physicell' : outputs are from PhysiCell (http://physicell.org/)
        """
        reader_class = self.determine_reader(source_engine=source_engine)
        self._reader = reader_class(data)

    @staticmethod
    def determine_reader(source_engine: string = 'custom') -> Type[Reader]:
        """
        Return the reader to match the requested source simulation engine
        """
        if source_engine in SUPPORTED_READERS:
            return SUPPORTED_READERS[source_engine]

        raise UnsupportedSourceEngineError(source_engine)
    
    def write_JSON(self, output_path: str):
        """
        Convert the data to .simularium JSON format and save it at the output path

        Parameters
        ----------
        output_path: str
            where to save the .simularium JSON file
        """
        _data = self._reader.data

        # generate a unique ID for each type
        type_ids = []
        type_id_mapping = {}
        k = 0
        for t in range(len(_data.times)):
            type_ids.append([])
            for i in range(len(_data.types[t])):
                if _data.types[t][i] not in type_id_mapping:
                    type_id_mapping[_data.types[t][i]] = k
                    k += 1
                type_ids[t].append(type_id_mapping[_data.types[t][i]])
        type_ids = np.array(type_ids)
        
        # pack the JSON data
        frame_buf = np.zeros((_data.max_n_agents * 10, ))
        frame_buf[::10] = 1000  # vis type
        data = {}
        data['msgType'] = 1
        data['bundleStart'] = 0
        data['bundleSize'] = len(_data.times)
        data['bundleData'] = []
        ix_particles = np.empty((3*_data.max_n_agents,), dtype=int)

        for i in range(_data.max_n_agents):
            ix_particles[3*i:3*i+3] = np.arange(i*10 + 2, i*10 + 2+3)

        for t in range(len(_data.times)):
            frame_data = {}
            frame_data['frameNumber'] = t
            frame_data['time'] = _data.times[t]
            n = int(n_entities[t])
            local_buf = frame_buf[:10*n]
            local_buf[1::10] = type_ids[t, :n]
            local_buf[ix_particles[:3*n]] = _data.positions[t, :n].flatten()
            local_buf[8::10] = _data.radii[t, :n]
            frame_data['data'] = local_buf.tolist()
            data['bundleData'].append(frame_data)

        # save to output path
        with open("{}.simularium".format(output_path), 'w+') as outfile:
            json.dump(data, outfile)
        
        
