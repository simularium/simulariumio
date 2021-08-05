#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from simulariumio.tests.conftest import empty_buffer
from simulariumio import DimensionData
from simulariumio.constants import BUFFER_SIZE_INC


@pytest.mark.parametrize(
    "total_steps, n_agents, n_subpoints, next_index, axis, expected_dimensions",
    [
        (
            10,
            10,
            0,
            9,
            0,
            DimensionData(
                total_steps=10,
                max_agents=10,
                max_subpoints=0,
            ),
        ),
        (
            10,
            10,
            0,
            10,
            0,
            DimensionData(
                total_steps=BUFFER_SIZE_INC.total_steps + 10,
                max_agents=10,
                max_subpoints=0,
            ),
        ),
        (
            10,
            10,
            0,
            9,
            1,
            DimensionData(
                total_steps=10,
                max_agents=10,
                max_subpoints=0,
            ),
        ),
        (
            1000,
            10,
            0,
            10,
            1,
            DimensionData(
                total_steps=1000,
                max_agents=BUFFER_SIZE_INC.max_agents + 10,
                max_subpoints=0,
            ),
        ),
        (
            10,
            10,
            10,
            0,
            2,
            DimensionData(
                total_steps=10,
                max_agents=10,
                max_subpoints=10,
            ),
        ),
        (
            10,
            10,
            0,
            0,
            2,
            DimensionData(
                total_steps=10,
                max_agents=10,
                max_subpoints=BUFFER_SIZE_INC.max_subpoints,
            ),
        ),
        (
            10,
            10,
            1,
            1,
            2,
            DimensionData(
                total_steps=10,
                max_agents=10,
                max_subpoints=BUFFER_SIZE_INC.max_subpoints + 1,
            ),
        ),
    ],
)
def test_buffer_size(
    total_steps, n_agents, n_subpoints, next_index, axis, expected_dimensions
):
    agent_data = empty_buffer(total_steps, n_agents, n_subpoints)
    agent_data = agent_data.check_increase_buffer_size(next_index, axis)
    assert agent_data.get_dimensions() == expected_dimensions
