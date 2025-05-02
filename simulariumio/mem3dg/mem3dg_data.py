from ..data_objects import MetaData, UnitData
from typing import List, Dict, Any


class Mem3dgData:
    input_file_path: str
    output_obj_file_path: str
    meta_data: MetaData
    agent_name: str
    agent_color: str
    time_units: UnitData
    spatial_units: UnitData
    plots: List[Dict[str, Any]]

    def __init__(
        self,
        input_file_path: str,
        output_obj_file_path: str = None,
        meta_data: MetaData = None,
        agent_name: str = None,
        agent_color: str = None,
        time_units: UnitData = None,
        spatial_units: UnitData = None,
        plots: List[Dict[str, Any]] = None,
    ):
        """
        Parameters
        ----------
        input_file_path : str
            The path to the .nc file output by Mem3DG for this trajectory.
        output_obj_file_path : str (optional)
            The path to the directory where output .obj files will be saved
            to. If nothing is provided, the output .obj files will be saved
            to the current directory.
        meta_data : MetaData
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        agent_name: str (optional)
            This converter generates it's own DisplayData, but the agent name
            can optionally be overridden here. This will change the agent
            name that is displayed on the side column in simularium
        agent_color: string (optional)
            This converter generates it's own DisplayData, but the agent color
            can optionally be overridden here with a hex value for the color to
            display, e.g "#FFFFFF"
            Default: Use default colors from Simularium Viewer
        time_units: UnitData (optional)
            multiplier and unit name for time values
            Default: 1.0 second
        spatial_units: UnitData (optional)
            multiplier and unit name for spatial values
            (including positions, radii, and box size)
            Default: 1.0 meter
        plots : List[Dict[str, Any]] (optional)
            An object containing plot data already
            in Simularium format
        """
        self.input_file_path = input_file_path
        self.output_obj_file_path = output_obj_file_path or "."
        self.meta_data = meta_data or MetaData()
        self.agent_name = agent_name
        self.agent_color = agent_color
        self.time_units = time_units or UnitData("s")
        self.spatial_units = spatial_units or UnitData("m")
        self.plots = plots or []
