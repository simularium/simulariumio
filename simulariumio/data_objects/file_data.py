#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from ..constants import DISPLAY_TYPE
from ..exceptions import DataError

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class FileData:
    file_path: str
    file_contents: str

    def __init__(
        self,
        file_path: str = "",
        file_contents: str = "",
    ):
        """
        This object contains info about a file of data

        Parameters
        ----------
        file_path: str (optional)
            A string path to the file
            Default: use file_contents instead
        file_contents: str (optional)
            A string of data from an opened file
            Default: use file_path instead
        """
        if not file_path and not file_contents:
            raise Exception(
                "Please provide either file_path or file_contents to create a FileData"
            )
        self.file_path = file_path
        self.file_contents = file_contents

    def get_data(self):
        """
        Return the data in the file.

        If file_contents is not empty, return that. 
        Otherwise try to open the file at file_path 
        and return the data inside as a string.
        """
        if self.file_contents:
            return self.file_contents
        with open(self.file_path, "r") as myfile:
            return myfile.read()
