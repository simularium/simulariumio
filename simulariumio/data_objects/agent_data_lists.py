import logging
from typing import List, Dict

from .display_data import DisplayData

###############################################################################

log = logging.getLogger(__name__)

###############################################################################


class AgentDataLists:
    n_timesteps: int
    times: List[float]
    n_agents: List[int]
    viz_types: List[List[float]]
    unique_ids: List[List[int]]
    types: List[List[str]]
    positions: List[List[List[float]]]
    radii: List[List[float]]
    rotations: List[List[List[float]]]
    n_subpoints: List[List[int]]
    subpoints: List[List[List[float]]]
    display_data: Dict[str, DisplayData]
    draw_fiber_points: bool

    def __init__(
        self,
        times: List[float],
        n_agents: List[int],
        viz_types: List[List[float]],
        unique_ids: List[List[int]],
        types: List[List[str]],
        positions: List[List[List[float]]],
        radii: List[List[float]],
        rotations: List[List[List[float]]] = None,
        n_subpoints: List[List[int]] = None,
        subpoints: List[List[List[float]]] = None,
        display_data: Dict[str, DisplayData] = None,
        draw_fiber_points: bool = False,
        n_timesteps: int = -1,
    ):
        """
        This object contains spatial simulation data

        Parameters
        ----------
        times : List[float] (shape = [timesteps])
            A list containing the elapsed simulated time
            at each timestep (in the units specified by
            TrajectoryData.time_units)
        n_agents : List[int] (shape = [timesteps])
            A list containing the number of agents
            that exist at each timestep
        viz_types : List[List[float]] (shape = [timesteps, agents])
            A list containing the viz type
            for each agent at each timestep. Current options:
                1000 : default,
                1001 : fiber (which will require subpoints)
        unique_ids : List[List[int]] (shape = [timesteps, agents])
            A list containing the unique ID
            for each agent at each timestep
        types : List[List[str]] (list of shape [timesteps, agents])
            A list containing timesteps, for each a list of
            the string name for the type of each agent
        positions : List[List[List[float]]] (shape = [timesteps, agents, 3])
            A list containing the XYZ position
            for each agent at each timestep (in the units
            specified by TrajectoryData.spatial_units)
        radii : List[List[float]] (shape = [timesteps, agents])
            A list containing the radius
            for each agent at each timestep
        rotations : List[List[List[float]]] (shape = [timesteps, agents, 3]) (optional)
            A list containing the XYZ euler angles representing
            the rotation for each agent at each timestep in degrees
            Default: [0, 0, 0] for each agent
        n_subpoints : List[List[int]] (shape = [timesteps, agents]) (optional)
            A list containing the number of subpoints
            belonging to each agent at each timestep. Required if
            subpoints are provided
            Default: None
        subpoints : List[List[List[float]]]
        (shape = [timesteps, agents, subpoints]) (optional)
            A list containing a list of subpoint data
            for each agent at each timestep. These values are
            currently used for fiber and sphere group agents
            Default: None
        display_data: Dict[str,DisplayData] (optional)
            A dictionary mapping agent type name to DisplayData
            to use for that type
            Default: None
        draw_fiber_points: bool (optional)
            Draw spheres at every other fiber point for fibers?
            Default: False
        n_timesteps : int (optional)
            Use the first n_timesteps frames of data
            Default: -1 (use the full length of the buffer)
        """
        self.times = times
        self.n_agents = n_agents
        self.viz_types = viz_types
        self.unique_ids = unique_ids
        self.types = types
        self.positions = positions
        self.radii = radii
        self.rotations = rotations
        self.n_subpoints = n_subpoints
        self.subpoints = subpoints
        self.display_data = display_data if display_data is not None else {}
        self.draw_fiber_points = draw_fiber_points
        self.n_timesteps = n_timesteps
