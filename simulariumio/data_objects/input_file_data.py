#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from ..exceptions import DataError
from ..constants import BINARY_SETTINGS

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class InputFileData:
    file_path: str
    file_contents: str

    def __init__(
        self,
        file_path: str = "",
        file_contents: str = "", # we also want bytes, so maybe? | bytes = b'',
    ):
        """
        This object contains data about a file

        Parameters
        ----------
        file_path: str (optional)
            A string path to the file
            Default: use file_contents instead
        file_contents: str (optional) or bytes (optional)
            A string of data from an opened file
            Default: use file_path instead
        """
        if not file_path and not file_contents:
            raise DataError(
                "Please provide either file_path or file_contents "
                "to create an InputFileData"
            )
        self.file_path = file_path
        self.file_contents = file_contents

    def get_contents(self):
        """
        Return the contents of the file.

        If file_contents is not empty, return that.
        Otherwise try to open the file at file_path
        and return the data inside as a string.
        """
        if self.file_contents:
            return self.file_contents
        with open(self.file_path, "r") as myfile:
            return myfile.read()  # only works for JSON files right now, maybe use SimulariumBinaryReader._binary_data_from_file()?

    def _is_binary(self):
        """
        Is this data in binary? (or JSON?)
        """
        if self.file_contents:
            # check file contents string to see if they're binary
            header = self.file_contents[0:len(BINARY_SETTINGS.FILE_IDENTIFIER)]
            if header.decode("utf-8") == BINARY_SETTINGS.FILE_IDENTIFIER:
                return True
        with open(self.file_path, "rb") as open_file:
            # need to be able to do this check with a binary blob rather than just file
            header = open_file.read(len(BINARY_SETTINGS.FILE_IDENTIFIER)).decode(
                "utf-8"
            )
            if header == BINARY_SETTINGS.FILE_IDENTIFIER:
                return True
        return False
