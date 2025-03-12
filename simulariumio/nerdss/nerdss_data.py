from ..data_objects import MetaData, DisplayData, UnitData
from typing import List, Dict, Any


class NerdssData:
    path_to_pdb_files: str
    meta_data: MetaData
    display_data: Dict[str, DisplayData]
    time_units: UnitData
    spatial_units: UnitData
    plots: List[Dict[str, Any]]
    time_step: UnitData

    def __init__(
        self,
        path_to_pdb_files: str,
        meta_data: MetaData = None,
        display_data: Dict[str, DisplayData] = None,
        time_units: UnitData = None,
        spatial_units: UnitData = None,
        plots: List[Dict[str, Any]] = None,
        time_step: UnitData = None,
    ):
        """
        Parameters
        ----------
        path_to_pdb_files : str
            A path to the folder of PDB files for the trajectory.
            For this converter, it is expected that the frame numbers
            are the names of the file (plus the file extention). At this
            time, the frame numbers must be at consistent intervals
        meta_data : MetaData
            An object containing metadata for the trajectory
            including box size, scale factor, and camera defaults
        display_data: Dict[str, DisplayData] (optional)
            The particle type name from NERDSS data mapped
            to display names and rendering info for that type,
            Default: for names, use NERDSS name,
                for radius, use 1.0,
                for rendering, use default representations and colors
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
        time_step : UnitData (optional)
            Time step between each frame, where the frame numbers are represented
            as the names of the .pdb files in path_to_pdb_files
            Default: 1.0 second
        """
        self.path_to_pdb_files = path_to_pdb_files
        self.meta_data = meta_data if meta_data is not None else MetaData()
        self.display_data = display_data if display_data is not None else {}
        self.time_units = time_units if time_units is not None else UnitData("s")
        self.spatial_units = (
            spatial_units if spatial_units is not None else UnitData("m")
        )
        self.plots = plots if plots is not None else []
        self.time_step = time_step if time_step is not None else self.time_units
