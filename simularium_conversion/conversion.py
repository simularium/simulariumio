#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Standard library
import logging
from typing import Any, Tuple

# Third party

# Relative

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class Converter(object):
    """
    This object converts simulation outputs from various engines (as well as custom data)
    into the JSON format used by the Simularium viewer.

    Parameters
    ----------
    source_engine: string
        A string specifying which simulation engine created these outputs. Current options:
            'custom' : outputs are from an engine not specifically supported
            'readdy' : outputs are from ReaDDy (https://readdy.github.io/)
            'cytosim' : outputs are from CytoSim (https://gitlab.com/f.nedelec/cytosim)
            'physicell' : outputs are from PhysiCell (http://physicell.org/)
    """

    @staticmethod
    def _convert_custom(self, val: Any):
        # TODO
    
    @staticmethod
    def _convert_readdy(self, val: Any):
        # TODO

    @staticmethod
    def _convert_cytosim(self, val: Any):
        # TODO

    @staticmethod
    def _convert_physicell(self, val: Any):
        # TODO

    @staticmethod
    def convert(val: Any):
        """
        Convert the provided data to Simularium JSON format according to the current source_engine
        """
        self.converter[source_engine](val)

    def __init__(self, source_engine: string = 'custom'):
        self.source_engine = source_engine
        self.converter = {
            'readdy': self._convert_readdy,
            'cytosim': self._convert_cytosim,
            'physicell' : self._convert_physicell,
            'custom' : self._convert_custom
        }
        
