import numpy as np

from simulariumio.data_objects import JsonData, BinaryData

n_frames = 751
test_name = "test.simularium"
traj_info = {
    'cameraDefault': {
        'fovDegrees': 50.0,
        'lookAtPosition': {'x': 0.0, 'y': 0.0, 'z': 0.0},
        'position': {'x': 0.0, 'y': 120.0, 'z': 0.0},
        'upVector': {'x': 0.0, 'y': 1.0, 'z': 0.0}
    },
    'modelInfo': {
        'authors': 'Shahid Khan et al',
        'description': 'A Smoldyn model of a dendritic spine with CaMKII and molecules of the postsynaptic density at the spine tip.',
        'doi': '10.1007/s10827-011-0323-2',
        'inputDataUrl': 'http://www.smoldyn.org/archive/Andrews_Arkin_2010/spine.txt',
        'sourceCodeLicenseUrl': 'https://github.com/ssandrews/Smoldyn/blob/master/LICENSE',
        'sourceCodeUrl': 'https://github.com/ssandrews/Smoldyn',
        'title': 'Sequestration of CaMKII in dendritic spines'
    },
    'size': {'x': 50.0, 'y': 50.0, 'z': 50.0},
    'spatialUnits': {'magnitude': 10.0, 'name': 'µm'},
    'timeStepSize': 2.0,
    'timeUnits': {'magnitude': 1.0, 'name': 'ms'},
    'totalSteps': 751,
    'trajectoryTitle': 'Sequestration of CaMKII in dendritic spines',
    'typeMapping': {
        '0': {'geometry': {'displayType': 'SPHERE'}, 'name': 'CaMKa#solution'},
        '1': {'geometry': {'displayType': 'SPHERE'}, 'name': 'PSDA#solution'},
        '2': {'geometry': {'displayType': 'SPHERE'}, 'name': 'NR2B#solution'}
    },
    'version': 3
}
frame_index = 744


def test_binary_data():
    path = "simulariumio/tests/data/simularium_files/smoldyn_spine_bin.simularium"
    with open(path, "rb") as file:
        contents = file.read()
        data_object = BinaryData(test_name, contents)
        assert data_object.get_file_name() == test_name
        assert data_object.get_num_frames() == n_frames
        assert data_object.get_trajectory_info() == traj_info
        frame = data_object.get_frame_at_index(frame_index)
        assert frame.frame_number == frame_index
        assert frame.n_agents == 306
        assert np.isclose(frame.time, 1488)
        assert data_object.get_index_for_time(12.0) == 6
        assert data_object.get_trajectory_data_object().meta_data.trajectory_title == 'Sequestration of CaMKII in dendritic spines'
        assert type(data_object.get_file_contents()) == bytes


def test_json_data():
    path = "simulariumio/tests/data/simularium_files/smoldyn_spine.simularium"
    file = open(path, "r")
    contents = file.read()
    data_object = JsonData(test_name, contents)
    assert data_object.get_file_name() == test_name
    assert data_object.get_num_frames() == n_frames
    assert data_object.get_trajectory_info() == traj_info
    frame = data_object.get_frame_at_index(frame_index)
    assert frame.frame_number == frame_index
    assert frame.n_agents == 306
    assert np.isclose(frame.time, 1488.0)
    assert data_object.get_index_for_time(12.0) == 6
    assert data_object.get_trajectory_data_object().meta_data.trajectory_title == 'Sequestration of CaMKII in dendritic spines'
    assert type(data_object.get_file_contents()) == dict