import numpy as np
import copy

from simulariumio import AgentData


def test_agent_data_jagged_list():
    times = [0.0, 0.1, 0.2]
    n_agents = [3, 4, 3]
    types = [
        ["H", "A", "C"],
        ["L", "D", "A", "U"],
        ["E", "Q", "K"],
    ]
    list_data = AgentData(
        times=times,
        n_agents=n_agents,
        viz_types=[
            [1000.0, 1001.0, 1001.0],
            [1001.0, 1000.0, 1001.0, 1001.0],
            [1000.0, 1000.0, 1001.0],
        ],
        unique_ids=[
            [0.0, 1.0, 2.0],
            [0.0, 1.0, 2.0, 3.0],
            [0.0, 1.0, 2.0],
        ],
        types=types,
        positions=[
            [
                [4.89610492, -29.81564851, 40.77254057],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
            ],
            [
                [0.0, 0.0, 0.0],
                [-43.37181102, -13.41127423, -17.31316927],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
            ],
            [
                [-24.91450698, -44.79360525, 13.32273796],
                [4.10861266, 43.86451151, 21.93697483],
                [0.0, 0.0, 0.0],
            ],
        ],
        radii=[
            [8.38656327, 1.0, 1.0],
            [1.0, 6.69209780, 1.0, 1.0],
            [8.91022619, 9.01379396, 1.0],
        ],
    )

    expected_results = AgentData(
        times=np.array(times),
        n_agents=np.array(n_agents),
        viz_types=np.array(
            [
                [1000.0, 1001.0, 1001.0, 1000.0],
                [1001.0, 1000.0, 1001.0, 1001.0],
                [1000.0, 1000.0, 1001.0, 1000.0],
            ],
        ),
        unique_ids=np.array(
            [
                [0.0, 1.0, 2.0, 0.0],
                [0.0, 1.0, 2.0, 3.0],
                [0.0, 1.0, 2.0, 0.0],
            ],
        ),
        types=types,
        positions=np.array(
            [
                [
                    [4.89610492, -29.81564851, 40.77254057],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                ],
                [
                    [0.0, 0.0, 0.0],
                    [-43.37181102, -13.41127423, -17.31316927],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                ],
                [
                    [-24.91450698, -44.79360525, 13.32273796],
                    [4.10861266, 43.86451151, 21.93697483],
                    [0.0, 0.0, 0.0],
                    [0.0, 0.0, 0.0],
                ],
            ],
        ),
        radii=np.array(
            [
                [8.38656327, 1.0, 1.0, 0.0],
                [1.0, 6.69209780, 1.0, 1.0],
                [8.91022619, 9.01379396, 1.0, 0.0],
            ],
        ),
    )
    assert expected_results == list_data


def test_from_list_with_scale_factor():
    times = [0.0, 0.1, 0.2]
    n_agents = [3, 3, 3]
    viz_types = [
        [1000.0, 1001.0, 1001.0],
        [1001.0, 1000.0, 1001.0],
        [1000.0, 1000.0, 1001.0],
    ]
    unique_ids = [
        [0.0, 1.0, 2.0],
        [0.0, 1.0, 2.0],
        [0.0, 1.0, 2.0],
    ]
    types = [
        ["H", "A", "C"],
        ["L", "D", "A"],
        ["E", "Q", "K"],
    ]
    positions = [
        [
            [0.489610492, -2.981564851, 4.077254057],
            [0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0],
        ],
        [
            [0.0, 0.0, 0.0],
            [-4.337181102, -1.341127423, -1.731316927],
            [0.0, 0.0, 0.0],
        ],
        [
            [-2.491450698, -4.479360525, 1.332273796],
            [0.410861266, 4.386451151, 2.193697483],
            [0.0, 0.0, 0.0],
        ],
    ]
    radii = [
        [0.838656327, 0.1, 0.1],
        [0.1, 0.669209780, 0.1],
        [0.891022619, 0.901379396, 0.1],
    ]

    list_data = AgentData(
        times=times,
        n_agents=n_agents,
        viz_types=viz_types,
        unique_ids=unique_ids,
        types=types,
        positions=positions,
        radii=radii,
    )

    expected_results = AgentData(
        times=np.array(times),
        n_agents=np.array(n_agents),
        viz_types=np.array(viz_types),
        unique_ids=np.array(unique_ids),
        types=types,
        positions=np.array(positions),
        radii=np.array(radii),
    )

    assert expected_results == list_data


def test_jagged_data_subpoints():
    times = [0.0, 1.00001, 2.00001]
    n_agents = [3, 3, 3]
    viz_types_array = 1001.0 * np.ones(shape=(3, 3))
    unique_ids = [[1.0, 2.0, 3.0], [1.0, 2.0, 3.0], [1.0, 2.0, 3.0]]
    types = [["H", "A", "C"], ["L", "D", "A"], ["K", "K", "A"]]
    positions_array = np.zeros(shape=(3, 3, 3))
    radii_array = np.ones(shape=(3, 3))
    n_subpoints = [[9, 12, 6], [9, 9, 6], [9, 6, 6]]
    jagged_subpoints = [
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
            ],
        ],
    ]

    list_data = AgentData(
        times=times,
        n_agents=n_agents,
        viz_types=viz_types_array.tolist(),
        unique_ids=unique_ids,
        types=types,
        positions=positions_array.tolist(),
        radii=radii_array.tolist(),
        n_subpoints=n_subpoints,
        subpoints=jagged_subpoints,
    )

    # make subpoint data not jagged for AgentData
    subpoints = copy.deepcopy(jagged_subpoints)
    subpoints[0][0].extend([0.0, 0.0])
    subpoints[0][2].append(0.0)
    subpoints[1][1].extend([0.0, 0.0, 0.0])
    subpoints[2][2].extend([0.0, 0.0, 0.0, 0.0, 0.0])

    expected_results = AgentData(
        times=np.array(times),
        n_agents=np.array(n_agents),
        viz_types=viz_types_array,
        unique_ids=np.array(unique_ids),
        types=types,
        positions=positions_array,
        radii=radii_array,
        n_subpoints=np.array(n_subpoints),
        subpoints=np.array(subpoints),
    )

    assert expected_results == list_data
