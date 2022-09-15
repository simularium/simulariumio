#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import numpy as np

from simulariumio import HistogramPlotData, UnitData, MetaData, DisplayData, JsonWriter
from simulariumio.readdy import ReaddyConverter, ReaddyData
from simulariumio.constants import CURRENT_VERSION, DISPLAY_TYPE


@pytest.mark.parametrize(
    "trajectory, plot_data1, plot_data2, expected_data",
    [
        (
            # histogram plot with multiple traces
            ReaddyData(
                meta_data=MetaData(
                    box_size=np.array([20.0, 20.0, 20.0]),
                ),
                timestep=0.1,
                path_to_readdy_h5="simulariumio/tests/data/readdy/test.h5",
                display_data={
                    "A": DisplayData(
                        name="C",
                        display_type=DISPLAY_TYPE.SPHERE,
                        radius=3.0,
                        color="#0080ff",
                    ),
                    "B": DisplayData(
                        name="B",
                        radius=2.0,
                        display_type=DISPLAY_TYPE.OBJ,
                        url="c.obj",
                        color="#dfdacd",
                    ),
                    "D": DisplayData(
                        name="C",
                        display_type=DISPLAY_TYPE.SPHERE,
                        radius=3.0,
                        color="#0080ff",
                    ),
                },
                ignore_types=["E"],
                time_units=UnitData("ms", 1e-6),
                spatial_units=UnitData("nm"),
            ),
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
                "version": CURRENT_VERSION.PLOT_DATA,
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
    converter = ReaddyConverter(trajectory)
    converter.add_plot(plot_data1, "histogram")
    converter.add_plot(plot_data2, "histogram")
    buffer_data = JsonWriter.format_trajectory_data(converter._data)
    assert expected_data == buffer_data["plotData"]
