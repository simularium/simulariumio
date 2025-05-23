#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import numpy as np

from simulariumio.tests.conftest import full_default_buffer
from simulariumio import AgentData, DimensionData
from simulariumio.constants import SUBPOINT_VALUES_PER_ITEM, DISPLAY_TYPE


@pytest.mark.parametrize(
    "axis, expected_data",
    [
        (
            0,
            AgentData(
                times=np.array([0.0, 0.1, 0.2, 0.0]),
                n_agents=np.array([2, 4, 0, 0]),
                viz_types=np.array(
                    [
                        [1001.0, 1000.0, 1001.0, 1000.0],
                        [1001.0, 1000.0, 1001.0, 1000.0],
                        [1001.0, 1000.0, 1001.0, 1000.0],
                        [1000.0, 1000.0, 1000.0, 1000.0],
                    ]
                ),
                unique_ids=np.array(
                    [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [0, 0, 0, 0]]
                ),
                types=[
                    ["A", "B"],
                    ["A", "B", "A", "B"],
                    [],
                    [],
                ],
                positions=np.array(
                    [
                        [
                            [0.0, 0.1, 0.2],
                            [0.3, 0.4, 0.5],
                            [0.6, 0.7, 0.8],
                            [0.9, 1.0, 1.1],
                        ],
                        [
                            [1.2, 1.3, 1.4],
                            [1.5, 1.6, 1.7],
                            [1.8, 1.9, 2.0],
                            [2.1, 2.2, 2.3],
                        ],
                        [
                            [2.4, 2.5, 2.6],
                            [2.7, 2.8, 2.9],
                            [3.0, 3.1, 3.2],
                            [3.3, 3.4, 3.5],
                        ],
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ],
                    ]
                ),
                radii=np.array(
                    [
                        [1.0, 3.0, 1.0, 3.0],
                        [1.0, 3.0, 1.0, 3.0],
                        [1.0, 3.0, 1.0, 3.0],
                        [1.0, 1.0, 1.0, 1.0],
                    ]
                ),
                rotations=np.array(
                    [
                        [
                            [0.0, 10.0, 20.0],
                            [30.0, 40.0, 50.0],
                            [60.0, 70.0, 80.0],
                            [90.0, 100.0, 110.0],
                        ],
                        [
                            [120.0, 130.0, 140.0],
                            [150.0, 160.0, 170.0],
                            [180.0, 190.0, 200.0],
                            [210.0, 220.0, 230.0],
                        ],
                        [
                            [240.0, 250.0, 260.0],
                            [270.0, 280.0, 290.0],
                            [300.0, 310.0, 320.0],
                            [330.0, 340.0, 350.0],
                        ],
                        [
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0],
                        ],
                    ]
                ),
                n_subpoints=np.array(
                    [[6, 0, 6, 0], [6, 0, 6, 0], [6, 0, 6, 0], [0, 0, 0, 0]]
                ),
                subpoints=np.array(
                    [
                        [
                            [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
                            [0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
                            [1.2, 1.3, 1.4, 1.5, 1.6, 1.7],
                            [1.8, 1.9, 2.0, 2.1, 2.2, 2.3],
                        ],
                        [
                            [2.4, 2.5, 2.6, 2.7, 2.8, 2.9],
                            [3.0, 3.1, 3.2, 3.3, 3.4, 3.5],
                            [3.6, 3.7, 3.8, 3.9, 4.0, 4.1],
                            [4.2, 4.3, 4.4, 4.5, 4.6, 4.7],
                        ],
                        [
                            [4.8, 4.9, 5.0, 5.1, 5.2, 5.3],
                            [5.4, 5.5, 5.6, 5.7, 5.8, 5.9],
                            [6.0, 6.1, 6.2, 6.3, 6.4, 6.5],
                            [6.6, 6.7, 6.8, 6.9, 7.0, 7.1],
                        ],
                        [
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        ],
                    ]
                ),
            ),
        ),
        (
            1,
            AgentData(
                times=np.array([0.0, 0.1, 0.2]),
                n_agents=np.array([2, 4, 0]),
                viz_types=np.array(
                    [
                        [1001.0, 1000.0, 1001.0, 1000.0, 1000.0],
                        [1001.0, 1000.0, 1001.0, 1000.0, 1000.0],
                        [1001.0, 1000.0, 1001.0, 1000.0, 1000.0],
                    ]
                ),
                unique_ids=np.array(
                    [[0, 1, 2, 3, 0], [4, 5, 6, 7, 0], [8, 9, 10, 11, 0]]
                ),
                types=[
                    ["A", "B"],
                    ["A", "B", "A", "B"],
                    [],
                ],
                positions=np.array(
                    [
                        [
                            [0.0, 0.1, 0.2],
                            [0.3, 0.4, 0.5],
                            [0.6, 0.7, 0.8],
                            [0.9, 1.0, 1.1],
                            [0.0, 0.0, 0.0],
                        ],
                        [
                            [1.2, 1.3, 1.4],
                            [1.5, 1.6, 1.7],
                            [1.8, 1.9, 2.0],
                            [2.1, 2.2, 2.3],
                            [0.0, 0.0, 0.0],
                        ],
                        [
                            [2.4, 2.5, 2.6],
                            [2.7, 2.8, 2.9],
                            [3.0, 3.1, 3.2],
                            [3.3, 3.4, 3.5],
                            [0.0, 0.0, 0.0],
                        ],
                    ]
                ),
                radii=np.array(
                    [
                        [1.0, 3.0, 1.0, 3.0, 1.0],
                        [1.0, 3.0, 1.0, 3.0, 1.0],
                        [1.0, 3.0, 1.0, 3.0, 1.0],
                    ]
                ),
                rotations=np.array(
                    [
                        [
                            [0.0, 10.0, 20.0],
                            [30.0, 40.0, 50.0],
                            [60.0, 70.0, 80.0],
                            [90.0, 100.0, 110.0],
                            [0.0, 0.0, 0.0],
                        ],
                        [
                            [120.0, 130.0, 140.0],
                            [150.0, 160.0, 170.0],
                            [180.0, 190.0, 200.0],
                            [210.0, 220.0, 230.0],
                            [0.0, 0.0, 0.0],
                        ],
                        [
                            [240.0, 250.0, 260.0],
                            [270.0, 280.0, 290.0],
                            [300.0, 310.0, 320.0],
                            [330.0, 340.0, 350.0],
                            [0.0, 0.0, 0.0],
                        ],
                    ]
                ),
                n_subpoints=np.array(
                    [[6, 0, 6, 0, 0], [6, 0, 6, 0, 0], [6, 0, 6, 0, 0]]
                ),
                subpoints=np.array(
                    [
                        [
                            [0.0, 0.1, 0.2, 0.3, 0.4, 0.5],
                            [0.6, 0.7, 0.8, 0.9, 1.0, 1.1],
                            [1.2, 1.3, 1.4, 1.5, 1.6, 1.7],
                            [1.8, 1.9, 2.0, 2.1, 2.2, 2.3],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        ],
                        [
                            [2.4, 2.5, 2.6, 2.7, 2.8, 2.9],
                            [3.0, 3.1, 3.2, 3.3, 3.4, 3.5],
                            [3.6, 3.7, 3.8, 3.9, 4.0, 4.1],
                            [4.2, 4.3, 4.4, 4.5, 4.6, 4.7],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        ],
                        [
                            [4.8, 4.9, 5.0, 5.1, 5.2, 5.3],
                            [5.4, 5.5, 5.6, 5.7, 5.8, 5.9],
                            [6.0, 6.1, 6.2, 6.3, 6.4, 6.5],
                            [6.6, 6.7, 6.8, 6.9, 7.0, 7.1],
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        ],
                    ]
                ),
            ),
        ),
        (
            2,
            AgentData(
                times=np.array([0.0, 0.1, 0.2]),
                n_agents=np.array([2, 4, 0]),
                viz_types=np.array(
                    [
                        [1001.0, 1000.0, 1001.0, 1000.0],
                        [1001.0, 1000.0, 1001.0, 1000.0],
                        [1001.0, 1000.0, 1001.0, 1000.0],
                    ]
                ),
                unique_ids=np.array([[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]),
                types=[
                    ["A", "B"],
                    ["A", "B", "A", "B"],
                    [],
                ],
                positions=np.array(
                    [
                        [
                            [0.0, 0.1, 0.2],
                            [0.3, 0.4, 0.5],
                            [0.6, 0.7, 0.8],
                            [0.9, 1.0, 1.1],
                        ],
                        [
                            [1.2, 1.3, 1.4],
                            [1.5, 1.6, 1.7],
                            [1.8, 1.9, 2.0],
                            [2.1, 2.2, 2.3],
                        ],
                        [
                            [2.4, 2.5, 2.6],
                            [2.7, 2.8, 2.9],
                            [3.0, 3.1, 3.2],
                            [3.3, 3.4, 3.5],
                        ],
                    ]
                ),
                radii=np.array(
                    [[1.0, 3.0, 1.0, 3.0], [1.0, 3.0, 1.0, 3.0], [1.0, 3.0, 1.0, 3.0]]
                ),
                rotations=np.array(
                    [
                        [
                            [0.0, 10.0, 20.0],
                            [30.0, 40.0, 50.0],
                            [60.0, 70.0, 80.0],
                            [90.0, 100.0, 110.0],
                        ],
                        [
                            [120.0, 130.0, 140.0],
                            [150.0, 160.0, 170.0],
                            [180.0, 190.0, 200.0],
                            [210.0, 220.0, 230.0],
                        ],
                        [
                            [240.0, 250.0, 260.0],
                            [270.0, 280.0, 290.0],
                            [300.0, 310.0, 320.0],
                            [330.0, 340.0, 350.0],
                        ],
                    ]
                ),
                n_subpoints=np.array([[6, 0, 6, 0], [6, 0, 6, 0], [6, 0, 6, 0]]),
                subpoints=np.array(
                    [
                        [
                            [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.0, 0.0, 0.0],
                            [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 0.0, 0.0, 0.0],
                            [1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 0.0, 0.0, 0.0],
                            [1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 0.0, 0.0, 0.0],
                        ],
                        [
                            [2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 0.0, 0.0, 0.0],
                            [3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 0.0, 0.0, 0.0],
                            [3.6, 3.7, 3.8, 3.9, 4.0, 4.1, 0.0, 0.0, 0.0],
                            [4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 0.0, 0.0, 0.0],
                        ],
                        [
                            [4.8, 4.9, 5.0, 5.1, 5.2, 5.3, 0.0, 0.0, 0.0],
                            [5.4, 5.5, 5.6, 5.7, 5.8, 5.9, 0.0, 0.0, 0.0],
                            [6.0, 6.1, 6.2, 6.3, 6.4, 6.5, 0.0, 0.0, 0.0],
                            [6.6, 6.7, 6.8, 6.9, 7.0, 7.1, 0.0, 0.0, 0.0],
                        ],
                    ]
                ),
            ),
        ),
    ],
)
def test_buffer_contents(axis, expected_data):
    agent_data = full_default_buffer()
    added_dimensions = (
        DimensionData(
            total_steps=1,
            max_agents=0,
        )
        if axis == 0
        else DimensionData(
            total_steps=0,
            max_agents=1,
        )
        if axis == 1
        else DimensionData(
            total_steps=0,
            max_agents=0,
            max_subpoints=SUBPOINT_VALUES_PER_ITEM(DISPLAY_TYPE.FIBER),
        )
    )
    agent_data = agent_data.get_copy_with_increased_buffer_size(
        added_dimensions=added_dimensions,
        axis=axis,
    )
    assert agent_data == expected_data
