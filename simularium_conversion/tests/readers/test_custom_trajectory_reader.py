#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simple example of a test file using a function.
NOTE: All test file names must have one of the two forms.
- `test_<XYY>.py`
- '<XYZ>_test.py'

Docs: https://docs.pytest.org/en/latest/
      https://docs.pytest.org/en/latest/goodpractices.html#conventions-for-python-test-discovery
"""

from string import ascii_uppercase
from random import choice

import pytest
import numpy as np

from ...simularium_conversion import Converter


# The best practice would be to parametrize your tests, and include tests for any
# exceptions that would occur
@pytest.mark.parametrize(
    "trajectory", "source_engine", "expected_data",
    [
        # 3 default agents (radius 5-10) at given positions for 5 frames, 
        # test string for plots
        ({ 
            'box_size' : np.array([100.0, 100.0, 100.0]),
            'times' : 0.5 * np.array(list(range(3))),
            'n_agents' : np.array(3 * [3]),
            'viz_types' : np.array(3 * (3 * [1000.0])),
            'positions' : np.array([
                [
                    [  4.89610492, -29.81564851,  40.77254057],
                    [ 43.43048197,  48.00424379, -36.02881338],
                    [ 29.84924588, -38.02769707,   2.46644825]
                ],
                [
                    [-43.37181102, -13.41127423, -17.31316927],
                    [  9.62132397,  13.4774314 , -20.30846039],
                    [ 41.41039848, -45.85543786,  49.06208485]
                ],
                [
                    [-24.91450698, -44.79360525,  13.32273796],
                    [  4.10861266,  43.86451151,  21.93697483],
                    [ -7.16740679, -13.06491594,  44.97026158]
                ]
            ]),
            'types' : [
                ['C', 'U', 'C'],
                ['U', 'L', 'S'],
                ['O', 'Y', 'W']
            ],
            'radii' : np.array([
                [8.38656327, 6.18568039, 6.61459206],
                [5.26366739, 6.6920978 , 9.88033853],
                [8.91022619, 9.01379396, 8.39880154]
            ]),
            'plots' : 'plot data goes here'
        },
        'custom',
        {
            'trajectoryInfo' : {
                'version' : 1,
                'timeStepSize' : 0.5,
                'totalSteps' : 3,
                'size' : {
                    'x' : 100.0,
                    'y' : 100.0,
                    'z' : 100.0
                },
                'nAgentTypes' : 7, 
                '0' : {
                    'name' : 'C'
                },
                '1' : {
                    'name' : 'U'
                },
                '2' : {
                    'name' : 'L'
                },
                '3' : {
                    'name' : 'S'
                },
                '4' : {
                    'name' : 'O'
                },
                '5' : {
                    'name' : 'Y'
                },
                '6' : {
                    'name' : 'W'
                }
            },
            'spatialData' : {
                'version' : 1,
                'msgType' : 1,
                'bundleStart' : 0,
                'bundleSize' : 3,
                'bundleData': [
                    { 
                        'frameNumber' : 0, 
                        'time' : 0, 
                        'data' : [
                            1000.0, 0.0, 4.89610492, -29.81564851, 40.77254057, 0.0, 0.0, 0.0, 8.38656327, 0.0,
                            1000.0, 1.0, 43.43048197, 48.00424379, -36.02881338, 0.0, 0.0, 0.0, 6.18568039, 0.0,
                            1000.0, 0.0, 29.84924588, -38.02769707, 2.46644825, 0.0, 0.0, 0.0, 6.61459206, 0.0,
                        ] 
                    },
                    { 
                        'frameNumber' : 0, 
                        'time' : 0, 
                        'data' : [
                            1000.0, 1.0, -43.37181102, -13.41127423, -17.31316927, 0.0, 0.0, 0.0, 5.26366739, 0.0,
                            1000.0, 2.0, 9.62132397, 13.4774314, -20.30846039, 0.0, 0.0, 0.0, 6.6920978, 0.0,
                            1000.0, 3.0, 41.41039848, -45.85543786, 49.06208485, 0.0, 0.0, 0.0, 9.88033853, 0.0,
                        ] 
                    },
                    { 
                        'frameNumber' : 0, 
                        'time' : 0, 
                        'data' : [
                            1000.0, 4.0, -24.91450698, -44.79360525, 13.32273796, 0.0, 0.0, 0.0, 8.91022619, 0.0,
                            1000.0, 5.0, 4.10861266, 43.86451151, 21.93697483, 0.0, 0.0, 0.0, 9.01379396, 0.0,
                            1000.0, 6.0, -7.16740679, -13.06491594, 44.97026158, 0.0, 0.0, 0.0, 8.39880154, 0.0,
                        ] 
                    }
                ]
            },
            'plotData' : 'plot data goes here'
        })
        # pytest.param(
        #     "hello",
        #     None,
        #     None,
        #     marks=pytest.mark.raises(
        #         exception=ValueError
        #     ),  # Init value isn't an integer
        # ),
    ],
)
def test_custom_trajectory_reader(
    trajectory, source_engine, expected_data
):
    converter = Converter(trajectory)
    assert expected_data == converter._data
