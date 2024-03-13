from ..trajectory_converter import TrajectoryConverter
from ..data_objects import AgentData, TrajectoryData, DimensionData
from .pdb_data import PDBData
from MDAnalysis import Universe
import os


class PDBConverter(TrajectoryConverter):

    def __init__(
        self,
        input_data: PDBData,
    ):
        self._data = self._read(input_data)

    def _read_pdb_files(self, input_data: PDBData) -> AgentData:
        file_list = os.listdir(input_data.path_to_pdb_files)
        file_list.sort()
        n_timesteps = len(file_list)
        dimensions = DimensionData(
            total_steps=n_timesteps,
            max_agents=0
        )
        times = []
        # universes = []
        for file in file_list:
            print(f"about to read file: {file}")
            u = Universe(os.path.join(input_data.path_to_pdb_files, file))
            n_agents = len(u.atoms.positions)
            if n_agents > dimensions.max_agents:
                dimensions.max_agents = n_agents
            times.append(os.path.splitext(file)[0])
        times.sort(key=int)
        result = AgentData.from_dimensions(dimensions)
        result.n_timesteps = n_timesteps

        for time_index in range(n_timesteps):
            # we are assuming the time is the file name
            universe = Universe(os.path.join(input_data.path_to_pdb_files, times[time_index] + ".pdb"))
            result.times[time_index] = float(times[time_index])
            result.positions[time_index] = universe.atoms.positions

            atoms = universe.atoms
            result.n_agents[time_index] = len(atoms)
            result.viz_types[time_index] = [1000.0] * len(atoms)
            result.radii[time_index] = [1.0] * len(atoms)
            # Go through all of the atoms, set each as a new agent and set their position
            # determine type based on resname and maybe name
            for atom_index in range(len(atoms)):
                atom = atoms[atom_index]
                # residue name
                resname = atom.resname
                # part (center of mass, binding site, etc)
                name = atom.name
                full_name = resname + "#" + name
                result.types[time_index].append(
                    TrajectoryConverter._get_display_type_name_from_raw(
                        full_name, input_data.display_data
                    )
                )
                result.unique_ids[time_index][atom_index] = atom.id
                # Get the user provided display data for this raw_type_name
                input_display_data = TrajectoryConverter._get_display_data_for_agent(
                    full_name, input_data.display_data
                )

                result.radii[time_index][atom_index] = (
                    input_display_data.radius
                    if input_display_data and input_display_data.radius is not None
                    else 1.0
                )
        return result
    
    def _read(self, input_data: PDBData) -> TrajectoryData:
        print("Reading files")
        agent_data = self._read_pdb_files(input_data)
        return TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=input_data.time_units,
            spatial_units=input_data.spatial_units,
            plots=input_data.plots,
        )

