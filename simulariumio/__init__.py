# -*- coding: utf-8 -*-

"""Top-level package for Simularium Conversion."""

__author__ = "Blair Lyons"
__email__ = "blairl@alleninstitute.org"
# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "1.0.1"


def get_module_version():
    return __version__


from .custom_converter import CustomConverter  # noqa: F401

from .data_objects import (  # noqa: F401
    CustomData,
    AgentData,
    ScatterPlotData,
    HistogramPlotData,
)
