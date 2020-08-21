#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any

from ..exceptions import MissingDataError
from .reader import Reader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class HistogramPlotReader(Reader):

    def read(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """

        if 'title' not in data:
            raise MissingDataError('title')
        if 'xaxis_title' not in data:
            raise MissingDataError('xaxis_title')
        if 'traces' not in data:
            raise MissingDataError('traces')

        simularium_data = {}

        # layout info
        simularium_data['layout'] = {
            'title' : data['title'],
            'xaxis' : {
                'title' : data['xaxis_title']
            },
            'yaxis' : {
                'title' : 'frequency'
            }
        }

        # plot data
        simularium_data['data'] = []
        for trace_name in data['traces']:
            simularium_data['data'] += {
                'name' : trace_name,
                'type' : 'histogram',
                'x' : data['traces'][trace_name]
            }

        return simularium_data
