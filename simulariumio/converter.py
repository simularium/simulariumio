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
from .plot_readers import (
    HistogramPlotReader,
    ScatterPlotReader,
    PlotReader,
)
from .data_objects.agent_data import AgentData
from .constants import V1_SPATIAL_BUFFER_STRUCT, VIZ_TYPE

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
            buffer_size = (len(V1_SPATIAL_BUFFER_STRUCT) - 1) * n_agents
            for n in range(n_agents):
                s = int(agent_data.n_subpoints[t][n])
                if s > 0:
                    buffer_size += 3 * s
                    if agent_data.draw_fiber_points:
                        buffer_size += (len(V1_SPATIAL_BUFFER_STRUCT) - 1) * max(
                            math.ceil(s / 2.0), 1
                        )
            local_buf = np.zeros(buffer_size)
            for n in range(n_agents):
                # add agent
                local_buf[
                    i + V1_SPATIAL_BUFFER_STRUCT.index("VIZ_TYPE")
                ] = agent_data.viz_types[t, n]
                local_buf[
                    i + V1_SPATIAL_BUFFER_STRUCT.index("UID")
                ] = agent_data.unique_ids[t, n]
                local_buf[
                    i + V1_SPATIAL_BUFFER_STRUCT.index("TID")
                ] = agent_data.type_ids[t, n]
                local_buf[
                    i
                    + V1_SPATIAL_BUFFER_STRUCT.index("POSX") : i
                    + V1_SPATIAL_BUFFER_STRUCT.index("POSX")
                    + 3
                ] = agent_data.positions[t, n]
                local_buf[i + V1_SPATIAL_BUFFER_STRUCT.index("R")] = (
                    agent_data.radii[t, n]
                    if abs(float(agent_data.viz_types[t, n]) - VIZ_TYPE.default)
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
                    local_buf[
                        i
                        + V1_SPATIAL_BUFFER_STRUCT.index("NSP") : i
                        + V1_SPATIAL_BUFFER_STRUCT.index("NSP")
                        + 1
                        + 3 * n_subpoints
                    ] = subpoints
                    i += (len(V1_SPATIAL_BUFFER_STRUCT) - 1) + 3 * n_subpoints
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
                            local_buf[
                                i + V1_SPATIAL_BUFFER_STRUCT.index("VIZ_TYPE")
                            ] = VIZ_TYPE.default
                            local_buf[i + V1_SPATIAL_BUFFER_STRUCT.index("UID")] = uids[
                                raw_uid
                            ]
                            local_buf[
                                i + V1_SPATIAL_BUFFER_STRUCT.index("TID")
                            ] = agent_data.type_ids[t, n]
                            local_buf[
                                i
                                + V1_SPATIAL_BUFFER_STRUCT.index("POSX") : i
                                + V1_SPATIAL_BUFFER_STRUCT.index("POSX")
                                + 3
                            ] = agent_data.subpoints[t][n][p]
                            local_buf[i + V1_SPATIAL_BUFFER_STRUCT.index("R")] = 0.5
                            i += len(V1_SPATIAL_BUFFER_STRUCT) - 1
                else:
                    i += len(V1_SPATIAL_BUFFER_STRUCT) - 1
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
            ix_particles[3 * i : 3 * i + 3] = np.arange(
                i * (len(V1_SPATIAL_BUFFER_STRUCT) - 1)
                + V1_SPATIAL_BUFFER_STRUCT.index("POSX"),
                i * (len(V1_SPATIAL_BUFFER_STRUCT) - 1)
                + V1_SPATIAL_BUFFER_STRUCT.index("POSX")
                + 3,
            )
        frame_buf = np.zeros((len(V1_SPATIAL_BUFFER_STRUCT) - 1) * max_n_agents)
        for t in range(len(agent_data.times)):
            frame_data = {}
            frame_data["frameNumber"] = t
            frame_data["time"] = float(agent_data.times[t])
            n = int(agent_data.n_agents[t])
            local_buf = frame_buf[: (len(V1_SPATIAL_BUFFER_STRUCT) - 1) * n]
            local_buf[
                V1_SPATIAL_BUFFER_STRUCT.index("VIZ_TYPE") :: len(
                    V1_SPATIAL_BUFFER_STRUCT
                )
                - 1
            ] = agent_data.viz_types[t, :n]
            local_buf[
                V1_SPATIAL_BUFFER_STRUCT.index("UID") :: len(V1_SPATIAL_BUFFER_STRUCT)
                - 1
            ] = agent_data.unique_ids[t, :n]
            local_buf[
                V1_SPATIAL_BUFFER_STRUCT.index("TID") :: len(V1_SPATIAL_BUFFER_STRUCT)
                - 1
            ] = agent_data.type_ids[t, :n]
            local_buf[ix_particles[: 3 * n]] = agent_data.positions[t, :n].flatten()
            local_buf[
                V1_SPATIAL_BUFFER_STRUCT.index("R") :: len(V1_SPATIAL_BUFFER_STRUCT) - 1
            ] = agent_data.radii[t, :n]
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
            i = 1
            uids = []
            get_n_subpoints = False
            while i < len(data):
                # get the number of subpoints
                # in order to correctly increment index
                if get_n_subpoints:
                    i += int(
                        data[i]
                        + (
                            len(V1_SPATIAL_BUFFER_STRUCT)
                            - V1_SPATIAL_BUFFER_STRUCT.index("NSP")
                        )
                    )
                    get_n_subpoints = False
                    continue
                # there should be a unique ID at this index, check for duplicate
                uid = data[i]
                if uid in uids:
                    raise Exception(
                        f"found duplicate ID {uid} in frame {t} at index {i}"
                    )
                uids.append(uid)
                i += V1_SPATIAL_BUFFER_STRUCT.index("NSP") - 1
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
