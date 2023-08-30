import numpy as np
import pytest
import random

from simulariumio.data_objects import JsonData, BinaryData


test_name = "test.simularium"

bin_path = "simulariumio/tests/data/simularium_files/smoldyn_spine_bin.simularium"
binary_file_data = open(bin_path, "rb").read()
binary_data_object = BinaryData(test_name, binary_file_data)

json_path = "simulariumio/tests/data/simularium_files/smoldyn_spine.simularium"
json_file_data = open(json_path, "r").read()
json_data_object = JsonData(test_name, json_file_data)

test_data_objects = [binary_data_object, json_data_object]


@pytest.mark.parametrize("data_object", test_data_objects)
def test_get_file_name(data_object):
    assert data_object.get_file_name() == test_name


expected_traj_info = {
    "cameraDefault": {
        "fovDegrees": 50.0,
        "lookAtPosition": {"x": 0.0, "y": 0.0, "z": 0.0},
        "position": {"x": 0.0, "y": 120.0, "z": 0.0},
        "upVector": {"x": 0.0, "y": 1.0, "z": 0.0},
    },
    "modelInfo": {
        "authors": "Shahid Khan et al",
        "description": "A Smoldyn model of a dendritic spine with CaMKII and "
        "molecules of the postsynaptic density at the spine tip.",
        "doi": "10.1007/s10827-011-0323-2",
        "inputDataUrl": "http://www.smoldyn.org/archive/Andrews_Arkin_2010/spine.txt",
        "sourceCodeLicenseUrl": "https://github.com/ssandrews/Smoldyn/"
        "blob/master/LICENSE",
        "sourceCodeUrl": "https://github.com/ssandrews/Smoldyn",
        "title": "Sequestration of CaMKII in dendritic spines",
    },
    "size": {"x": 50.0, "y": 50.0, "z": 50.0},
    "spatialUnits": {"magnitude": 10.0, "name": "µm"},
    "timeStepSize": 2.0,
    "timeUnits": {"magnitude": 1.0, "name": "ms"},
    "totalSteps": 751,
    "trajectoryTitle": "Sequestration of CaMKII in dendritic spines",
    "typeMapping": {
        "0": {"geometry": {"displayType": "SPHERE"}, "name": "CaMKa#solution"},
        "1": {"geometry": {"displayType": "SPHERE"}, "name": "PSDA#solution"},
        "2": {"geometry": {"displayType": "SPHERE"}, "name": "NR2B#solution"},
    },
    "version": 3,
}


@pytest.mark.parametrize("data_object", test_data_objects)
def test_get_traj_info(data_object):
    assert data_object.get_trajectory_info() == expected_traj_info


@pytest.mark.parametrize("data_object", test_data_objects)
def test_get_num_steps(data_object):
    assert data_object.get_num_frames() == expected_traj_info["totalSteps"]


expected_plot_data_names = ["CaMKa", "PSDA", "NR2B"]


@pytest.mark.parametrize("data_object", test_data_objects)
def test_get_plot_data(data_object):
    plot_data = data_object.get_plot_data()
    assert type(plot_data) == dict
    for dataset in plot_data["data"][0]["data"]:
        assert dataset["name"] in expected_plot_data_names
        assert dataset["type"] == "scatter"

    # TrajectoryData.plots should match get_plot_data()
    traj_data_obj = data_object.get_trajectory_data_object()
    assert traj_data_obj.plots == plot_data["data"]


frame_index = 744
expected_n_agents = 306
expected_time = 1488


@pytest.mark.parametrize("data_object", test_data_objects)
def test_frame_data(data_object):
    frame = data_object.get_frame_at_index(frame_index)
    assert frame.frame_number == frame_index
    assert frame.n_agents == expected_n_agents
    assert np.isclose(frame.time, expected_time)


@pytest.mark.parametrize("data_object", test_data_objects)
def test_get_index_for_time(data_object):
    random_frame = random.randint(0, expected_traj_info["totalSteps"])
    expected_time = random_frame * expected_traj_info["timeStepSize"]
    assert data_object.get_index_for_time(expected_time) == random_frame
