#!/usr/bin/env python
# -*- coding: utf-8 -*-

from typing import Dict, Any

import numpy as np

from simulariumio import AgentData, CustomData, UnitData, ScatterPlotData


def three_default_agents() -> Dict[str, Any]:
    return CustomData(
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
        time_units=UnitData("ns"),
        spatial_units=UnitData("nm"),
    )


def test_scatter_plot() -> Dict[str, Any]:
    return ScatterPlotData(
        title="Test Scatterplot 1",
        xaxis_title="time (ns)",
        yaxis_title="concentration (uM)",
        xtrace=np.array([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]),
        ytraces={
            "agent1": np.array(
                [
                    74.0190301,
                    40.35983437,
                    21.29691538,
                    93.67690109,
                    24.54807229,
                    58.38854845,
                    11.19286985,
                    27.28811308,
                    18.89378287,
                    34.53219224,
                ]
            ),
            "agent2": np.array(
                [
                    89.85589674,
                    9.10122431,
                    40.23560224,
                    67.5501959,
                    30.36962677,
                    13.04011962,
                    26.98629198,
                    66.03464652,
                    66.05164469,
                    7.00278548,
                ]
            ),
            "agent3": np.array(
                [
                    24.60902276,
                    12.88084466,
                    52.99450258,
                    85.68006617,
                    26.16588002,
                    36.35818642,
                    77.19386492,
                    9.83423903,
                    23.2876747,
                    58.56315023,
                ]
            ),
        },
        render_mode="lines",
    )
