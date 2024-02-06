"""

INSTRUCTIONS:
 (TODO what about multiple instances of geometry?)
 (TODO different states at different times)

 1. Install simulariumio: in terminal on Mac run 
    `/Applications/Autodesk/maya2024/Maya.app/Contents/bin/mayapy 
    -m pip install simulariumio`. Restart Maya. (More help here:
    https://help.autodesk.com/view/MAYAUL/2022/ENU/
    ?guid=GUID-72A245EC-CDB4-46AB-BEE0-4BBBF9791627)
 1. Name objects in the hierarchy with the name you want 
    to display in Simularium viewer.
 2. Set the main color of each object's first shader to the color 
    you want to display in the viewer.
 3. Save the OBJs in the cloud somewhere and provide the url 
    for each in the geometry_urls (these links must be publicly accessible).
 4. Edit the parameter values in the block directly below as needed.
 5. Select the objects you want to export and then run this script.
    
"""   

# edit these parameter values
# geometry_urls = {
#     "Antigen" : "https://www.dropbox.com/scl/fi/xh3vmyt9d74cl5cbhqgpm/Antigen.obj?rlkey=b4zcediso03wiuc96w3agm6rg&dl=1",
#     "Antibody1" : "https://www.dropbox.com/scl/fi/1x8ei4xcn7apdi6l1h2gw/Antibody1.obj?rlkey=wak5oriwxuvupu71nayy2qsdf&dl=1",
#     "Antibody2" : "https://www.dropbox.com/scl/fi/7ek5w2bltdkqai6aa27fy/Antibody2.obj?rlkey=g3mtgwgqh4c2xfc43jbvtg4l0&dl=1",
# }
geometry_urls = {
    "Antigen" : "https://aics-simularium-data.s3.us-east-2.amazonaws.com/meshes/obj/Antigen.obj",
    "Antibody1" : "https://aics-simularium-data.s3.us-east-2.amazonaws.com/meshes/obj/Antibody1.obj",
    "Antibody2" : "https://aics-simularium-data.s3.us-east-2.amazonaws.com/meshes/obj/Antibody2.obj",
    "gizmo" : "https://aics-simularium-data.s3.us-east-2.amazonaws.com/meshes/obj/maya_gizmo.obj",
    "static" : "https://aics-simularium-data.s3.us-east-2.amazonaws.com/meshes/obj/Pi.obj",
    "pTorus1" : "https://aics-simularium-data.s3.us-east-2.amazonaws.com/meshes/obj/TorusOBJ.obj",
    "pCube1" : "https://aics-simularium-data.s3.us-east-2.amazonaws.com/meshes/obj/CubeOBJ.obj",
}
spatial_units = "nm"  # nanometers
timestep = 1.0  # time that passes each step
time_units = "ns"  # nanoseconds
output_path = "/Users/blairl/Dropbox/ForBlair_20231002/" # this file path must be absolute
trajectory_name = "AgAb_animation" #.simularium
display_title = "Antibody-Antigen animation"
author_names = "Margot Riggi, Janet Iwasa"
animation_description = "An animation of an antibody binding an antigen."
box_dimensions = [100.0, 100.0, 100.0] # box will be centered at [0, 0, 0]
camera_position=[0.0, 0.0, 200.0]
camera_look_at_position=[0.0, 0.0, 0.0]
camera_fov_degrees=60.0
save_objs = True

# don't edit below

import maya.cmds as cmds
import numpy as np
from scipy.spatial.transform import Rotation
from simulariumio import (
    TrajectoryConverter, 
    TrajectoryData, 
    AgentData, 
    UnitData, 
    MetaData, 
    ModelMetaData,
    CameraData, 
    DisplayData,
    DISPLAY_TYPE,
)
from simulariumio.constants import VIZ_TYPE

min_time = int(cmds.playbackOptions(query=True, min=True))
max_time = int(cmds.playbackOptions(query=True, max=True))
total_steps = max_time - min_time + 1
type_names = cmds.ls(selection=True)
max_agents = len(type_names)
positions = []
rotations = []
radii = []

if max_agents < 1:
    raise Exception("Select one or more objects to export.")

# convert shader colors to hex codes
def color_to_hex(raw_color):
    rgb_color = (
        int(255 * raw_color[0][0]), 
        int(255 * raw_color[0][1]), 
        int(255 * raw_color[0][2])
    )
    return '#%02x%02x%02x' % rgb_color

def rotation_matrix_to_euler_angles(rotation_matrix):
    return -1 * Rotation.from_matrix(rotation_matrix).as_euler("xyz", degrees=False)

# get display information
display_data={}
for type_name in type_names:
    # get color from first shader
    sel_shape = cmds.ls(objectsOnly=True, shapes=True)
    shading_groups = cmds.listConnections(sel_shape, type='shadingEngine')
    shaders = cmds.ls(cmds.listConnections(shading_groups), materials=True)
    # TODO debug color
    # color_hex = color_to_hex(cmds.getAttr(shaders[0]+".color"))
    # create display data
    display_data[type_name] = DisplayData(
        name=type_name,
        display_type=DISPLAY_TYPE.OBJ,
        url=geometry_urls[type_name],
        # color=color_hex,
    )

# get trajectory
for time_ix, time in enumerate(range(min_time, max_time + 1)):
    cmds.currentTime(time)
    positions.append([])
    rotations.append([])
    radii.append([])
    for type_name in type_names:
        position = cmds.xform(type_name, query=True, rotatePivot=True, worldSpace=True)
        transform = cmds.getAttr(f"{type_name}.worldMatrix", time=time)
        scale = [
            np.linalg.norm(transform[0:3]),
            np.linalg.norm(transform[4:7]),
            np.linalg.norm(transform[8:11])
        ]
        rotation_matrix = np.array([
            [transform[0] / scale[0], transform[1] / scale[0], transform[2] / scale[0]], 
            [transform[4] / scale[1], transform[5] / scale[1], transform[6] / scale[1]], 
            [transform[8] / scale[2], transform[9] / scale[2], transform[10] / scale[2]]
        ])
        positions[time_ix].append(position)
        rotations[time_ix].append(rotation_matrix_to_euler_angles(rotation_matrix))
        radii[time_ix].append(scale[0])
cmds.currentTime(min_time)

# export OBJs
if save_objs:
    for type_name in type_names:
        cmds.select(type_name, replace=True)
        merged_name = f"{type_name}_merged"
        try:
            position = cmds.xform(
                type_name, 
                query=True, 
                rotatePivot=True, 
                worldSpace=True
            )
            cmds.polyUnite(mergeUVSets=1, name=merged_name)
            cmds.xform(merged_name, pivots=position)
        except:
            merged_name = type_name
            cmds.parent(type_name, world=True)
        cmds.move(0, 0, 0, merged_name, rotatePivotRelative=True)
        cmds.makeIdentity(
            merged_name, 
            apply=True, 
            translate=True, 
            rotate=True, 
            scale=True, 
            normal=0, 
            preserveNormals=True
        )
        cmds.file(
            f"{output_path}{type_name}.obj", 
            force=True, 
            options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1", 
            type="OBJexport", 
            preserveReferences=True,
            exportSelected=True,
        )
 
# convert to simularium
trajectory_data = TrajectoryData(
    meta_data=MetaData(
        box_size=np.array(box_dimensions),
        camera_defaults=CameraData(
            position=np.array(camera_position),
            look_at_position=np.array(camera_look_at_position),
            fov_degrees=camera_fov_degrees,
        ),
        trajectory_title=display_title,
        model_meta_data=ModelMetaData(
            title="An animation created in Maya",
            authors=author_names,
            description=animation_description,
        ),
    ),
    agent_data=AgentData(
        times=timestep * np.array(list(range(min_time, max_time + 1))),
        n_agents=total_steps * [max_agents],
        viz_types=total_steps * [max_agents * [VIZ_TYPE.DEFAULT]],
        unique_ids=total_steps * [list(range(max_agents))],
        types=total_steps * [type_names],
        positions=positions,
        rotations=rotations,
        radii=radii,
        display_data=display_data,
    ),
    time_units=UnitData(time_units),
    spatial_units=UnitData(spatial_units),
)

# save the file(s)
TrajectoryConverter(trajectory_data).save(f"{output_path}{trajectory_name}")
