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

geometry_urls = {
     "Antigen1" : "https://www.dropbox.com/scl/fi/e77e7cyhx7kukrkk6fry8/Antigen.obj?rlkey=kpq7inxd4pkn0gs98f2c0quun&dl=0",
     "Antigen2" : "https://www.dropbox.com/scl/fi/e77e7cyhx7kukrkk6fry8/Antigen.obj?rlkey=kpq7inxd4pkn0gs98f2c0quun&dl=0",
     "Antigen3" : "https://www.dropbox.com/scl/fi/e77e7cyhx7kukrkk6fry8/Antigen.obj?rlkey=kpq7inxd4pkn0gs98f2c0quun&dl=0",
     "Antigen4" : "https://www.dropbox.com/scl/fi/e77e7cyhx7kukrkk6fry8/Antigen.obj?rlkey=kpq7inxd4pkn0gs98f2c0quun&dl=0",
     "Antigen5" : "https://www.dropbox.com/scl/fi/e77e7cyhx7kukrkk6fry8/Antigen.obj?rlkey=kpq7inxd4pkn0gs98f2c0quun&dl=0",
     "Antigen6" : "https://www.dropbox.com/scl/fi/e77e7cyhx7kukrkk6fry8/Antigen.obj?rlkey=kpq7inxd4pkn0gs98f2c0quun&dl=0",
     "Antigen7" : "https://www.dropbox.com/scl/fi/e77e7cyhx7kukrkk6fry8/Antigen.obj?rlkey=kpq7inxd4pkn0gs98f2c0quun&dl=0",
     "Antigen8" : "https://www.dropbox.com/scl/fi/e77e7cyhx7kukrkk6fry8/Antigen.obj?rlkey=kpq7inxd4pkn0gs98f2c0quun&dl=0",
     "Antigen9" : "https://www.dropbox.com/scl/fi/e77e7cyhx7kukrkk6fry8/Antigen.obj?rlkey=kpq7inxd4pkn0gs98f2c0quun&dl=0",
     "Antigen10" : "https://www.dropbox.com/scl/fi/e77e7cyhx7kukrkk6fry8/Antigen.obj?rlkey=kpq7inxd4pkn0gs98f2c0quun&dl=0",
     "Antigen11" : "https://www.dropbox.com/scl/fi/e77e7cyhx7kukrkk6fry8/Antigen.obj?rlkey=kpq7inxd4pkn0gs98f2c0quun&dl=0",
     "Antibody1" : "https://www.dropbox.com/scl/fi/sp9nb0udohs3fe7nwzlrh/Antibody.obj?rlkey=t0jy5wdkx9039x6waeynjtn9c&dl=0",
     "Antibody2" : "https://www.dropbox.com/scl/fi/sp9nb0udohs3fe7nwzlrh/Antibody.obj?rlkey=t0jy5wdkx9039x6waeynjtn9c&dl=0",
     "Antibody3" : "https://www.dropbox.com/scl/fi/sp9nb0udohs3fe7nwzlrh/Antibody.obj?rlkey=t0jy5wdkx9039x6waeynjtn9c&dl=0",
     "Antibody4" : "https://www.dropbox.com/scl/fi/sp9nb0udohs3fe7nwzlrh/Antibody.obj?rlkey=t0jy5wdkx9039x6waeynjtn9c&dl=0",
     "Complex1": "https://www.dropbox.com/scl/fi/gaa670l67pi6bc4h0j9d9/Complex.obj?rlkey=d6vhexhgh1kibr39kzvxzp7s2&dl=0",
     "Complex2": "https://www.dropbox.com/scl/fi/gaa670l67pi6bc4h0j9d9/Complex.obj?rlkey=d6vhexhgh1kibr39kzvxzp7s2&dl=0",
     "Complex3": "https://www.dropbox.com/scl/fi/gaa670l67pi6bc4h0j9d9/Complex.obj?rlkey=d6vhexhgh1kibr39kzvxzp7s2&dl=0",
     "Complex4": "https://www.dropbox.com/scl/fi/gaa670l67pi6bc4h0j9d9/Complex.obj?rlkey=d6vhexhgh1kibr39kzvxzp7s2&dl=0",
     "Antigen" : "https://www.dropbox.com/scl/fi/e77e7cyhx7kukrkk6fry8/Antigen.obj?rlkey=kpq7inxd4pkn0gs98f2c0quun&dl=0",
     "Antibody" : "https://www.dropbox.com/scl/fi/sp9nb0udohs3fe7nwzlrh/Antibody.obj?rlkey=t0jy5wdkx9039x6waeynjtn9c&dl=0",
     "Complex": "https://www.dropbox.com/scl/fi/gaa670l67pi6bc4h0j9d9/Complex.obj?rlkey=d6vhexhgh1kibr39kzvxzp7s2&dl=0",
     
}
spatial_units = "nm"  # nanometers
timestep = 2.0  # time that passes each step
time_units = "us"  # microseconds

# this file path must be absolute
output_path = "/Users/blairl/Dropbox/ForBlair_20231002/"
# output_path = "/Users/margotriggi/Documents/SpringSaladTutorial/TestAgAb/TestSimulariumExport"

trajectory_name = "AgAb_animation" #.simularium
display_title = "Antibody-Antigen animation"
author_names = "Margot Riggi, Janet Iwasa"
animation_description = "An animation of an antibody binding an antigen."
box_dimensions = [300.0, 300.0, 300.0] # box will be centered at [0, 0, 0]
camera_position=[0.0, 0.0, 200.0]
camera_look_at_position=[0.0, 0.0, 0.0]
camera_fov_degrees=60.0
save_objs = False

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

# TODO
# to group agents by type (but couldn't find how to use it later)  
def getClass(x):
    word=(f"{x}")
    if (word[4]=="g"):
        return ("Antigen")
    elif (word[4]=="b"):
        return ("Antibody")
    else:
        return ("Complex")

agent_types=set ()    
type_names = cmds.ls(selection=True)
for type_name in type_names:
    agent_type=getClass(type_name)
    agent_types.add(agent_type)


# TODO
# convert shader colors to hex codes
def num_to_letter(x):
    if (x==10):
         return ("a")
    elif (x==11):
         return ("b")
    elif (x==12):
         return ("c")
    elif (x==13):
         return ("d")
    elif (x==14):
         return ("e")
    elif (x==15):
         return ("f")
    else:
        return (x)
        
def color_to_hex(color):
    rgb_color = (
        int(255 * color[0][0]), 
        int(255 * color[0][1]), 
        int(255 * color[0][2])
    )
    a=int((rgb_color[0])/16)
    b=int((((rgb_color[0])/16)-a)*16)
    c=int((rgb_color[1])/16)
    d=int((((rgb_color[1])/16)-c)*16)
    e=int((rgb_color[2])/16)
    f=int((((rgb_color[2])/16)-e)*16)        
    return ("#"+f"{num_to_letter(a)}{num_to_letter(b)}{num_to_letter(c)}{num_to_letter(d)}{num_to_letter(e)}{num_to_letter(f)}")


def rotation_matrix_to_euler_angles(rotation_matrix):
    return -1 * Rotation.from_matrix(rotation_matrix).as_euler("xyz", degrees=False)

# get display information
display_data={}
for type_name in type_names:
#for agent_type in agent_types:
    # get color 
    shaders = cmds.listConnections(cmds.listHistory(type_name))
    materials = [x for x in cmds.ls(cmds.listConnections(shaders), materials=1)]   
    colorRGB= cmds.getAttr (f"{materials[0]}.color")
    color_hex = color_to_hex(colorRGB)
    # create display data
    display_data[type_name] = DisplayData(
        name=type_name,
        display_type=DISPLAY_TYPE.OBJ,
        url=geometry_urls[type_name],
        color=color_hex,
    )
    
# get display information - one by agent type, but not sure how to use it later
#display_data={}
#for agent_type in agent_types:
    # get color
   # shaders = cmds.listConnections(cmds.listHistory(f"{agent_type}.1"))
   # materials = [x for x in cmds.ls(cmds.listConnections(shaders), materials=1)]   
   # colorRGB= cmds.getAttr (f"{materials[0]}.color")
   # color_hex = color_to_hex(colorRGB)
    # create display data
   # display_data[agent_type] = DisplayData(
        #name=agent_type,
        #display_type=DISPLAY_TYPE.OBJ,
        #url=geometry_urls[agent_type],
       # color=color_hex,
    #)


# get trajectory
for time_ix, time in enumerate(range(min_time, max_time + 1)):
    cmds.currentTime(time)
    positions.append([])
    rotations.append([])
    radii.append([])
    for type_name in type_names:
        vis=cmds.getAttr (f"{type_name}.v")
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
        # TODO
        if vis==True:
            positions[time_ix].append(position)
            rotations[time_ix].append(rotation_matrix_to_euler_angles(rotation_matrix))
            radii[time_ix].append(scale[0])
            # might exist a more elegant way! I'm just sending the object far away when they are supposed to not be visible (can we just "skip" timepoints if objects are not visible in Maya?)
        else:
            positions[time_ix].append([2000,2000,2000])
            rotations[time_ix].append(rotation_matrix_to_euler_angles(rotation_matrix))
            radii[time_ix].append(scale[0])
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
