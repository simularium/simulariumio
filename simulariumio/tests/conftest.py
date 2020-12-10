#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any

import numpy as np

from simulariumio import AgentData, CustomData


def three_default_agents() -> Dict[str, Any]:
    return CustomData(
        spatial_unit_factor_meters=1e-9,
        box_size=np.array([100.0, 100.0, 100.0]),
        agent_data=AgentData(
            times=0.5 * np.array(list(range(3))),
            n_agents=np.array(3 * [3]),
            viz_types=np.array(3 * [3 * [1000.0]]),
            unique_ids=np.array([[0.0, 1.0, 2.0], [0.0, 1.0, 2.0], [0.0, 1.0, 2.0]]),
            types=[["C", "U", "C"], ["U", "L", "S"], ["O", "Y", "W"]],
            positions=np.array(
                [
                    [
                        [4.89610492, -29.81564851, 40.77254057],
                        [43.43048197, 48.00424379, -36.02881338],
                        [29.84924588, -38.02769707, 2.46644825],
                    ],
                    [
                        [-43.37181102, -13.41127423, -17.31316927],
                        [9.62132397, 13.4774314, -20.30846039],
                        [41.41039848, -45.85543786, 49.06208485],
                    ],
                    [
                        [-24.91450698, -44.79360525, 13.32273796],
                        [4.10861266, 43.86451151, 21.93697483],
                        [-7.16740679, -13.06491594, 44.97026158],
                    ],
                ]
            ),
            radii=np.array(
                [
                    [8.38656327, 6.18568039, 6.61459206],
                    [5.26366739, 6.69209780, 9.88033853],
                    [8.91022619, 9.01379396, 8.39880154],
                ]
            ),
        ),
    )
