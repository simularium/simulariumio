#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any
import json

from .exceptions import UnsupportedSourceEngineError, UnsupportedPlotTypeError
from .readers import (
    CustomTrajectoryReader,
    CytosimTrajectoryReader,
    ScatterPlotReader,
    HistogramPlotReader,
)
from .readers.reader import Reader

###############################################################################

log = logging.getLogger(__name__)

###############################################################################

SUPPORTED_TRAJECTORY_READERS = {
    "custom": CustomTrajectoryReader,
    "cytosim": CytosimTrajectoryReader,
}

SUPPORTED_PLOT_READERS = {
    "scatter": ScatterPlotReader,
    "histogram": HistogramPlotReader,
}

###############################################################################


class Converter:
    _data: Dict[str, Any] = {}

    def __init__(self, data: Dict[str, Any] = {}, source_engine: str = "custom"):
        """
        This object reads simulation trajectory outputs from various engines 
        (as well as custom data) and plot data and writes them 
        in the JSON format used by the Simularium viewer.

        Parameters
        ----------
        data: Dict[str, Any]
            Loaded data or path to data from a simulation engine. 
            Fields for each engine:

                custom: 
                    box_size : np.ndarray (shape = [3])
                        A numpy ndarray containing the XYZ dimensions 
                        of the simulation bounding volume
                    times : np.ndarray (shape = [timesteps])
                        A numpy ndarray containing the elapsed simulated time 
                        at each timestep
                    n_agents : np.ndarray (shape = [timesteps])
                        A numpy ndarray containing the number of agents 
                        that exist at each timestep
                    viz_types : np.ndarray (shape = [timesteps, agents])
                        A numpy ndarray containing the viz type 
                        for each agent at each timestep. Current options:
                            1000 : default,
                            1001 : fiber (which will require subpoints)
                    unique_ids : np.ndarray (shape = [timesteps, agents])
                        A numpy ndarray containing the unique ID
                        for each agent at each timestep
                    types: List[List[str]] (list of shape [timesteps, agents])
                        A list containing timesteps, for each a list of 
                        the string name for the type of each agent
                    positions : np.ndarray (shape = [timesteps, agents, 3])
                        A numpy ndarray containing the XYZ position 
                        for each agent at each timestep
                    radii : np.ndarray (shape = [timesteps, agents])
                        A numpy ndarray containing the radius 
                        for each agent at each timestep
                    n_subpoints : np.ndarray (shape = [timesteps, agents]) (optional)
                        A numpy ndarray containing the number of subpoints
                        belonging to each agent at each timestep. Required if
                        subpoints are provided
                    subpoints : np.ndarray 
                    (shape = [timesteps, agents, subpoints, 3]) (optional) 
                        A numpy ndarray containing a list of subpoint position data 
                        for each agent at each timestep. These values are 
                        currently only used for fiber agents.
                    plots : Dict[str, Any] (optional) 
                        An object containing plot data already 
                        in Simularium format

                Cytosim:
                    box_size : np.ndarray (shape = [3])
                        A numpy ndarray containing the XYZ dimensions 
                        of the simulation bounding volume
                    data : Dict[str, Any]
                        fibers : Dict[str, Any]
                            filepath : str
                                path to fiber_points.txt    
                            agents : Dict[str, Any] (optional)
                                [agent type index from Cytosim data] : Dict[str, Any]
                                    the type index from Cytosim data mapped 
                                    to display names for each type of fiber
                                    name : str (optional)
                                        the display name for this type of fiber
                                        Default: "fiber[agent type index 
                                            from Cytosim data]"
                            draw_points : bool (optional)
                                in addition to drawing a line for each fiber,
                                also draw spheres at each point along it?
                                Default: False
                        solids : Dict[str, Any]
                            filepath : str
                                path to solids.txt
                            agents : Dict[str, Any] (optional)
                                [agent type index from Cytosim data] : Dict[str, Any]
                                    the type index from Cytosim data mapped 
                                    to display names and radii for each type of solid
                                    name : str (optional)
                                        the display name for this type of solid
                                        Default: "solid[agent type index 
                                            from Cytosim data]"
                                    radius : float (optional)
                                        the radius for this type of solid
                                        Default: 1.0
                                    position_offset : np.ndarray (shape = [3]) (optional)
                                        XYZ translation to apply to this agent
                                        Default: [0.0, 0.0, 0.0]
                            position_indices : List[int] (optional)
                                the columns in Cytosim's reports are not 
                                always consistent, use this to override them 
                                if your output file has different column indices 
                                for position XYZ
                                Default: [2, 3, 4]
                        singles : Dict[str, Any]
                            filepath : str
                                path to singles.txt
                            agents : Dict[str, Any] (optional)
                                [agent type index from Cytosim data] : Dict[str, Any]
                                    the type index from Cytosim data mapped 
                                    to display names and radii for each type of single
                                    name : str (optional)
                                        the display name for this type of single
                                        Default: "single[agent type index 
                                            from Cytosim data]"
                                    radius : float (optional)
                                        the radius for this type of single
                                        Default: 1.0
                            position_indices : List[int] (optional)
                                the columns in Cytosim's reports are not 
                                always consistent, use this to override them 
                                if your output file has different column indices 
                                for position XYZ
                                Default: [2, 3, 4]
                        couples : Dict[str, Any] (optional)
                            filepath : str
                                path to couples.txt
                            agents : Dict[str, Any] (optional)
                                [agent type index from Cytosim data] : Dict[str, Any]
                                    the type index from Cytosim data mapped 
                                    to display names and radii for each type of couple
                                    name : str (optional)
                                        the display name for this type of couple
                                        Default: "couple[agent type index 
                                            from Cytosim data]"
                                    radius : float (optional)
                                        the radius for this type of couple
                                        Default: 1.0
                            position_indices : List[int] (optional)
                                the columns in Cytosim's reports are not 
                                always consistent, use this to override them 
                                if your output file has different column indices 
                                for position XYZ
                                Default: [2, 3, 4]
                    scale_factor : float (optional)
                        A multiplier for the Cytosim scene, use if 
                        visualization is too large or small
                        Default: 1.0
                    plots : Dict[str, Any] (optional) 
                        An object containing plot data already 
                        in Simularium format

        source_engine: str
            A string specifying which simulation engine created these outputs. 
            Current options:
                'custom' : outputs are from an engine not specifically supported
                'cytosim' : outputs are from CytoSim 
                    (https://gitlab.com/f.nedelec/cytosim)
            Coming Soon:
                'readdy' : outputs are from ReaDDy 
                    (https://readdy.github.io/)
                'physicell' : outputs are from PhysiCell 
                    (http://physicell.org/)
        """
        traj_reader_class = self._determine_trajectory_reader(source_engine)
        self._data = traj_reader_class().read(data)

    @staticmethod
    def _determine_trajectory_reader(source_engine: str = "custom") -> [Reader]:
        """
        Return the trajectory reader to match the requested 
        source simulation engine
        """
        if source_engine in SUPPORTED_TRAJECTORY_READERS:
            return SUPPORTED_TRAJECTORY_READERS[source_engine]

        raise UnsupportedSourceEngineError(source_engine)

    @staticmethod
    def _determine_plot_reader(plot_type: str = "scatter") -> [Reader]:
        """
        Return the plot reader to match the requested plot type
        """
        if plot_type in SUPPORTED_PLOT_READERS:
            return SUPPORTED_PLOT_READERS[plot_type]

        raise UnsupportedPlotTypeError(plot_type)

    def add_plot(self, data: Dict[str, Any] = {}, plot_type: str = "scatter"):
        """
        Add data to be rendered in a plot

        Parameters
        ----------
        data: Dict[str, Any]
            Loaded data for a plot. Fields for each plot type:

                scatter : 
                    title: str
                        A string display title for the plot
                    xaxis_title: str
                        A string label (with units) for the x-axis
                    yaxis_title: str
                        A string label (with units) for the y-axis
                    xtrace: np.ndarray (shape = [x values])
                        A numpy ndarray of values for x, 
                        the independent variable
                    ytraces: Dict[str, np.ndarray (shape = [x values])]
                        A dictionary with y-trace display names as keys, 
                        each mapped to a numpy ndarray of values for y, 
                        the dependent variable
                    render_mode: str (optional)
                        A string specifying how to draw the datapoints.
                        Options:
                            'markers' : draw as points
                            'lines' : connect points with line
                        Default: 'markers'

                histogram: 
                    title: str
                        A string display title for the plot
                    xaxis_title: str
                        A string label (with units) for the x-axis
                    traces: Dict[str, np.ndarray (shape = [values])]
                        A dictionary with trace display names as keys, 
                        each mapped to a numpy ndarray of values

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
