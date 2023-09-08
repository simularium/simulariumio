import numpy as np
import pytest
import random

from simulariumio.data_objects import JsonData, BinaryData, SimulariumFileData
from simulariumio import FileConverter, InputFileData, JsonWriter


bin_path = "simulariumio/tests/data/binary/binary_test.binary"
binary_file_data = open(bin_path, "rb").read()
binary_data_object = BinaryData(binary_file_data)

# convert to JSON
traj_data_obj = FileConverter(input_file=InputFileData(file_path=bin_path))._data
json_path = "simulariumio/tests/data/binary/json_test"
JsonWriter.save(traj_data_obj, json_path, False)
json_file_data = open(json_path + ".simularium", "r").read()
json_data_object = JsonData(json_file_data)

test_data_objects = [binary_data_object, json_data_object]

expected_traj_info = {
    "version": 3,
    "timeUnits": {"magnitude": 1.0, "name": "s"},
    "timeStepSize": 1.0,
    "totalSteps": 3,
    "spatialUnits": {"magnitude": 1.0, "name": "µm"},
    "size": {"x": 1000.0, "y": 1000.0, "z": 1000.0},
    "cameraDefault": {
        "position": {"x": 0.0, "y": 0.0, "z": 120.0},
        "lookAtPosition": {"x": 0.0, "y": 0.0, "z": 0.0},
        "upVector": {"x": 0.0, "y": 1.0, "z": 0.0},
        "fovDegrees": 75.0,
    },
    "typeMapping": {
        "0": {"name": "H", "geometry": {"displayType": "SPHERE"}},
        "1": {"name": "A", "geometry": {"displayType": "FIBER"}},
        "2": {"name": "C", "geometry": {"displayType": "FIBER"}},
        "3": {"name": "X", "geometry": {"displayType": "SPHERE"}},
        "4": {"name": "J", "geometry": {"displayType": "FIBER"}},
        "5": {"name": "L", "geometry": {"displayType": "FIBER"}},
        "6": {"name": "D", "geometry": {"displayType": "SPHERE"}},
        "7": {"name": "U", "geometry": {"displayType": "FIBER"}},
        "8": {"name": "E", "geometry": {"displayType": "SPHERE"}},
        "9": {"name": "Q", "geometry": {"displayType": "SPHERE"}},
        "10": {"name": "K", "geometry": {"displayType": "FIBER"}},
    },
}


@pytest.mark.parametrize("data_object", test_data_objects)
def test_get_traj_info(data_object: SimulariumFileData):
    assert data_object.get_trajectory_info() == expected_traj_info


@pytest.mark.parametrize("data_object", test_data_objects)
def test_get_num_steps(data_object: SimulariumFileData):
    assert data_object.get_num_frames() == expected_traj_info["totalSteps"]


expected_plot_data = {"version": 1, "data": ["plot data goes here"]}


@pytest.mark.parametrize("data_object", test_data_objects)
def test_get_plot_data(data_object: SimulariumFileData):
    assert data_object.get_plot_data() == expected_plot_data


@pytest.mark.parametrize("data_object", test_data_objects)
def test_get_traj_data_obj(data_object: SimulariumFileData):
    assert data_object.get_trajectory_data_object() == traj_data_obj


frame_index = 1
expected_n_agents = 5
expected_time = 1


@pytest.mark.parametrize("data_object", test_data_objects)
def test_frame_data(data_object: SimulariumFileData):
    frame = data_object.get_frame_at_index(frame_index)
    assert frame.frame_number == frame_index
    assert frame.n_agents == expected_n_agents
    assert np.isclose(frame.time, expected_time)


@pytest.mark.parametrize("data_object", test_data_objects)
def test_get_index_for_time(data_object: SimulariumFileData):
    random_frame = random.randint(0, expected_traj_info["totalSteps"] - 1)
    expected_time = random_frame * expected_traj_info["timeStepSize"]
    assert data_object.get_index_for_time(expected_time) == random_frame
