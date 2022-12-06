#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Any, Dict

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
        display_type: DISPLAY_TYPE,
        radius: float = None,
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
        display_type: DISPLAY_TYPE
            the type of geometry to display
            Options: SPHERE, FIBER, PDB, OBJ, or SPHERE_GROUP
        radius : float (optional)
            A float radius for rendering this agent.
            For fibers, this is the thickness of the line
            For default agents, this is the scale of the representation
            Default : 1.0
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
            try:
                display_type = DISPLAY_TYPE[display_type]
            except KeyError:
                raise DataError(
                    f"In {name}'s DisplayData, {display_type} is not a display type, "
                    'try "SPHERE" or see DISPLAY_TYPE documentation for other options.'
                )
        self.display_type = display_type
        self.url = url
        if color and ((len(color) != 4 and len(color) != 7) or color[0] != "#"):
            raise DataError(f"{color} should be provided as '#xxxxxx' or '#xxx'")
        self.color = color

    @classmethod
    def from_dict(
        cls,
        display_info: Dict[str, Any],
        default_display_type: DISPLAY_TYPE = DISPLAY_TYPE.SPHERE
    ):
        """
        Create DisplayData from a simularium JSON dict containing buffers.
        """
        if display_info is None:
            return cls(name="")
        return cls(
            name=display_info.get("name", "[No name]"),
            radius=float(display_info.get("radius", 1.0)),
            display_type=display_info.get("displayType", default_display_type),
            url=display_info.get("url", ""),
            color=display_info.get("color", ""),
        )

    def __str__(self):
        return (
            f"{self.name}: display_type={self.display_type.value}, "
            f"url={self.url}, color={self.color} "
        )

    def __iter__(self):
        yield "displayType", self.display_type.value
        if self.url:
            yield "url", self.url
        if self.color:
            yield "color", self.color

    def __copy__(self):
        result = type(self)(
            name=self.name,
            radius=self.radius,
            display_type=self.display_type,
            url=self.url,
            color=self.color,
        )
        return result

    def __eq__(self, other):
        if isinstance(other, DisplayData):
            return (
                self.name == other.name
                and self.radius == other.radius
                and self.display_type == other.display_type
                and self.url == other.url
                and self.color == other.color
            )
        return False
