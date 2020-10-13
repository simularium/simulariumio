# -*- coding: utf-8 -*-

"""Top-level package for Simularium Conversion."""

__author__ = "Blair Lyons"
__email__ = "blairl@alleninstitute.org"
# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "0.0.0"


def get_module_version():
    return __version__


from .custom_converter import CustomConverter  # noqa: F401
from .cytosim_converter import CytosimConverter  # noqa: F401
from .readdy_converter import ReaddyConverter  # noqa: F401
from .physicell_converter import PhysicellConverter  # noqa: F401

from .data_objects import (
    CustomData,
    AgentData,
    CytosimData,
    CytosimObjectInfo,
    CytosimAgentInfo,
    ReaddyData,
    PhysicellData,
    ScatterPlotData,
    HistogramPlotData
)  # noqa: F401