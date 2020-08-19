#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Tuple

from .exceptions import UnsupportedSourceEngineError
from .readers import (
    CytosimReader,
    CustomReader,
)
from .readers.reader import Reader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################

SUPPORTED_READERS = {
    'custom' : CustomReader,
    'cytosim' : CytosimReader,
}

###############################################################################

# times, n_entities, positions, types, radii, output_path

class Converter:
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
            TODO
            Default: {}
        source_engine: string
            A string specifying which simulation engine created these outputs. Current options:
                'custom' : outputs are from an engine not specifically supported
                'cytosim' : outputs are from CytoSim (https://gitlab.com/f.nedelec/cytosim)
            Coming Soon:
                'readdy' : outputs are from ReaDDy (https://readdy.github.io/)
                'physicell' : outputs are from PhysiCell (http://physicell.org/)
        """
        self._data = data
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
    
    def write_JSON():
        """
        Convert the data to .simularium JSON format
        """
        # self._reader.data
        
        
