#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class DisplayData:
    name: str
    radius: float
    display_type: str
    url: str
    color: str

    def __init__(
        self,
        name: str,
        radius: float = None,
        display_type: str = None,
        url: str = None,
        color: str = None,
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
        display_type: str (optional)
            the type of geometry to display
            Options: "SPHERE", "CUBE", "GIZMO", "FIBER", "PDB", or "OBJ"
            Default: "SPHERE" or "FIBER"
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
        return self.display_type is None and not self.url and not self.color

    def to_string(self):
        default = self.is_default()
        return (
            f"{self.display_type}: url={self.url}, color={self.color} "
            f"DEFAULT? {default}"
        )

    def __iter__(self):
        if self.display_type:
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