from MDAnalysis import Universe
import os

from ..trajectory_converter import TrajectoryConverter
from ..data_objects import (
    AgentData,
    TrajectoryData,
    DimensionData,
    UnitData,
    DisplayData,
)
from ..constants import DISPLAY_TYPE, VALUES_PER_3D_POINT, VIZ_TYPE
from ..exceptions import InputDataError
from .nerdss_data import NerdssData


class NerdssConverter(TrajectoryConverter):
    def __init__(
        self,
        input_data: NerdssData,
    ):
        """
        Parameters
        ----------
        input_data : NerdssData
            An object containing info for reading
            NERDSS simulation trajectory outputs and plot data
        """
        self._data = self._read(input_data)

    def _read_pdb_files(self, input_data: NerdssData) -> AgentData:
        file_list = os.listdir(input_data.path_to_pdb_files)
        file_list.sort()
        n_timesteps = len(file_list)
        dimensions = DimensionData(
            total_steps=n_timesteps, max_agents=0, max_subpoints=VALUES_PER_3D_POINT * 2
        )
        time_steps = []
        for file in file_list:
            u = Universe(os.path.join(input_data.path_to_pdb_files, file))
            n_agents = len(u.atoms.positions)
            if n_agents * 2 > dimensions.max_agents:
                # each "atom" will be represented by 1 sphere agent and up
                # to 1 fiber agent, representing a bond
                dimensions.max_agents = n_agents * 2
            file_name = os.path.splitext(file)[0]
            if not file_name.isdigit():
                raise InputDataError(
                    f"File name is expected to be the timestep, {file_name} is invalid"
                )
            time_steps.append(file_name)
        time_steps.sort(key=int)
        agent_data = AgentData.from_dimensions(dimensions)
        agent_data.n_timesteps = n_timesteps

        # keep track of fiber positions for bonds as we go
        fiber_positions = [[] for i in range(n_timesteps)]

        for time_index in range(n_timesteps):
            # we are assuming the time is the file name
            universe = Universe(
                os.path.join(
                    input_data.path_to_pdb_files, time_steps[time_index] + ".pdb"
                )
            )
            atoms = universe.atoms
            temp_n_agents = len(atoms)
            agent_data.positions[time_index][0:temp_n_agents] = universe.atoms.positions

            agent_data.times[time_index] = (
                float(time_steps[time_index]) * input_data.time_units.magnitude
            )

            agent_data.n_agents[time_index] = len(atoms)
            if input_data.display_data.get("bonds") is None:
                input_data.display_data["bonds"] = DisplayData(
                    name="bonds", display_type=DISPLAY_TYPE.FIBER, radius=0.5
                )

            for residue in universe.residues:
                com_pos = None
                bond_site_pos = []
                resname = residue.resname

                for atom in residue.atoms:
                    name = atom.name
                    atom_index = atom.index
                    full_name = resname + "#" + name
                    position = atom.position
                    agent_data.types[time_index].append(
                        TrajectoryConverter._get_display_type_name_from_raw(
                            full_name, input_data.display_data
                        )
                    )
                    agent_data.unique_ids[time_index][atom_index] = atom.id

                    # Get the user provided display data for this raw_type_name
                    input_display_data = (
                        TrajectoryConverter._get_display_data_for_agent(
                            full_name, input_data.display_data
                        )
                    )

                    agent_data.radii[time_index][atom_index] = (
                        input_display_data.radius
                        if input_display_data and input_display_data.radius is not None
                        else 1.0
                    )

                    # Draw intra-molecular bonds as a fiber between COM (center of
                    # mass) and binding sites each residue
                    if name != "ref":
                        if name == "COM":
                            # Found the center of mass!
                            com_pos = list(position)
                            for bond_site in bond_site_pos:
                                # Add a fiber to connect COM with bond sites
                                bond_coords = com_pos + bond_site
                                fiber_positions[time_index].append(bond_coords)
                        elif com_pos:
                            # Already have COM, so add fiber to connect it to this site
                            bond_coords = com_pos + list(position)
                            fiber_positions[time_index].append(bond_coords)
                        else:
                            # Haven't found COM, so keep track of this bond site to
                            # connect to COM when we find it
                            bond_site_pos.append(list(position))

        # Add bond data into agent_data
        bonds_display_data = TrajectoryConverter._get_display_data_for_agent(
            "bonds", input_data.display_data
        )
        next_uid = agent_data.unique_ids.max() + 1
        for timestep in range(n_timesteps):
            n_fibers = len(fiber_positions[timestep])
            n_atoms = int(agent_data.n_agents[timestep])
            agent_data.n_agents[timestep] = n_fibers + n_atoms
            for agent_index in range(n_fibers):
                agent_data.subpoints[timestep][agent_index + n_atoms] = fiber_positions[
                    timestep
                ][agent_index]
                agent_data.n_subpoints[timestep][agent_index + n_atoms] = (
                    VALUES_PER_3D_POINT * 2
                )
                agent_data.viz_types[timestep][agent_index + n_atoms] = VIZ_TYPE.FIBER
                agent_data.radii[timestep][
                    agent_index + n_atoms
                ] = bonds_display_data.radius
                agent_data.types[timestep].append(bonds_display_data.name)
                agent_data.unique_ids[timestep][agent_index + n_atoms] = next_uid
                next_uid += 1
        return agent_data

    def _read(self, input_data: NerdssData) -> TrajectoryData:
        """
        Return a TrajectoryData object containing the NERDSS data
        """
        print("Reading PDB Data -------------")
        agent_data = self._read_pdb_files(input_data)
        # get display data (geometry and color)
        for tid in input_data.display_data:
            display_data = input_data.display_data[tid]
            agent_data.display_data[display_data.name] = display_data
        input_data.meta_data.scale_factor = 1.0
        input_data.meta_data._set_box_size()
        result = TrajectoryData(
            meta_data=input_data.meta_data,
            agent_data=agent_data,
            time_units=UnitData(name=input_data.time_units.name),
            spatial_units=input_data.spatial_units,
            plots=input_data.plots,
        )
        return result
