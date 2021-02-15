#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging

from .custom_converter import CustomConverter

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class FileConverter(CustomConverter):
    def __init__(self, input_path: str):
        """
        This object loads the data in .simularium JSON format
        at the input path

        Parameters
        ----------
        input_path: str
            path to the .simularium JSON file to load
        """
        print("Reading Simularium JSON -------------")
        with open(input_path) as simularium_file:
            data = json.load(simularium_file)
        self._data = data
