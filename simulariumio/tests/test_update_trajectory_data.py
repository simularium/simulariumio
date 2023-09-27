import copy
import numpy as np
from simulariumio import TrajectoryData, DisplayData, AgentData, MetaData, ModelMetaData, CameraData, UnitData
from simulariumio.tests.conftest import three_default_agents
from simulariumio.constants import DISPLAY_TYPE

def test_update_agent_data():
    traj = three_default_agents()
    new_radii = np.array(
        [
            [1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0],
            [1.0, 1.0, 1.0],
        ]
    )
    new_display_data = {
        "C": DisplayData(
            name="C",
            display_type=DISPLAY_TYPE.OBJ,
            url="molecule.obj",
            color="#333333",
        )
    }
    expected_result = TrajectoryData(
        meta_data=traj.meta_data,
        agent_data=AgentData(
            times=traj.agent_data.times,
            n_agents=traj.agent_data.n_agents,
            viz_types=traj.agent_data.viz_types,
            unique_ids=traj.agent_data.unique_ids,
            types=traj.agent_data.types,
            positions=traj.agent_data.positions,
            radii=new_radii,
            rotations=traj.agent_data.rotations,
            n_subpoints=traj.agent_data.n_subpoints,
            subpoints=traj.agent_data.subpoints,
            display_data=new_display_data
        ),
        time_units=traj.time_units,
        spatial_units=traj.spatial_units,
        plots=traj.plots
    )
    copied_traj = traj.__deepcopy__({})
    copied_traj.update_agent_data(radii=new_radii, display_data=new_display_data)
    assert copied_traj == expected_result


def test_add_display_data():
    traj = three_default_agents()
    additional_display_data = {
        "C": DisplayData(
            name="C",
            display_type=DISPLAY_TYPE.OBJ,
            url="molecule.obj",
            color="#333333",
        )
    }
    expected_display_data = copy.deepcopy(traj.agent_data.display_data)
    expected_display_data["C"] = additional_display_data["C"]
    expected_result = TrajectoryData(
        meta_data=traj.meta_data,
        agent_data=AgentData(
            times=traj.agent_data.times,
            n_agents=traj.agent_data.n_agents,
            viz_types=traj.agent_data.viz_types,
            unique_ids=traj.agent_data.unique_ids,
            types=traj.agent_data.types,
            positions=traj.agent_data.positions,
            radii=traj.agent_data.radii,
            rotations=traj.agent_data.rotations,
            n_subpoints=traj.agent_data.n_subpoints,
            subpoints=traj.agent_data.subpoints,
            display_data=expected_display_data
        ),
        time_units=traj.time_units,
        spatial_units=traj.spatial_units,
        plots=traj.plots
    )
    copied_traj = traj.__deepcopy__({})
    copied_traj.add_display_data(additional_display_data)
    assert copied_traj == expected_result

def test_update_metadata():
    traj = three_default_agents()
    new_box_size = np.array([10.0, 10.0, 10.0])
    new_trajectory_title = "Test 1234"
    new_authors = "Test Author"
    new_camera_position = np.array([15.0, 0.0, 0.0])
    expected_result = TrajectoryData(
        meta_data=MetaData(
            box_size=new_box_size,
            camera_defaults=CameraData(
                position=new_camera_position,
                look_at_position=traj.meta_data.camera_defaults.look_at_position,
                up_vector=traj.meta_data.camera_defaults.up_vector,
                fov_degrees=traj.meta_data.camera_defaults.fov_degrees,
            ),
            scale_factor=traj.meta_data.scale_factor,
            trajectory_title=new_trajectory_title,
            model_meta_data=ModelMetaData(
                title=traj.meta_data.model_meta_data.title,
                version=traj.meta_data.model_meta_data.version,
                authors=new_authors,
                description=traj.meta_data.model_meta_data.description,
                source_code_url=traj.meta_data.model_meta_data.source_code_url,
                input_data_url=traj.meta_data.model_meta_data.input_data_url,
                raw_output_data_url=traj.meta_data.model_meta_data.raw_output_data_url,
            )
        ),
        agent_data=traj.agent_data,
        time_units=traj.time_units,
        spatial_units=traj.spatial_units,
        plots=traj.plots,
    )
    copied_traj = traj.__deepcopy__({})
    copied_traj.update_meta_data(
        box_size=new_box_size,
        camera_position=new_camera_position,
        authors=new_authors,
        trajectory_title=new_trajectory_title
    )
    assert copied_traj == expected_result

def test_update_time_units():
    traj = three_default_agents()
    new_magnitude = 0.5
    expected_result = TrajectoryData(
        meta_data=traj.meta_data,
        agent_data=traj.agent_data,
        time_units=UnitData(magnitude=new_magnitude, name=traj.time_units.name),
        spatial_units=traj.spatial_units,
        plots=traj.plots
    )
    copied_traj = traj.__deepcopy__({})
    copied_traj.update_time_units(magnitude=new_magnitude)
    assert copied_traj == expected_result

def test_update_spatial_units():
    traj = three_default_agents()
    new_magnitude = 5
    expected_result = TrajectoryData(
        meta_data=traj.meta_data,
        agent_data=traj.agent_data,
        spatial_units=UnitData(magnitude=new_magnitude, name=traj.spatial_units.name),
        time_units=traj.time_units,
        plots=traj.plots
    )
    copied_traj = traj.__deepcopy__({})
    copied_traj.update_spatial_units(magnitude=new_magnitude)
    assert copied_traj == expected_result
