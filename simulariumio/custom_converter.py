#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
from typing import Any, Dict, List
import math

import numpy as np

from .plot_readers import (
    HistogramPlotReader,
    ScatterPlotReader,
    PlotReader,
)
from .data_objects import (
    HistogramPlotData,
    ScatterPlotData,
    AgentData,
    CustomData,
)
from .filters import (
    EveryNthAgentFilter,
)
from .filters.params import FilterParams
from .filters.filter import Filter
from .exceptions import (
    UnsupportedPlotTypeError,
    UnsupportedFilterTypeError,
)
from .constants import V1_SPATIAL_BUFFER_STRUCT, VIZ_TYPE

###############################################################################

log = logging.getLogger(__name__)

###############################################################################

SUPPORTED_PLOT_READERS = {
    "scatter": ScatterPlotReader,
    "histogram": HistogramPlotReader,
}

FILTERS = {
    "every_nth_agent": EveryNthAgentFilter,
}

###############################################################################


class CustomConverter:
    _data: Dict[str, Any] = {}

    def __init__(self, input_data: CustomData):
        """
        This object reads custom simulation trajectory outputs
        and plot data and writes them in the JSON format used
        by the Simularium viewer

        Parameters
        ----------
        input_data : CustomData
            An object containing custom simulation trajectory outputs
            and plot data
        """
        self._data = self._read_custom_data(input_data)
        self._check_agent_ids_are_unique_per_frame()

    def _read_custom_data(self, input_data: CustomData) -> Dict[str, Any]:
        """
        Return an object containing the data shaped for Simularium format
        """
        print("Reading Custom Data -------------")
        simularium_data = {}
        # trajectory info
        totalSteps = input_data.agent_data.times.size

        type_mapping = input_data.agent_data.get_type_mapping()
        traj_info = {
            "version": 2,
            "timeUnits": {
                "magnitude": input_data.time_units.magnitude,
                "name": input_data.time_units.name,
            },
            "timeStepSize": CustomConverter._format_timestep(
                float(input_data.agent_data.times[2] - input_data.agent_data.times[1])
                if totalSteps > 2
                else float(
                    input_data.agent_data.times[1] - input_data.agent_data.times[0]
                )
                if totalSteps > 1
                else 0.0
            ),
            "totalSteps": totalSteps,
            "spatialUnits": {
                "magnitude": input_data.spatial_units.magnitude,
                "name": input_data.spatial_units.name,
            },
            "size": {
                "x": float(input_data.box_size[0]),
                "y": float(input_data.box_size[1]),
                "z": float(input_data.box_size[2]),
            },
            "typeMapping": type_mapping,
        }
        simularium_data["trajectoryInfo"] = traj_info
        # spatial data
        spatialData = {
            "version": 1,
            "msgType": 1,
            "bundleStart": 0,
            "bundleSize": totalSteps,
        }
        if input_data.agent_data.subpoints is not None:
            spatialData["bundleData"] = self._get_spatial_bundle_data_subpoints(
                input_data.agent_data
            )
        else:
            spatialData["bundleData"] = self._get_spatial_bundle_data_no_subpoints(
                input_data.agent_data
            )
        simularium_data["spatialData"] = spatialData
        # plot data
        simularium_data["plotData"] = {
            "version": 1,
            "data": input_data.plots,
        }
        return simularium_data

    @staticmethod
    def _get_spatial_bundle_data_subpoints(
        agent_data: AgentData, used_unique_IDs: List[int] = []
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
                local_buf[i + V1_SPATIAL_BUFFER_STRUCT.index("R")] = agent_data.radii[
                    t, n
                ]
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

    @staticmethod
    def _get_spatial_bundle_data_no_subpoints(
        agent_data: AgentData,
    ) -> List[Dict[str, Any]]:
        """
        Return the spatialData's bundleData for a simulation
        of agents without subpoints, using list slicing for speed
        """
        bundleData: List[Dict[str, Any]] = []
        max_n_agents = int(np.amax(agent_data.n_agents, 0))
        ix_positions = np.empty((3 * max_n_agents,), dtype=int)
        for i in range(max_n_agents):
            ix_positions[3 * i : 3 * i + 3] = np.arange(
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
            local_buf[ix_positions[: 3 * n]] = agent_data.positions[t, :n].flatten()
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
    def _format_timestep(number: float):
        return float("%.4g" % number)

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

    @staticmethod
    def _determine_filter(filter_type: str) -> [Filter]:
        """
        Return the filter to match the requested filter type
        """
        if filter_type in FILTERS:
            return FILTERS[filter_type]

        raise UnsupportedFilterTypeError(filter_type)

    def apply_filters(self, params: List[FilterParams]):
        """
        Apply the given filter to the simularium data

        Parameters
        ----------
        params: List[FilterParams]
            a list of filter parameters, one for each filter to be applied
        """
        box_size = self._data["trajectoryInfo"]["size"]
        plot_data = self._data["plotData"]
        agent_data = AgentData.from_simularium_data(self._data)
        for i in range(len(params)):
            filter_class = self._determine_filter(params[i].name)
            agent_data = filter_class().filter_spatial_data(agent_data, params[i])
        self._data = self._read_custom_data(
            CustomData(
                spatial_unit_factor_meters=self._data["trajectoryInfo"][
                    "spatialUnitFactorMeters"
                ],
                box_size=np.array(
                    [float(box_size["x"]), float(box_size["y"]), float(box_size["z"])]
                ),
                agent_data=agent_data,
            )
        )
        self._data["plotData"] = plot_data

    def write_JSON(self, output_path: str):
        """
        Save the data in .simularium JSON format at the output path

        Parameters
        ----------
        output_path: str
            where to save the file
        """
        print("Writing JSON -------------")
        with open(f"{output_path}.simularium", "w+") as outfile:
            json.dump(self._data, outfile)
        print(f"saved to {output_path}.simularium")
