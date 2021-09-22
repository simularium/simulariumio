#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

from ..constants import DISPLAY_TYPE
from ..exceptions import DataError

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class DisplayData:
    name: str
    radius: float
    display_type: DISPLAY_TYPE
    url: str
    color: str

    def __init__(
        self,
        name: str,
        radius: float = None,
        display_type: DISPLAY_TYPE = DISPLAY_TYPE.NONE,
        url: str = "",
        color: str = "",
    ):
        """
        This object contains info about how to display an agent

        Parameters
        ----------
        name : str
            A string display name for this type of agent
            Default: use names from simulator data if possible
        radius : float (optional)
            A float radius for rendering this agent.
            For fibers, this is the thickness of the line
            For default agents, this is the scale of the representation
            Default : 1.0
        display_type: DISPLAY_TYPE (optional)
            the type of geometry to display
            Options: SPHERE, FIBER, PDB, or OBJ
            Default: If not specified, the Simularium Viewer
                defaults to SPHERE or FIBER depending on
                the viz type of each agent
        url: str (optional)
            local path or web URL for the geometry file to display,
            web URLs are required for streaming
            or loading the trajectory by URL
            Default: None
        color: str (optional)
            the hex value for the color to display, e.g "#FFFFFF"
            Default: Use default colors from Simularium Viewer
        """
        self.name = name
        # radius defaults to None here so that later,
        # when it's used to override radius in data,
        # it's easy to test whether the user has specified it
        self.radius = radius
        if not isinstance(display_type, DISPLAY_TYPE):
            raise DataError(
                f"In {name}'s DisplayData, display_type is {type(display_type)}"
                " instead of DISPLAY_TYPE"
            )
        self.display_type = display_type
        self.url = url
        if color and ((len(color) != 4 and len(color) != 7) or color[0] != "#"):
            raise DataError(f"{color} should be provided as '#xxxxxx' or '#xxx'")
        self.color = color

    def is_default(self):
        """
        Check if this DisplayData is only holding default data
        """
        return (
            self.display_type == DISPLAY_TYPE.NONE and not self.url and not self.color
        )

    def to_string(self):
        return (
            f"{self.display_type.value}: url={self.url}, color={self.color} "
            f"is_default? {self.is_default()}"
        )

    def __iter__(self):
        if self.display_type != DISPLAY_TYPE.NONE:
            yield "displayType", self.display_type.value
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
