from ..data_objects import MetaData, DisplayData, UnitData
from .bond_data import BondData
from typing import List, Dict, Any

class PDBData:
    path_to_pdb_files: str
    meta_data: MetaData
    display_data: Dict[str, DisplayData]
    time_units: UnitData
    spatial_units: UnitData
    plots: List[Dict[str, Any]]
    inter_molecular_bonds: List[BondData]
    intra_molecular_bonds: List[BondData]
    time_step: UnitData

    def __init__(
        self,
        path_to_pdb_files: str,
        meta_data: MetaData = None,
        display_data: Dict[str, DisplayData] = None,
        time_units: UnitData = None,
        spatial_units: UnitData = None,
        plots: List[Dict[str, Any]] = None,
        inter_molecular_bonds: List[BondData] = None,
        intra_molecular_bonds: List[BondData] = None,
        time_step: UnitData = None,
    ):
        self.path_to_pdb_files = path_to_pdb_files
        self.meta_data = meta_data if meta_data is not None else MetaData()
        self.display_data = display_data if display_data is not None else {}
        self.time_units = time_units if time_units is not None else UnitData("s")
        self.spatial_units = (
            spatial_units if spatial_units is not None else UnitData("m")
        )
        self.plots = plots if plots is not None else []
        self.inter_molecular_bonds = inter_molecular_bonds if inter_molecular_bonds is not None else []
        self.intra_molecular_bonds = intra_molecular_bonds if inter_molecular_bonds is not None else []
        self.time_step = time_step if time_step is not None else self.time_units