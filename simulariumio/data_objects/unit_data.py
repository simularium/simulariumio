#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
from typing import Any, Dict
from pint import UnitRegistry
import numpy as np

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class UnitData:
    magnitude: float
    name: str

    def __init__(
        self,
        name: str,
        magnitude: float = 1.0,
    ):
        """
        This object contains data for units

        Parameters
        ----------
        name: str
            unit name for values (we support this list
            https://github.com/hgrecco/pint/blob/master/pint/default_en.txt)
        magnitude: float (optional)
            multiplier for values (in case they are not given in whole units)
            Default: 1.0
        """
        # standardize and simplify units with pint
        ureg = UnitRegistry()
        self._quantity = magnitude * ureg(name)
        self._update_units()

    def _clamp_precision(self, number: float):
        """
        clamp float precision to 4 significant figures
        """
        return float("%.4g" % number)

    def _update_units(self):
        """
        update magnitude and name after setting quantity
        """
        self._quantity = self._quantity.to_compact()
        self.magnitude = self._clamp_precision(self._quantity.magnitude)
        n = f"{self._quantity.units:~}"
        # pint has the wrong abbreviation for microns? (µ instead of µm)
        if n == "µ":
            n += "m"
        self.name = n

    def multiply(self, multiplier: float):
        """
        multiply quantity and simplify
        """
        self._quantity *= multiplier
        self._update_units()

    @classmethod
    def from_dict(
        cls,
        unit_data: Dict[str, Any],
        default_name: str = None,
        default_mag: float = 1.0
    ):
        """
        Create UnitData object from a simularium JSON dict
        """
        if unit_data is None:
            return cls(name=default_name, magnitude=default_mag)
        return cls(
            name=unit_data.get("name", default_name),
            magnitude=float(unit_data.get("magnitude", default_mag)),
        )

    def __str__(self):
        """
        get a string for the units
        """
        magnitude = (
            str(self.magnitude) + " "
            if self.magnitude > 1.0 + sys.float_info.epsilon
            or self.magnitude < 1.0 - sys.float_info.epsilon
            else ""
        )
        return f"{magnitude}{self.name}"

    def __copy__(self):
        result = type(self)(
            name=self.name,
            magnitude=self.magnitude,
        )
        return result

    def __eq__(self, other):
        if isinstance(other, UnitData):
            return (
                np.isclose(self.magnitude, other.magnitude)
                and self.name == other.name
            )
        return False
