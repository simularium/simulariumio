#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .reader import Reader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class CustomReader(Reader):
    """
    TODO
    
    Parameters
    ----------
    data: Dict[str, Any]
        TODO
        Default: {}
    """

    def __init__(self, data: Dict[str, Any] = {}):