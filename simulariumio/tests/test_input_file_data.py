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
    assert input_file._is_binary() == is_binary


@pytest.mark.parametrize(
    "file_to_read, is_binary",
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
def test_input_data_binary(file_to_read, is_binary):
    with open(file_to_read, "rb") as open_binary_file:
        content = open_binary_file.read()
        file_data = InputFileData(file_contents=content)
        assert file_data._is_binary() == is_binary
