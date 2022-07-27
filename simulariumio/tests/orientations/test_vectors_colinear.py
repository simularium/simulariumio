#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import numpy as np

from simulariumio.orientations import RotationUtility


@pytest.mark.parametrize(
    "vector1, vector2, expected",
    [
        (
            np.array([1.0, 0.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
            True,
        ),
        (
            np.array([30.476, 36.034, 26.528]),
            np.array([304.76, 360.34, 265.28]),
            True,
        ),
        (
            np.array([0.0, 1.0, 0.0]),
            np.array([1.0, 0.0, 0.0]),
            False,
        ),
        (
            np.array([1.0, 0.0, 0.0]),
            np.array([-1.0, 0.0, 0.0]),
            True,
        ),
        (
            np.array([-0.3013853, 0.5702147, -0.7642134]),
            np.array([0.3013853, -0.5702147, 0.7642134]),
            True,
        ),
        (
            np.array([-0.3013853, 0.5702147, -0.7642134]),
            np.array([5.46372266, 7.60125865, 3.51690213]),
            False,
        ),
    ],
)
def test_vectors_colinear(vector1, vector2, expected):
    assert RotationUtility._vectors_are_colinear(vector1, vector2) == expected