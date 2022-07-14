# .simularium File Format

.simularium format, which contains spatiotemporal trajectory data and can be loaded by the Simularium Viewer (https://simularium.allencell.org/viewer), can be saved as JSON or binary. 

## Data Structure

Both JSON and binary contain the following data structured like:
* **trajectory info**
  * version - 2.0
  * trajectoryTitle (optional) - a name for this run of the model
  * modelInfo (optional) - metadata about the model that produced this trajectory
    * title - display title for this model
    * authors - modelers name(s) in one string
    * version - version of the model that produced this trajectory
    * description - comments to display with the trajectory
    * doi - the DOI of the publication accompanying this model
    * sourceCodeUrl - if the code that generated this model is posted publicly, a link to the repository of source code
    * sourceCodeLicenseUrl - a link to the license for the source code
    * inputDataUrl - a link to any model configuration or parameter files posted publicly
    * rawOutputDataUrl - a link to any raw outputs from the source code posted publicly
  * timeUnits - unit info for temporal data (e.g. timeStepSize)
    * magnitude - multiplier for time values (in case they are not given in whole units)
    * name - unit name for time values (we support this list https://github.com/hgrecco/pint/blob/master/pint/default_en.txt)
  * timeStepSize - the amount of time that passes in the simulation for each time step
  * totalSteps - the total number of time steps, or frames, in the simulation trajectory
  * spatialUnits - unit info for spatial data (e.g. positions and radii)
    * magnitude - multiplier for spatial values (in case they are not given in whole units)
    * name - unit name for spatial values (we support units in this list https://github.com/hgrecco/pint/blob/master/pint/default_en.txt)
  * size X, Y, Z - size of the bounding volume for the simulation. for now only rectangular prisms are supported, and the width in X, Y, and Z dimensions is provided
  * cameraDefault - the default view of the camera (when the trajectory is loaded and when the view is reset)
    * position X, Y, Z - 3D position of the camera itself (default = [0, 0, 120])
    * lookAtPosition X, Y, Z - position the camera looks at (default = [0, 0, 0])
    * upVector X, Y, Z - the vector that defines which direction is "up" in the camera's view (default = [0, 1, 0])
    * fovDegrees - the angle defining the extent of the 3D world that is seen from bottom to top of the camera view (default = 75)
  * type mapping - for each agent type ID in the trajectory, information about how to display and render it:
    * name - the type name to display for all agents of this type. Optionally, this name can be followed by a hash and state tags for the agent’s current state delimited with underscores
      * ex: "actin#barbed_ATP_1" is parsed as agent type "actin" in states "barbed", "ATP", and "1"
      * ex: "actA" is parsed as agent type "actA" with no state information
      * if no name is provided, the agent type ID, an integer number, is used for display
    * geometry - rendering information for each agent type (note: only the first 100,000 geometry files will be loaded)
      * displayType - “SPHERE”, “FIBER”, “PDB”, “OBJ”, or "SPHERE_GROUP"
        * Default to “SPHERE”
        * for PDB, can provide either ID or full URL
      * url (optional)- local path or web URL, web URLs are required for streaming or loading the trajectory by URL
      * color (optional) - hex value 

* **spatial data** - spatial data was designed to be sent in bundles from the simularium-engine in order to eventually support live simulation rendering. Therefore, each block of spatial data has metadata: msgType, bundleStart, and bundleSize.
  * version - 1.0
  * msgType - always 1
  * bundleStart - the frame index of the first frame in the bundle
  * bundleSize - the number of frames in the bundle
  * bundleData - a list of frames, for each frame:
    * frameNumber - the index of this frame in the trajectory
    * time - the simulated time at this frame
    * data - a buffer of agent instance data, in order for each instance:
      * visualization type
        * 1000 = default, rendered with PDB or mesh
        * 1001 = fiber, rendered as a line
      * agent instance ID - integer number ID for this agent instance
      * agent type ID - integer number ID for the agent’s type. This is used to look up its display data (name and geometry)
      * position X, Y, Z - agent’s 3D position
      * rotation X, Y, Z - euler angles for agent’s orientation
      * radius - the radius the agent occupies, used for drawing a sphere or for scaling other geometry representations
      * subpoints - the number of proceeding values that are extra data belonging to this agent, followed by a list of numerical data
        * for default type (1000), this is not used
          * ex: subpoints = 0
        * for fiber type (1001), this is the list of positions XYZ of the points along the fiber
          * ex: subpoints = 9, pos1 X, pos1 Y, pos1 Z, pos2 X, pos2 Y, pos2 Z, pos3 X, pos3 Y, pos3 Z 
* **plot data** - a list of plots, either scatterplots or histograms, for each:
  * version - 1.0
  * data - a list of plots, each has:
    * layout
      * title - label for the plot
      * xaxis 
        * title - the x-axis label
        * if this label contains the text "time", scatterplots will be considered time dependent and have a dynamic time bar rendered over them
      * yaxis
        * title - the y-axis label
    * data - a list of traces, for each
      * name - the label for this trace
      * type - either "scatter" or "histogram"
      * x - a list of x-values
      * y - only for a scatterplot, a list of y-values, one for each x-value
      * mode - only for a scatterplot, draw the data points as either "lines" or "markers", if not provided default to markers

## JSON Files

For JSON files, the data structure specified above is simply saved as JSON, with utf-8 encoding. For example:

```javascript
{
    // trajectory info
    "trajectoryInfo" : {
        "version" : 3,
        // model metadata
        "trajectoryTitle" : "Fast diffusion",
        "modelInfo" : {
            "title" : "SARS-CoV-2 Dynamics in Human Lung Epithelium"
            "version" : 4.1
            "authors" : "Michael Getz et al"
            "description" : "A PhysiCell model of SARS-CoV-2 dynamics in human lung epithelium."
            "doi" : "10.1101/2020.04.02.019075"
            "sourceCodeUrl" : "https://github.com/pc4covid19/pc4covid19"
        },
        // time units
        "timeUnits": {
            "magnitude": 1.0,
            "name": "ms",
        },
        // time
        "timeStepSize" : 0.5,
        "totalSteps" : 1000,
        // spatial units
        "spatialUnits": {
            "magnitude": 1.0,
            "name": "nm",
        },
        // box size
        "size" : {
            "x" : 300,
            "y" : 300,
            "z" : 300
        },
        // default camera position and orientation
        "cameraDefault" : {
            "position" : {            
                "x" : 0,
                "y" : 0,
                "z" : 120
            },
            "lookAtPosition" : {            
                "x" : 0,
                "y" : 0,
                "z" : 0
            },
            "upVector" : {            
                "x" : 0,
                "y" : 1,
                "z" : 0
            },
            "fovDegrees" : 75,
        },
        // agent display data
        "typeMapping": {
            "0" : {
                "name" : "agent1",
                "geometry" : {
                    "displayType" : "FIBER",
                },
            },
            "1" : {
                "name" : "agent1#bound",
                "geometry" : {
                    "displayType" : "PDB",
                    "url" : "agent1.pdb",  // optional
                    "color" : "#4796bd",   // optional
                },
            },
            "2" : {
                "name" : "agent2",
                "geometry" : {
                    "displayType" : "SPHERE",
                },
            },
            ...
        }
    },
    // spatial data 
    "spatialData" : {
        "version" : 1,
        "msgType" : 1,
        "bundleStart" : 0,
        "bundleSize" : 5,
        "bundleData": [
            { "frameNumber" : 0, "time" : 0, "data" : [...] },
            { "frameNumber" : 1,  
              "time" : 0.5,  
              "data" : [  
                  // first agent : default
                  1000.0,// visualization type : default
                  0.0,   // agent instance ID
                  2.0,   // agent type ID
                  15.5,  // position X
                  15.6,  // position Y
                  15.7,  // position Z  
                  45.25, // rotation X
                  45.26, // rotation Y
                  45.27, // rotation Z
                  1.0,   // radius
                  0.0,   // number of subpoint values following this number
                  // second agent : fiber
                  1001.0,// visualization type : fiber
                  1.0,   // agent instance ID
                  0.0,   // agent type ID
                  15.5,  // position X
                  15.6,  // position Y
                  15.7,  // position Z
                  0.0,   // rotation X
                  0.0,   // rotation Y
                  0.0,   // rotation Z
                  1.0,   // radius
                  9.0,   // number of subpoint values following this number
                  0.0,   // position1 X
                  1.0,   // position1 Y 
                  2.0,   // position1 Z
                  3.0,   // position2 X 
                  4.0,   // position2 Y 
                  5.0,   // position2 Z 
                  6.0,   // position3 X 
                  7.0,   // position3 Y 
                  8.0,   // position3 Z
                  ...
              ]
            },
            { "frameNumber" : 2, "time" : 1.0, "data" : [...] },
            { "frameNumber" : 3, "time" : 1.5, "data" : [...] },
            { "frameNumber" : 4, "time" : 2.0, "data" : [...] }
        ]
    },
    // plot data
    "plotData" : {
        "version" : 1,
        "data" : [  
            // scatterplot
            { 
                "layout" : {
                    "title" : "something over time",
                    "xaxis" : {
                        "title" : "time (ns)"
                    },
                    "yaxis" : {
                        "title" : "something (units)"
                    }
                },
                "data" : [
                    // first y-trace
                    {
                        "name" : "first thing",
                        "type" : "scatter",
                        "x" : [0, 10, 20, ...],
                        "y" : [1, 2, 3, ...],
                        "mode" : "markers"
                    },
                    // second y-trace
                    {
                        "name" : "second thing",
                        "type" : "scatter",
                        "x" : [0, 10, 20, ...],
                        "y" : [4, 5, 6, ...],
                        "mode" : "lines"
                    }
                ]
            },
            // histogram
            { 
                "layout" : {
                    "title" : "something",
                    "xaxis" : {
                        "title" : "something (units)"
                    },
                    "yaxis" : {
                        "title" : "frequency"
                    }
                },
                "data" : [
                    {
                        "name" : "something"
                        "type" : "histogram"
                        "x" : [1, 2, 3, 2, ...]
                    }
                ]
            }
        ]
    }
}
```

## Binary Files

For binary files, the data structure specified above is saved in blocks with additional info to help with reading the file. Some of the blocks can be saved as JSON within the binary file, but they must be utf-8 encoded. Currently JSON is the only format for trajectory info and plot data blocks.

Binary files must be smaller than 4GB, if the data is larger than this, it can be broken into multiple files, but data for each timestep should stay together in one file and not be split between multiple files.

```
// binary header
"SIMULARIUMBINARY" (binary identifier, 16-bytes)
Header length (4-byte int)
Binary version (4-byte int)
Number of blocks (4-byte int)
Block offset, type, and length (Number of blocks * 3 4-byte ints)

// for each block
Block type (4-byte int)
Block length (4-byte int) (includes block header)

    // type = 0 : spatial data block in JSON (see above)

    // type = 1 : trajectory info block in JSON (see above)

    // type = 2 : plot data block in JSON (see above)

    // type = 3 : spatial data block in binary
    Spatial data version (4-byte int)
    Number of frames (4-byte int)
    Frame offset and length (Number of frames * 2 4-byte int)

        // for each timestep
        Frame number (4-byte int)
        Time stamp (4-byte float)
        Number of agents (4-byte int)

            // for each agent at this timestep
            Visualization type (4-byte float)
            Agent instance ID (4-byte float)
            Agent type ID (4-byte float)
            Position X (4-byte float)
            Position Y (4-byte float)
            Position Z (4-byte float)
            Rotation X (4-byte float)
            Rotation Y (4-byte float)
            Rotation Z (4-byte float)
            Radius (4-byte float)
            Number of subpoints (4-byte float)
            Subpoints (4-byte floats, optional)

```