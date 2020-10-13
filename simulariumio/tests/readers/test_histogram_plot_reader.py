#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np

from simulariumio import CustomConverter, HistogramPlotData
from simulariumio.tests.conftest import three_default_agents


@pytest.mark.parametrize(
    "trajectory, plot_data1, plot_data2, expected_data",
    [
        (
            # histogram plot with multiple traces
            three_default_agents(),
            HistogramPlotData(
                title="Test Histogram 1",
                xaxis_title="angle (degrees)",
                traces={
                    "crosslinked monomers": np.array(
                        [
                            0.0,
                            1.0,
                            2.0,
                            3.0,
                            4.0,
                            5.0,
                            6.0,
                            7.0,
                            8.0,
                            9.0,
                            3.0,
                            4.0,
                            3.0,
                            7.0,
                            5.0,
                            3.0,
                            6.0,
                            5.0,
                            2.0,
                            4.0,
                        ]
                    ),
                    "bent monomers": np.array(
                        [
                            10.0,
                            10.0,
                            20.0,
                            30.0,
                            40.0,
                            50.0,
                            60.0,
                            70.0,
                            80.0,
                            90.0,
                            30.0,
                            40.0,
                            30.0,
                            70.0,
                            50.0,
                            30.0,
                            60.0,
                            50.0,
                            20.0,
                            40.0,
                        ]
                    ),
                },
            ),
            HistogramPlotData(
                title="Test Histogram 2",
                xaxis_title="concentrations (uM)",
                traces={
                    "agent1": np.array(
                        [
                            0.0,
                            1.0,
                            2.0,
                            3.0,
                            4.0,
                            5.0,
                            6.0,
                            7.0,
                            8.0,
                            9.0,
                            3.0,
                            4.0,
                            3.0,
                            7.0,
                            5.0,
                            3.0,
                            6.0,
                            5.0,
                            2.0,
                            4.0,
                        ]
                    ),
                },
            ),
            {
                "version": 1,
                "data": [
                    {
                        "layout": {
                            "title": "Test Histogram 1",
                            "xaxis": {"title": "angle (degrees)"},
                            "yaxis": {"title": "frequency"},
                        },
                        "data": [
                            {
                                "name": "crosslinked monomers",
                                "type": "histogram",
                                "x": [
                                    0.0,
                                    1.0,
                                    2.0,
                                    3.0,
                                    4.0,
                                    5.0,
                                    6.0,
                                    7.0,
                                    8.0,
                                    9.0,
                                    3.0,
                                    4.0,
                                    3.0,
                                    7.0,
                                    5.0,
                                    3.0,
                                    6.0,
                                    5.0,
                                    2.0,
                                    4.0,
                                ],
                            },
                            {
                                "name": "bent monomers",
                                "type": "histogram",
                                "x": [
                                    10.0,
                                    10.0,
                                    20.0,
                                    30.0,
                                    40.0,
                                    50.0,
                                    60.0,
                                    70.0,
                                    80.0,
                                    90.0,
                                    30.0,
                                    40.0,
                                    30.0,
                                    70.0,
                                    50.0,
                                    30.0,
                                    60.0,
                                    50.0,
                                    20.0,
                                    40.0,
                                ],
                            },
                        ],
                    },
                    {
                        "layout": {
                            "title": "Test Histogram 2",
                            "xaxis": {"title": "concentrations (uM)"},
                            "yaxis": {"title": "frequency"},
                        },
                        "data": [
                            {
                                "name": "agent1",
                                "type": "histogram",
                                "x": [
                                    0.0,
                                    1.0,
                                    2.0,
                                    3.0,
                                    4.0,
                                    5.0,
                                    6.0,
                                    7.0,
                                    8.0,
                                    9.0,
                                    3.0,
                                    4.0,
                                    3.0,
                                    7.0,
                                    5.0,
                                    3.0,
                                    6.0,
                                    5.0,
                                    2.0,
                                    4.0,
                                ],
                            },
                        ],
                    },
                ],
            },
        ),
    ],
)
def test_add_two_histogram_plots(trajectory, plot_data1, plot_data2, expected_data):
    converter = CustomConverter(trajectory)
    converter.add_plot(plot_data1, "histogram")
    converter.add_plot(plot_data2, "histogram")
    raise Exception(converter._data["plotData"]["data"][0])
    assert expected_data["data"][0]["layout"] == converter._data["plotData"]["data"][0]["layout"]
