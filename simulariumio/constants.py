#!/usr/bin/env python
# -*- coding: utf-8 -*-


V1_SPATIAL_BUFFER_STRUCT = [
    "VIZ_TYPE",
    "UID",  # unique ID
    "TID",  # type ID
    "POSX",
    "POSY",
    "POSZ",
    "ROTX",
    "ROTY",
    "ROTZ",
    "R",  # radius
    "NSP",  # num subpoints
    "SP",  # subpoints
]

SPATIAL_UNIT_OPTIONS = [
    "Ym",
    "Zm",
    "Em",
    "Pm",
    "Tm",
    "Gm",
    "Mm",
    "km",
    "hm",
    "dam",
    "m",
    "dm",
    "cm",
    "mm",
    "um",
    "μm",
    "nm",
    "A",
    "pm",
    "fm",
    "am",
    "zm",
    "ym",
]


class VIZ_TYPE:
    default: float = 1000.0
    fiber: float = 1001.0
