#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from typing import Any, Dict, List
import sys
import math

import numpy as np

from .exceptions import UnsupportedPlotTypeError
from .data_objects import (
    HistogramPlotData,
    ScatterPlotData,
)
from .readers import (
    HistogramPlotReader,
    ScatterPlotReader,
)
from .readers.plot_reader import PlotReader
from .data_objects.agent_data import AgentData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################

SUPPORTED_PLOT_READERS = {
    "scatter": ScatterPlotReader,
    "histogram": HistogramPlotReader,
}

###############################################################################


class Converter:
    _data: Dict[str, Any] = {}

    def _get_spatial_bundle_data_subpoints(
        self, agent_data: AgentData, used_unique_IDs: List[int] = []
    ) -> List[Dict[str, Any]]:
        """
        Return the spatialData's bundleData for a simulation
        of agents with subpoints, packing buffer with jagged data is slower
        """
        bundleData: List[Dict[str, Any]] = []
        uids = {}
        for t in range(len(agent_data.times)):
            # timestep
            frame_data = {}
            frame_data["frameNumber"] = t
            frame_data["time"] = float(agent_data.times[t])
            n_agents = int(agent_data.n_agents[t])
            i = 0
            buffer_size = 11 * n_agents
            for n in range(n_agents):
                s = int(agent_data.n_subpoints[t][n])
                if s > 0:
                    buffer_size += 3 * s
                    if agent_data.draw_fiber_points:
                        buffer_size += 11 * max(math.ceil(s / 2.0), 1)
            local_buf = np.zeros(buffer_size)
            for n in range(n_agents):
                # add agent
                local_buf[i] = agent_data.viz_types[t, n]
                local_buf[i + 1] = agent_data.unique_ids[t, n]
                local_buf[i + 2] = agent_data.type_ids[t, n]
                local_buf[i + 3 : i + 6] = agent_data.positions[t, n]
                local_buf[i + 9] = (
                    agent_data.radii[t, n]
                    if abs(float(agent_data.viz_types[t, n]) - 1000.0)
                    < sys.float_info.epsilon
                    else 1.0
                )
                n_subpoints = int(agent_data.n_subpoints[t][n])
                if n_subpoints > 0:
                    # add subpoints to fiber agent
                    subpoints = [3 * n_subpoints]
                    for p in range(n_subpoints):
                        for d in range(3):
                            subpoints.append(agent_data.subpoints[t][n][p][d])
                    local_buf[i + 10 : i + 11 + 3 * n_subpoints] = subpoints
                    i += 11 + 3 * n_subpoints
                    # optionally draw spheres at points
                    if agent_data.draw_fiber_points:
                        for p in range(n_subpoints):
                            # every other fiber point
                            if p % 2 != 0:
                                continue
                            # unique instance ID
                            raw_uid = 100 * (agent_data.unique_ids[t, n] + 1) + p
                            if raw_uid not in uids:
                                uid = raw_uid
                                while uid in used_unique_IDs:
                                    uid += 100
                                uids[raw_uid] = uid
                                used_unique_IDs.append(uid)
                            # add sphere
                            local_buf[i] = 1000.0
                            local_buf[i + 1] = uids[raw_uid]
                            local_buf[i + 2] = agent_data.type_ids[t, n]
                            local_buf[i + 3 : i + 6] = agent_data.subpoints[t][n][p]
                            local_buf[i + 9] = 0.5
                            i += 11
                else:
                    i += 11
            frame_data["data"] = local_buf.tolist()
            bundleData.append(frame_data)
        return bundleData

    def _get_spatial_bundle_data_no_subpoints(
        self, agent_data: AgentData
    ) -> List[Dict[str, Any]]:
        """
        Return the spatialData's bundleData for a simulation
        of agents without subpoints, using list slicing for speed
        """
        bundleData: List[Dict[str, Any]] = []
        max_n_agents = int(np.amax(agent_data.n_agents, 0))
        ix_particles = np.empty((3 * max_n_agents,), dtype=int)
        for i in range(max_n_agents):
            ix_particles[3 * i : 3 * i + 3] = np.arange(i * 11 + 3, i * 11 + 3 + 3)
        frame_buf = np.zeros(11 * max_n_agents)
        for t in range(len(agent_data.times)):
            frame_data = {}
            frame_data["frameNumber"] = t
            frame_data["time"] = float(agent_data.times[t])
            n = int(agent_data.n_agents[t])
            local_buf = frame_buf[: 11 * n]
            local_buf[0::11] = agent_data.viz_types[t, :n]
            local_buf[1::11] = agent_data.unique_ids[t, :n]
            local_buf[2::11] = agent_data.type_ids[t, :n]
            local_buf[ix_particles[: 3 * n]] = agent_data.positions[t, :n].flatten()
            local_buf[9::11] = agent_data.radii[t, :n]
            frame_data["data"] = local_buf.tolist()
            bundleData.append(frame_data)
        return bundleData

    def _check_agent_ids_are_unique_per_frame(self) -> bool:
        """
        For each frame, check that none of the unique agent IDs overlap
        """
        bundleData = self._data["spatialData"]["bundleData"]
        for t in range(len(bundleData)):
            data = bundleData[t]["data"]
            next_uid_index = 1
            uids = []
            get_n_subpoints = False
            for i in range(len(data)):
                if i == next_uid_index:
                    # get the number of subpoints
                    # in order to correctly increment next_uid_index
                    if get_n_subpoints:
                        next_uid_index += data[i] + 2
                        get_n_subpoints = False
                        continue
                    # there should be a unique ID at this index, check for duplicate
                    uid = data[i]
                    if uid in uids:
                        raise Exception(
                            f"found duplicate ID {uid} in frame {t} at index {i}"
                        )
                    uids.append(uid)
                    next_uid_index += 9
                    get_n_subpoints = True
        return True

    @staticmethod
    def _determine_plot_reader(plot_type: str = "scatter") -> [PlotReader]:
        """
        Return the plot reader to match the requested plot type
        """
        if plot_type in SUPPORTED_PLOT_READERS:
            return SUPPORTED_PLOT_READERS[plot_type]

        raise UnsupportedPlotTypeError(plot_type)

    def add_plot(
        self,
        data: [ScatterPlotData or HistogramPlotData] = {},
        plot_type: str = "scatter",
    ):
        """
        Add data to be rendered in a plot

        Parameters
        ----------
        data: ScatterPlotData or HistogramPlotData
            Loaded data for a plot.
        plot_type: str
            A string specifying which type of plot to render.
            Current options:
                'scatter' : a scatterplot with y-trace(s) dependent
                    on an x-trace
                'histogram' : a histogram with bars drawn at intervals
                    over the range(s) of the data, with their height
                    corresponding to the number of values in each interval
            Default: 'scatter'
        """
        plot_reader_class = self._determine_plot_reader(plot_type)
        self._data["plotData"]["data"].append(plot_reader_class().read(data))

    def write_JSON(self, output_path: str):
        """
        Save the data in .simularium JSON format at the output path

        Parameters
        ----------
        output_path: str
            where to save the file
        """
        with open(f"{output_path}.simularium", "w+") as outfile:
            json.dump(self._data, outfile)
