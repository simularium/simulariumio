#!/usr/bin/env python
# -*- coding: utf-8 -*-

from string import ascii_uppercase
from random import choice
from typing import Dict, Any

import numpy as np

from simulariumio import (
    TrajectoryData,
    AgentData,
    UnitData,
    MetaData,
    ScatterPlotData,
    DisplayData,
    CameraData,
    ModelMetaData,
)
from simulariumio.constants import (
    DISPLAY_TYPE,
    VALUES_PER_3D_POINT,
    SUBPOINT_VALUES_PER_ITEM,
)


def default_agents_type_mapping() -> Dict[str, Any]:
    return {
        "0": {
            "name": "C",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
        "1": {
            "name": "U",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
        "2": {
            "name": "L",
            "geometry": {
                "displayType": "OBJ",
                "url": "molecule.obj",
                "color": "#333333",
            },
        },
        "3": {
            "name": "S",
            "geometry": {
                "displayType": "SPHERE",
                "color": "#000000",
            },
        },
        "4": {
            "name": "O",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
        "5": {
            "name": "Y",
            "geometry": {
                "displayType": "PDB",
                "url": "https://files.rcsb.org/download/7PDZ.pdb",
            },
        },
        "6": {
            "name": "W",
            "geometry": {
                "displayType": "SPHERE",
                "color": "#666",
            },
        },
    }


def minimal_custom_type_mappings() -> Dict[str, Any]:
    return {
        "0": {
            "name": "C",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
        "1": {
            "name": "U",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
        "2": {
            "name": "L",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
        "3": {
            "name": "S",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
        "4": {
            "name": "O",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
        "5": {
            "name": "Y",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
        "6": {
            "name": "W",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
    }


def three_default_agents() -> TrajectoryData:
    return TrajectoryData(
        meta_data=MetaData(
            box_size=np.array([100.0, 100.0, 100.0]),
        ),
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
            rotations=np.array(
                [
                    [
                        [40.77254057, -29.81564851, 4.89610492],
                        [-36.02881338, 48.00424379, 43.43048197],
                        [2.46644825, -38.02769707, 29.84924588],
                    ],
                    [
                        [-17.31316927, -13.41127423, -43.37181102],
                        [-20.30846039, 13.4774314, 9.62132397],
                        [49.06208485, -45.85543786, 41.41039848],
                    ],
                    [
                        [13.32273796, -44.79360525, -24.91450698],
                        [21.93697483, 43.86451151, 4.10861266],
                        [44.97026158, -13.06491594, -7.16740679],
                    ],
                ]
            ),
            display_data={
                "W": DisplayData(
                    name="W",
                    display_type=DISPLAY_TYPE.SPHERE,
                    color="#666",
                ),
                "S": DisplayData(
                    name="S",
                    display_type=DISPLAY_TYPE.SPHERE,
                    color="#000000",
                ),
                "Y": DisplayData(
                    name="Y",
                    display_type=DISPLAY_TYPE.PDB,
                    url="https://files.rcsb.org/download/7PDZ.pdb",
                ),
                "L": DisplayData(
                    name="L",
                    display_type=DISPLAY_TYPE.OBJ,
                    url="molecule.obj",
                    color="#333333",
                ),
                "U": DisplayData(
                    name="U",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                "O": DisplayData(
                    name="O",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
            },
        ),
        time_units=UnitData("ns"),
        spatial_units=UnitData("nm"),
    )


def minimal_custom_data() -> TrajectoryData:
    return TrajectoryData(
        meta_data=MetaData(),
        agent_data=AgentData(
            times=0.5 * np.array(list(range(3))),
            n_agents=np.array(3 * [3]),
            viz_types=np.array(3 * [3 * [1000.0]]),
            unique_ids=np.array([[0.0, 1.0, 2.0], [0.0, 1.0, 2.0], [0.0, 1.0, 2.0]]),
            types=[["C", "U", "C"], ["U", "L", "S"], ["O", "Y", "W"]],
            display_data={
                "C": DisplayData(
                    name="C",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                "W": DisplayData(
                    name="W",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                "S": DisplayData(
                    name="S",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                "Y": DisplayData(
                    name="Y",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                "L": DisplayData(
                    name="L",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                "U": DisplayData(
                    name="U",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                "O": DisplayData(
                    name="O",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
            },
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


def test_scatter_plot() -> ScatterPlotData:
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


def empty_buffer(total_steps: int, n_agents: int, n_subpoints: int) -> AgentData:
    box_size = 100
    type_names = []
    for t in range(total_steps):
        type_names.append([choice(ascii_uppercase) for i in range(n_agents)])
    return AgentData(
        times=0.1 * np.array(list(range(total_steps))),
        n_agents=np.array(total_steps * [n_agents]),
        viz_types=np.array(
            total_steps * [n_agents * [1000.0]]
        ),  # default viz type = 1000
        unique_ids=np.array(total_steps * [list(range(n_agents))]),
        types=type_names,
        positions=np.ones((total_steps, n_agents, VALUES_PER_3D_POINT)) * box_size
        - box_size * 0.5,
        radii=np.ones((total_steps, n_agents)),
        rotations=np.ones((total_steps, n_agents, VALUES_PER_3D_POINT)) * 360,
        n_subpoints=SUBPOINT_VALUES_PER_ITEM(DISPLAY_TYPE.FIBER)
        * n_subpoints
        * np.ones((total_steps, n_agents)),
        subpoints=np.ones((total_steps, n_agents, n_subpoints)),
    )


def full_default_buffer() -> AgentData:
    total_steps = 3
    max_agents = 4
    max_subpoints = 2 * SUBPOINT_VALUES_PER_ITEM(DISPLAY_TYPE.FIBER)
    return AgentData(
        times=0.1 * np.arange(total_steps),
        n_agents=np.array([2, 4, 0]),
        viz_types=np.array(total_steps * [int(0.5 * max_agents) * [1001.0, 1000.0]]),
        unique_ids=np.arange(total_steps * max_agents).reshape(
            (total_steps, max_agents)
        ),
        types=np.array(total_steps * [int(0.5 * max_agents) * ["A", "B"]]).tolist(),
        positions=0.1
        * np.arange(total_steps * max_agents * VALUES_PER_3D_POINT).reshape(
            (total_steps, max_agents, VALUES_PER_3D_POINT)
        ),
        radii=np.array(total_steps * [int(0.5 * max_agents) * [1.0, 3.0]]),
        rotations=10.0
        * np.arange(total_steps * max_agents * VALUES_PER_3D_POINT).reshape(
            (total_steps, max_agents, VALUES_PER_3D_POINT)
        ),
        n_subpoints=np.array(
            total_steps
            * [
                int(0.5 * max_agents)
                * [2 * SUBPOINT_VALUES_PER_ITEM(DISPLAY_TYPE.FIBER), 0]
            ]
        ),
        subpoints=0.1
        * np.arange(total_steps * max_agents * max_subpoints).reshape(
            (total_steps, max_agents, max_subpoints)
        ),
    )


def fiber_agents_type_mapping() -> Dict[str, Any]:
    return {
        "0": {
            "name": "H",
            "geometry": {
                "displayType": "FIBER",
            },
        },
        "1": {
            "name": "A",
            "geometry": {
                "displayType": "FIBER",
            },
        },
        "2": {
            "name": "C",
            "geometry": {
                "displayType": "FIBER",
            },
        },
        "3": {
            "name": "L",
            "geometry": {
                "displayType": "FIBER",
            },
        },
        "4": {
            "name": "D",
            "geometry": {
                "displayType": "FIBER",
            },
        },
        "5": {
            "name": "K",
            "geometry": {
                "displayType": "FIBER",
            },
        },
    }


def fiber_agents() -> TrajectoryData:
    return TrajectoryData(
        meta_data=MetaData(
            box_size=np.array([1000.0, 1000.0, 1000.0]),
            model_meta_data=ModelMetaData(
                title="Some fibers",
                authors="A Modeler",
            ),
        ),
        agent_data=AgentData(
            times=np.array([0.0, 1.00001, 2.00001]),
            n_agents=np.array(3 * [3]),
            viz_types=1001.0 * np.ones(shape=(3, 3)),
            unique_ids=np.array([[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]),
            types=[["H", "A", "C"], ["L", "D", "A"], ["K", "K", "A"]],
            positions=np.zeros(shape=(3, 3, 3)),
            radii=np.ones(shape=(3, 3)),
            n_subpoints=np.array([[9, 12, 6], [9, 9, 6], [9, 6, 6]]),
            subpoints=np.array(
                [
                    [
                        [
                            -243.14059805,
                            207.75566987,
                            -95.33921063,
                            -20.54663446,
                            475.97201603,
                            14.43506311,
                            -76.45581828,
                            -97.31170699,
                            -144.30184731,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            108.28447939,
                            175.55049775,
                            -274.34792273,
                            13.44237701,
                            258.21483663,
                            -65.05452787,
                            224.55922362,
                            -455.56482869,
                            -351.23389958,
                            -286.95502659,
                            330.12683064,
                            183.79420473,
                        ],
                        [
                            49.76236816,
                            -353.11708296,
                            226.84570983,
                            -234.5462914,
                            105.46507228,
                            17.16552317,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                    ],
                    [
                        [
                            -442.27202981,
                            202.83568625,
                            -262.13407113,
                            -372.23130078,
                            217.21997368,
                            404.88561338,
                            171.37918011,
                            205.80515525,
                            -65.95336727,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            245.9111405,
                            372.15936027,
                            -261.94702214,
                            3.50037066,
                            441.92904046,
                            321.75701298,
                            146.23928574,
                            -315.3241668,
                            82.00405173,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            104.82606074,
                            -413.76671598,
                            366.66127719,
                            136.7228888,
                            -210.69313998,
                            -465.59967482,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                    ],
                    [
                        [
                            -148.70447678,
                            225.27562348,
                            -273.51318785,
                            -5.32043612,
                            -55.97783429,
                            413.32948686,
                            165.64239994,
                            322.63703294,
                            -2.2348818,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            -317.48515644,
                            -237.70246887,
                            238.69661676,
                            94.56942257,
                            346.13786088,
                            -7.93209392,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            7.77508859,
                            260.16762947,
                            -171.02427873,
                            -20.46326319,
                            179.43194042,
                            485.07810635,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                    ],
                ]
            ),
            display_data={
                "H": DisplayData(
                    name="H",
                    display_type=DISPLAY_TYPE.FIBER,
                ),
                "A": DisplayData(
                    name="A",
                    display_type=DISPLAY_TYPE.FIBER,
                ),
                "C": DisplayData(
                    name="C",
                    display_type=DISPLAY_TYPE.FIBER,
                ),
                "L": DisplayData(
                    name="L",
                    display_type=DISPLAY_TYPE.FIBER,
                ),
                "D": DisplayData(
                    name="D",
                    display_type=DISPLAY_TYPE.FIBER,
                ),
                "K": DisplayData(
                    name="K",
                    display_type=DISPLAY_TYPE.FIBER,
                ),
            },
            draw_fiber_points=True,
        ),
        time_units=UnitData("us"),
        spatial_units=UnitData("m", 10.0),
        plots=["plot data goes here"],
    )


def mixed_agents_type_mapping() -> Dict[str, Any]:
    return {
        "0": {
            "name": "H",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
        "1": {
            "name": "A",
            "geometry": {
                "displayType": "FIBER",
            },
        },
        "2": {
            "name": "C",
            "geometry": {
                "displayType": "FIBER",
            },
        },
        "3": {
            "name": "X",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
        "4": {
            "name": "J",
            "geometry": {
                "displayType": "FIBER",
            },
        },
        "5": {
            "name": "L",
            "geometry": {
                "displayType": "FIBER",
            },
        },
        "6": {
            "name": "D",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
        "7": {
            "name": "U",
            "geometry": {
                "displayType": "FIBER",
            },
        },
        "8": {
            "name": "E",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
        "9": {
            "name": "Q",
            "geometry": {
                "displayType": "SPHERE",
            },
        },
        "10": {
            "name": "K",
            "geometry": {
                "displayType": "FIBER",
            },
        },
    }


def mixed_agents() -> TrajectoryData:
    return TrajectoryData(
        meta_data=MetaData(
            box_size=np.array([1000.0, 1000.0, 1000.0]),
            camera_defaults=CameraData(
                position=np.array([0.0, 120.0, 0.0]),
                look_at_position=np.array([10.0, 0.0, 0.0]),
                up_vector=np.array([0.0, 0.0, 1.0]),
                fov_degrees=60.0,
            ),
            trajectory_title="low concentrations",
            model_meta_data=ModelMetaData(
                title="Some agent-based model",
                version="8.1",
                authors="A Modeler",
                description=(
                    "An agent-based model started with low agent concentrations"
                ),
                doi="https://doi.org/10.7554/eLife.49840",
                input_data_url="https://allencell.org",
            ),
        ),
        agent_data=AgentData(
            times=1.0 * np.array(list(range(3))),
            n_agents=np.array(3 * [5]),
            viz_types=np.array(
                [
                    [1000.0, 1001.0, 1001.0, 1000.0, 1001.0],
                    [1001.0, 1000.0, 1001.0, 1001.0, 1000.0],
                    [1000.0, 1000.0, 1001.0, 1001.0, 1001.0],
                ]
            ),
            unique_ids=np.array(
                [
                    [0.0, 1.0, 2.0, 3.0, 4.0],
                    [0.0, 1.0, 2.0, 3.0, 4.0],
                    [0.0, 1.0, 2.0, 3.0, 4.0],
                ]
            ),
            types=[
                ["H", "A", "C", "X", "J"],
                ["L", "D", "A", "U", "D"],
                ["E", "Q", "K", "K", "A"],
            ],
            positions=np.array(
                [
                    [
                        [4.89610492, -29.81564851, 40.77254057],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [43.43048197, 48.00424379, -36.02881338],
                        [0.0, 0.0, 0.0],
                    ],
                    [
                        [0.0, 0.0, 0.0],
                        [-43.37181102, -13.41127423, -17.31316927],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [9.62132397, 13.4774314, -20.30846039],
                    ],
                    [
                        [-24.91450698, -44.79360525, 13.32273796],
                        [4.10861266, 43.86451151, 21.93697483],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                        [0.0, 0.0, 0.0],
                    ],
                ]
            ),
            radii=np.array(
                [
                    [8.38656327, 1.0, 1.0, 6.18568039, 1.0],
                    [1.0, 6.69209780, 1.0, 1.0, 9.88033853],
                    [8.91022619, 9.01379396, 1.0, 1.0, 1.0],
                ]
            ),
            n_subpoints=np.array([[0, 9, 12, 0, 6], [9, 0, 9, 6, 0], [0, 0, 9, 6, 6]]),
            subpoints=np.array(
                [
                    [
                        [
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            -243.14059805,
                            207.75566987,
                            -95.33921063,
                            -20.54663446,
                            475.97201603,
                            14.43506311,
                            -76.45581828,
                            -97.31170699,
                            -144.30184731,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            108.28447939,
                            175.55049775,
                            -274.34792273,
                            13.44237701,
                            258.21483663,
                            -65.05452787,
                            224.55922362,
                            -455.56482869,
                            -351.23389958,
                            -286.95502659,
                            330.12683064,
                            183.79420473,
                        ],
                        [
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            49.76236816,
                            -353.11708296,
                            226.84570983,
                            -234.5462914,
                            105.46507228,
                            17.16552317,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                    ],
                    [
                        [
                            -442.27202981,
                            202.83568625,
                            -262.13407113,
                            -372.23130078,
                            217.21997368,
                            404.88561338,
                            171.37918011,
                            205.80515525,
                            -65.95336727,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            245.9111405,
                            372.15936027,
                            -261.94702214,
                            3.50037066,
                            441.92904046,
                            321.75701298,
                            146.23928574,
                            -315.3241668,
                            82.00405173,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            104.82606074,
                            -413.76671598,
                            366.66127719,
                            136.7228888,
                            -210.69313998,
                            -465.59967482,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                    ],
                    [
                        [
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            -148.70447678,
                            225.27562348,
                            -273.51318785,
                            -5.32043612,
                            -55.97783429,
                            413.32948686,
                            165.64239994,
                            322.63703294,
                            -2.2348818,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            -317.48515644,
                            -237.70246887,
                            238.69661676,
                            94.56942257,
                            346.13786088,
                            -7.93209392,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                        [
                            7.77508859,
                            260.16762947,
                            -171.02427873,
                            -20.46326319,
                            179.43194042,
                            485.07810635,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                            0.0,
                        ],
                    ],
                ]
            ),
            display_data={
                "H": DisplayData(
                    name="H",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                "A": DisplayData(
                    name="A",
                    display_type=DISPLAY_TYPE.FIBER,
                ),
                "C": DisplayData(
                    name="C",
                    display_type=DISPLAY_TYPE.FIBER,
                ),
                "X": DisplayData(
                    name="X",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                "J": DisplayData(
                    name="J",
                    display_type=DISPLAY_TYPE.FIBER,
                ),
                "L": DisplayData(
                    name="L",
                    display_type=DISPLAY_TYPE.FIBER,
                ),
                "D": DisplayData(
                    name="D",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                "U": DisplayData(
                    name="U",
                    display_type=DISPLAY_TYPE.FIBER,
                ),
                "E": DisplayData(
                    name="E",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                "Q": DisplayData(
                    name="Q",
                    display_type=DISPLAY_TYPE.SPHERE,
                ),
                "K": DisplayData(
                    name="K",
                    display_type=DISPLAY_TYPE.FIBER,
                ),
            },
        ),
        time_units=UnitData("s", 2.0),
        spatial_units=UnitData("um"),
        plots=["plot data goes here"],
    )


def sphere_group_agents() -> TrajectoryData:
    return TrajectoryData(
        meta_data=MetaData(
            box_size=np.array([100.0, 100.0, 100.0]),
        ),
        agent_data=AgentData(
            times=0.5 * np.array(list(range(3))),
            n_agents=np.array(3 * [2]),
            viz_types=np.array(3 * [2 * [1000.0]]),
            unique_ids=np.array(3 * [list(range(2))]),
            types=[
                ["A", "B"],
                ["A", "B"],
                ["A", "B"],
            ],
            positions=np.zeros(shape=(3, 2, 3)),
            radii=np.ones(shape=(3, 2)),
            n_subpoints=3 * 4 * np.ones(shape=(3, 2)),
            subpoints=np.array(
                [
                    [
                        [
                            10,
                            12,
                            0,
                            2,
                            12,
                            9,
                            0,
                            1,
                            8,
                            9,
                            0,
                            1,
                        ],
                        [
                            0,
                            10,
                            12,
                            1,
                            0,
                            12,
                            9,
                            2,
                            0,
                            8,
                            9,
                            2,
                        ],
                    ],
                    [
                        [
                            11,
                            13,
                            1,
                            2,
                            13,
                            10,
                            1,
                            1,
                            9,
                            10,
                            1,
                            1,
                        ],
                        [
                            1,
                            10,
                            12,
                            1,
                            1,
                            12,
                            9,
                            2,
                            1,
                            8,
                            9,
                            2,
                        ],
                    ],
                    [
                        [
                            11,
                            13,
                            1,
                            2,
                            13,
                            10,
                            1,
                            1,
                            9,
                            10,
                            1,
                            1,
                        ],
                        [
                            1,
                            10,
                            12,
                            1,
                            1,
                            12,
                            9,
                            2,
                            1,
                            8,
                            9,
                            2,
                        ],
                    ],
                ]
            ),
            display_data={
                "A": DisplayData(
                    name="A",
                    display_type=DISPLAY_TYPE.SPHERE_GROUP,
                ),
                "B": DisplayData(
                    name="B",
                    display_type=DISPLAY_TYPE.SPHERE_GROUP,
                ),
            },
        ),
        plots=["plot data goes here"],
    )


# 2 default agents (radius 5-10) and 3 fiber agents
# at given positions for 3 frames, no plots
binary_test_data = TrajectoryData(
    meta_data=MetaData(
        box_size=np.array([1000.0, 1000.0, 1000.0]),
    ),
    agent_data=AgentData(
        times=1.0 * np.array(list(range(3))),
        n_agents=np.array(3 * [5]),
        viz_types=np.array(
            [
                [1000.0, 1001.0, 1001.0, 1000.0, 1001.0],
                [1001.0, 1000.0, 1001.0, 1001.0, 1000.0],
                [1000.0, 1000.0, 1001.0, 1001.0, 1001.0],
            ]
        ),
        unique_ids=np.array(
            [
                [0.0, 1.0, 2.0, 3.0, 4.0],
                [0.0, 1.0, 2.0, 3.0, 4.0],
                [0.0, 1.0, 2.0, 3.0, 4.0],
            ]
        ),
        types=[
            ["H", "A", "C", "X", "J"],
            ["L", "D", "A", "U", "D"],
            ["E", "Q", "K", "K", "A"],
        ],
        positions=np.array(
            [
                [
                    [4.89610492, -29.81564851, 40.77254057],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [43.43048197, 48.00424379, -36.02881338],
                    [0.0, 0.0, 0.0],
                ],
                [
                    [0.0, 0.0, 0.0],
                    [-43.37181102, -13.41127423, -17.31316927],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [9.62132397, 13.4774314, -20.30846039],
                ],
                [
                    [-24.91450698, -44.79360525, 13.32273796],
                    [4.10861266, 43.86451151, 21.93697483],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                ],
            ]
        ),
        radii=np.array(
            [
                [8.38656327, 1.0, 1.0, 6.18568039, 1.0],
                [1.0, 6.69209780, 1.0, 1.0, 9.88033853],
                [8.91022619, 9.01379396, 1.0, 1.0, 1.0],
            ]
        ),
        n_subpoints=np.array([[0, 9, 12, 0, 6], [9, 0, 9, 6, 0], [0, 0, 9, 6, 6]]),
        subpoints=np.array(
            [
                [
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                    ],
                    [
                        -243.14059805,
                        207.75566987,
                        -95.33921063,
                        -20.54663446,
                        475.97201603,
                        14.43506311,
                        -76.45581828,
                        -97.31170699,
                        -144.30184731,
                        0.0,
                        0.0,
                        0.0,
                    ],
                    [
                        108.28447939,
                        175.55049775,
                        -274.34792273,
                        13.44237701,
                        258.21483663,
                        -65.05452787,
                        224.55922362,
                        -455.56482869,
                        -351.23389958,
                        -286.95502659,
                        330.12683064,
                        183.79420473,
                    ],
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                    ],
                    [
                        49.76236816,
                        -353.11708296,
                        226.84570983,
                        -234.5462914,
                        105.46507228,
                        17.16552317,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                    ],
                ],
                [
                    [
                        -442.27202981,
                        202.83568625,
                        -262.13407113,
                        -372.23130078,
                        217.21997368,
                        404.88561338,
                        171.37918011,
                        205.80515525,
                        -65.95336727,
                        0.0,
                        0.0,
                        0.0,
                    ],
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                    ],
                    [
                        245.9111405,
                        372.15936027,
                        -261.94702214,
                        3.50037066,
                        441.92904046,
                        321.75701298,
                        146.23928574,
                        -315.3241668,
                        82.00405173,
                        0.0,
                        0.0,
                        0.0,
                    ],
                    [
                        104.82606074,
                        -413.76671598,
                        366.66127719,
                        136.7228888,
                        -210.69313998,
                        -465.59967482,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                    ],
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                    ],
                ],
                [
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                    ],
                    [
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                    ],
                    [
                        -148.70447678,
                        225.27562348,
                        -273.51318785,
                        -5.32043612,
                        -55.97783429,
                        413.32948686,
                        165.64239994,
                        322.63703294,
                        -2.2348818,
                        0.0,
                        0.0,
                        0.0,
                    ],
                    [
                        -317.48515644,
                        -237.70246887,
                        238.69661676,
                        94.56942257,
                        346.13786088,
                        -7.93209392,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                    ],
                    [
                        7.77508859,
                        260.16762947,
                        -171.02427873,
                        -20.46326319,
                        179.43194042,
                        485.07810635,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                        0.0,
                    ],
                ],
            ]
        ),
        display_data={
            "H": DisplayData(
                name="H",
                display_type=DISPLAY_TYPE.SPHERE,
            ),
            "A": DisplayData(
                name="A",
                display_type=DISPLAY_TYPE.FIBER,
            ),
            "C": DisplayData(
                name="C",
                display_type=DISPLAY_TYPE.FIBER,
            ),
            "X": DisplayData(
                name="X",
                display_type=DISPLAY_TYPE.SPHERE,
            ),
            "J": DisplayData(
                name="J",
                display_type=DISPLAY_TYPE.FIBER,
            ),
            "L": DisplayData(
                name="L",
                display_type=DISPLAY_TYPE.FIBER,
            ),
            "D": DisplayData(
                name="D",
                display_type=DISPLAY_TYPE.SPHERE,
            ),
            "U": DisplayData(
                name="U",
                display_type=DISPLAY_TYPE.FIBER,
            ),
            "E": DisplayData(
                name="E",
                display_type=DISPLAY_TYPE.SPHERE,
            ),
            "Q": DisplayData(
                name="Q",
                display_type=DISPLAY_TYPE.SPHERE,
            ),
            "K": DisplayData(
                name="K",
                display_type=DISPLAY_TYPE.FIBER,
            ),
        },
    ),
    time_units=UnitData("s"),
    spatial_units=UnitData("um"),
    plots=["plot data goes here"],
)


def assert_buffers_equal(
    test_buffer: Dict[str, Any],
    expected_buffer: Dict[str, Any],
):
    assert test_buffer["trajectoryInfo"] == expected_buffer["trajectoryInfo"]
    assert (
        test_buffer["spatialData"]["version"]
        == expected_buffer["spatialData"]["version"]
    )
    assert (
        test_buffer["spatialData"]["msgType"]
        == expected_buffer["spatialData"]["msgType"]
    )
    assert (
        test_buffer["spatialData"]["bundleStart"]
        == expected_buffer["spatialData"]["bundleStart"]
    )
    assert (
        test_buffer["spatialData"]["bundleSize"]
        == expected_buffer["spatialData"]["bundleSize"]
    )
    for frame_index in range(len(test_buffer["spatialData"]["bundleData"])):
        test_frame = test_buffer["spatialData"]["bundleData"][frame_index]
        expected_frame = expected_buffer["spatialData"]["bundleData"][frame_index]
        assert test_frame["frameNumber"] == expected_frame["frameNumber"]
        assert test_frame["time"] == expected_frame["time"]
        assert False not in np.isclose(
            np.array(test_frame["data"]), np.array(expected_frame["data"])
        )
    assert test_buffer["plotData"] == expected_buffer["plotData"]
