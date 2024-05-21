"""

INSTRUCTIONS:

 1. Install simulariumio: in terminal on Mac run 
    `/Applications/Autodesk/maya2024/Maya.app/Contents/bin/mayapy 
    -m pip install simulariumio`. Restart Maya. (More help here:
    https://help.autodesk.com/view/MAYAUL/2022/ENU/
    ?guid=GUID-72A245EC-CDB4-46AB-BEE0-4BBBF9791627)
 1. Name objects in the hierarchy: "[A]__[B][C]"
    A = The name you want to display in Simularium viewer.
    B = If you want to have the same display name but different mesh geometry for some agents, 
        add unique names for each geometry here. Otherwise you can skip this.
    C = If you want to manually set IDs, add digits to the end of each object's name. 
        IDs determine unique objects in Simularium. When one is clicked, all the objects 
        with the same ID will highlight and draw trails together.
 2. Set the main color of each object's first shader to the color 
    you want to display in the viewer.
 3. Save the OBJs in the cloud somewhere and provide the url 
    for each in the geometry_urls (these links must be publicly accessible).
 4. Edit the parameter values in the block directly below as needed.
 5. Select the objects you want to export and then run this script.
    
"""   

# edit these parameter values *******************************************************************

logging = False
"""
IDs determine unique objects in Simularium.
When one is clicked, all the objects with the same ID will highlight and draw trails together.
There are two options to set IDs:
- manually_set_IDs = False : Each selected object will get it's own ID automatically
- manually_set_IDs = True : The script will use the digits at the end of each object's name as the ID
"""
manually_set_IDs = False
geometry_urls = {
    """
    Map Maya names to geometry URLs.
    - you can leave the digits at the end off the name here.
    """
    "Unbound_Subunit__AlphaOne" : "https://www.dropbox.com/scl/fi/0i2pqtfmco7ypae97j7lm/Alpha1.obj?rlkey=rmiqbqbgbpqeo6dgg7en43cl3&dl=0",
    "Unbound_Subunit__AlphaTwo" : "https://www.dropbox.com/scl/fi/6vgyrtszp0z57sb3vxtkl/Alpha2.obj?rlkey=als8pwcevjlbnycgit7bkx4qj&dl=0",
    "Unbound_Subunit__BetaOne" : "https://www.dropbox.com/scl/fi/scpblondcj06w459vuofr/Beta1.obj?rlkey=cy1us3gqe9yhanuosx9wapzn2&dl=0",
    "Unbound_Subunit__BetaTwo" : "https://www.dropbox.com/scl/fi/3tlfc0hm4wwpqkeuxlffv/Beta2.obj?rlkey=2fq8wt2j169go2wu2qe7axmjy&dl=0",
    "Bound_To_O2_Subunit__AlphaOne" : "https://www.dropbox.com/scl/fi/0i2pqtfmco7ypae97j7lm/Alpha1.obj?rlkey=rmiqbqbgbpqeo6dgg7en43cl3&dl=0",
    "Bound_To_O2_Subunit__AlphaTwo" : "https://www.dropbox.com/scl/fi/6vgyrtszp0z57sb3vxtkl/Alpha2.obj?rlkey=als8pwcevjlbnycgit7bkx4qj&dl=0",
    "Bound_To_O2_Subunit__BetaOne" : "https://www.dropbox.com/scl/fi/scpblondcj06w459vuofr/Beta1.obj?rlkey=cy1us3gqe9yhanuosx9wapzn2&dl=0",
    "Bound_To_O2_Subunit__BetaTwo" : "https://www.dropbox.com/scl/fi/3tlfc0hm4wwpqkeuxlffv/Beta2.obj?rlkey=2fq8wt2j169go2wu2qe7axmjy&dl=0",
    "Bound_To_CO_Subunit__AlphaOne" : "https://www.dropbox.com/scl/fi/0i2pqtfmco7ypae97j7lm/Alpha1.obj?rlkey=rmiqbqbgbpqeo6dgg7en43cl3&dl=0",
    "Bound_To_CO_Subunit__AlphaTwo" : "https://www.dropbox.com/scl/fi/6vgyrtszp0z57sb3vxtkl/Alpha2.obj?rlkey=als8pwcevjlbnycgit7bkx4qj&dl=0",
    "Bound_To_CO_Subunit__BetaOne" : "https://www.dropbox.com/scl/fi/scpblondcj06w459vuofr/Beta1.obj?rlkey=cy1us3gqe9yhanuosx9wapzn2&dl=0",
    "Bound_To_CO_Subunit__BetaTwo" : "https://www.dropbox.com/scl/fi/3tlfc0hm4wwpqkeuxlffv/Beta2.obj?rlkey=2fq8wt2j169go2wu2qe7axmjy&dl=0",
    "Dioxygen" : "https://www.dropbox.com/scl/fi/imq5v6hpjmrvawyvcc92b/Dioxygen.obj?rlkey=sieohllmlmpfli713fl7m7q4r&dl=0",
    "Carbon_Monoxyde" : "https://www.dropbox.com/scl/fi/r1z6pdyk8g7s3x1uoxoup/CarbonMonoxyde.obj?rlkey=8zuy9tk7er5rszdu6pzvwr24g&dl=0",
}
spatial_units = "nm"  # nanometers
timestep = 0.033  # time that passes each step
time_units = "ms"  # microseconds

# this file path must be absolute
output_path = "/Users/margotriggi/Documents/Postdoc/Hb/"

trajectory_name = "Haemoglobin_oxygen_CO_animation_20240419_test" #.simularium
display_title = "Haemoglobin_O2_CO animation"
author_names = "Margot Riggi, Janet Iwasa"
animation_description = "An animation of O2 and CO interactions with haemoglobin in red blood cells"
box_dimensions = [15.0, 15.0, 15.0] # box will be centered at [0, 0, 0]
camera_position=[0.0, 0.0, 200.0]
camera_look_at_position=[0.0, 0.0, 0.0]
camera_fov_degrees=60.0
save_objs = False

# don't edit below ******************************************************************************

import maya.cmds as cmds
import numpy as np
from scipy.spatial.transform import Rotation
from simulariumio import (
    TrajectoryConverter, 
    TrajectoryData, 
    AgentData, 
    DimensionData,
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
if max_agents < 1:
    raise Exception("Select one or more objects to export.")
agent_data = AgentData.from_dimensions(
    DimensionData(
        total_steps=total_steps, 
        max_agents=max_agents
    )
)
agent_data.times = timestep * np.array(list(range(min_time, max_time + 1)))


# get display information
def rgb_to_hex(material_color):
    rgb = (
        int(255 * material_color[0][0]), 
        int(255 * material_color[0][1]), 
        int(255 * material_color[0][2])
    )
    return "#%02x%02x%02x" % rgb

def get_raw_and_display_type_names_and_uid(type_name, type_ix):
    uid = ""
    raw_name = type_name
    while len(raw_name) > 0 and raw_name[-1].isdigit():
        uid = raw_name[-1] + uid
        raw_name = raw_name[0:-1]
    if not manually_set_IDs:
        uid = type_ix
    else:
        try:
            uid = int(uid)
        except ValueError:
            raise Exception(
                "Please add digits to the end of each object's "
                "name in Maya in order to manually set IDs"
            )
    display_name = raw_name.split("__")[0]
    display_name = display_name.replace("_", " ")
    if logging:
        print(
            f"{type_name} -> raw_name = {raw_name}, "
            f"display name = {display_name}, uid = {uid}"
        )
    return raw_name, display_name, uid

for type_ix, type_name in enumerate(type_names):
    # get color 
    shaders = cmds.listConnections(cmds.listHistory(type_name))
    materials = [x for x in cmds.ls(cmds.listConnections(shaders), materials=1)]   
    color_rgb = cmds.getAttr(f"{materials[0]}.color")
    color_hex = rgb_to_hex(color_rgb)
    raw_name, display_name, _ = get_raw_and_display_type_names_and_uid(type_name, type_ix)
    # create display data
    if raw_name not in agent_data.display_data:
        agent_data.display_data[raw_name] = DisplayData(
            name=display_name,
            display_type=DISPLAY_TYPE.OBJ,
            url=geometry_urls[raw_name],
            color=color_hex,
        )


# get trajectory
def rotation_matrix_to_euler_angles(rotation_matrix):
    return -1 * Rotation.from_matrix(rotation_matrix).as_euler("xyz", degrees=False)

for time_ix, time in enumerate(range(min_time, max_time + 1)):
    cmds.currentTime(time)
    agent_ix = 0
    for type_ix, type_name in enumerate(type_names):
        # check visibility
        visible = cmds.getAttr(f"{type_name}.v")
        if not visible:
            continue
        # get transform
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
        # save agent data
        raw_name, _, uid = get_raw_and_display_type_names_and_uid(type_name, type_ix)
        agent_data.unique_ids[time_ix][agent_ix] = uid
        agent_data.types[time_ix].append(raw_name)
        agent_data.positions[time_ix][agent_ix] = position
        agent_data.rotations[time_ix][agent_ix] = rotation_matrix_to_euler_angles(rotation_matrix)
        agent_data.radii[time_ix][agent_ix] = scale[0]
        agent_ix += 1
    agent_data.n_agents[time_ix] = agent_ix
cmds.currentTime(min_time)

# export OBJs TODO
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
    agent_data=agent_data,
    time_units=UnitData(time_units),
    spatial_units=UnitData(spatial_units),
)

# save the file(s)
TrajectoryConverter(trajectory_data).save(f"{output_path}{trajectory_name}")
