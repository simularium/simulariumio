#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from ..constants import DISPLAY_TYPE

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class DisplayData:
    display_type: str
    url: str
    color: str

    def __init__(
        self,
        display_type: str = DISPLAY_TYPE.DEFAULT,
        url: str = None,
        color: str = None,
    ):
        """
        This object contains data for displaying an agent

        Parameters
        ----------
        display_type: str (optional)
            the type of geometry to display
            Options: "DEFAULT", “SPHERE”, “CUBE”, “GIZMO”, “PDB”, or “OBJ”
            Default: "DEFAULT"
        url: str (optional)
            local path or web URL for the geometry file to display,
            web URLs are required for streaming
            or loading the trajectory by URL
            Default: None
        color: str (optional)
            the hex value for the color to display, e.g "#FFFFFF"
            Default: Use default colors from Simularium Viewer
        """
        self.display_type = display_type
        self.url = url
        if color is not None and (
            (len(color) != 4 and len(color) != 7) or color[0] != "#"
        ):
            raise Exception(f"{color} should be provided as '#xxxxxx'")
        self.color = color

    def is_default(self):
        """
        Check if this DisplayData is only holding default data
        """
        return self.display_type == "DEFAULT" and not self.url and not self.color

    def __iter__(self):
        yield "displayType", self.display_type
        if self.url:
            yield "url", self.url
        if self.color:
            yield "color", self.color

    def __copy__(self):
        result = type(self)(
            display_type=self.display_type,
            url=self.url,
            color=self.color,
        )
        return result
