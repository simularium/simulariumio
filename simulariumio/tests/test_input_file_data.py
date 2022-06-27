#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from simulariumio import InputFileData


@pytest.mark.parametrize(
    "input_path, is_binary",
    [
        (
            (
                "simulariumio/tests/data/cytosim/aster_pull3D_couples_actin"
                "_solid_3_frames/aster_pull3D_couples_actin_solid_3_frames.json"
            ),
            False,
        ),
        (
            (
                "simulariumio/tests/data/binary/"
                "50filaments_motor_linker_binary.binary"
            ),
            True,
        ),
    ],
)
def test_input_file_is_binary(input_path, is_binary):
    input_file = InputFileData(file_path=input_path)
    assert input_file._is_binary_file() == is_binary
