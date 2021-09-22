# -*- coding: utf-8 -*-

"""Top-level package for Simularium Conversion."""

__author__ = "Blair Lyons"
__email__ = "blairl@alleninstitute.org"
# Do not edit this string manually, always use bumpversion
# Details in CONTRIBUTING.md
__version__ = "1.2.0"


def get_module_version():
    return __version__


from .trajectory_converter import TrajectoryConverter  # noqa: F401
from .file_converter import FileConverter  # noqa: F401

from .data_objects import (  # noqa: F401
    TrajectoryData,
    AgentData,
    UnitData,
    MetaData,
    ModelMetaData,
    CameraData,
    DimensionData,
    DisplayData,
    ScatterPlotData,
    HistogramPlotData,
)
from .constants import DISPLAY_TYPE  # noqa: F401
