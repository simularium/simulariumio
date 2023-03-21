# -*- coding: utf-8 -*-

"""Top-level package for simulariumio."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("simulariumio")
except PackageNotFoundError:
    __version__ = "uninstalled"


from .data_objects import (  # noqa: F401
    AgentData,
    DisplayData,
    CameraData,
    DimensionData,
    HistogramPlotData,
    InputFileData,
    MetaData,
    ModelMetaData,
    ScatterPlotData,
    TrajectoryData,
    UnitData,
)
# DO NOT ISORT DISPLAY_TYPE, CAUSES CIRCULAR DEP
from .constants import DISPLAY_TYPE  # noqa: F401
from .file_converter import FileConverter  # noqa: F401
from .trajectory_converter import TrajectoryConverter  # noqa: F401
from .writers import BinaryWriter, JsonWriter  # noqa: F401
