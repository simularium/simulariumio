#!/usr/bin/env python
# -*- coding: utf-8 -*-

from simularium_conversion.exceptions import MissingDataError
from .reader import Reader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CustomReader(Reader):

    def _read(self, data: Dict[str, Any]) -> SimulariumData:

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
        
        return SimulariumData(
            data['times'],
            data['max_n_agents'],
            data['positions'],
            data['types'],
            data['radii']
        )
