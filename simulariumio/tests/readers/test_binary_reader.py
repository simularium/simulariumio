#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from simulariumio import (
    FileConverter,
    InputFileData,
    TrajectoryConverter,
    JsonWriter,
)
from simulariumio.tests.conftest import binary_test_data, assert_buffers_equal


@pytest.mark.parametrize(
    "input_path, expected_data",
    [
        (
            "simulariumio/tests/data/binary/binary_test.binary",
            binary_test_data,
        ),
    ],
)
def test_binary_file_parsing(
    input_path,
    expected_data,
):
    test_converter = FileConverter(input_file=InputFileData(file_path=input_path))
    test_buffer_data = JsonWriter.format_trajectory_data(test_converter._data)
    expected_converter = TrajectoryConverter(expected_data)
    expected_buffer_data = JsonWriter.format_trajectory_data(expected_converter._data)
    assert_buffers_equal(test_buffer_data, expected_buffer_data)


@pytest.mark.parametrize(
    "input_path, expected_data",
    [
        (
            "simulariumio/tests/data/binary/binary_test.binary",
            binary_test_data,
        ),
    ],
)
def test_binary_parsing(
    input_path,
    expected_data,
):
    with open(input_path, "rb") as open_binary_file:
        binary_content = open_binary_file.read()
        test_converter = FileConverter(
            input_file=InputFileData(file_contents=binary_content)
        )
        test_buffer_data = JsonWriter.format_trajectory_data(test_converter._data)
        expected_converter = TrajectoryConverter(expected_data)
        expected_buffer_data = JsonWriter.format_trajectory_data(
            expected_converter._data
        )
        assert_buffers_equal(test_buffer_data, expected_buffer_data)
