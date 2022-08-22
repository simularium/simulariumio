## Simularium repositories
This repository is part of the Simularium project ([simularium.allencell.org](https://simularium.allencell.org)), which includes repositories:
- [simulariumIO](https://github.com/simularium/simulariumio) - Python package that converts simulation outputs to the format consumed by the Simularium viewer website
- [simularium-engine](https://github.com/simularium/simularium-engine) - C++ backend application that interfaces with biological simulation engines and serves simulation data to the front end website
- [simularium-viewer](https://github.com/simularium/simularium-viewer) - NPM package to view Simularium trajectories in 3D
- [simularium-website](https://github.com/simularium/simularium-website) - Front end website for the Simularium project, includes the Simularium viewer

<br/>

---
---
<br/>

# SimulariumIO
[![Build Status](https://github.com/simularium/simulariumio/workflows/CI/badge.svg)](https://github.com/simularium/simulariumio/actions)
[![Documentation](https://github.com/simularium/simulariumio/workflows/Documentation/badge.svg)](https://simularium.github.io/simulariumio)
[![Code Coverage](https://codecov.io/gh/simularium/simulariumio/branch/master/graph/badge.svg)](https://codecov.io/gh/simularium/simulariumio)

---
---

<br/>


## Convert simulation outputs so they can be visualized in the [Simularium Viewer](https://simularium.allencell.org/).

<br/>

# 1. Convert your data
Save your data as a .simularium file (see Jupyter notebook [examples](examples/)):

```python
import numpy as np
from simulariumio import TrajectoryConverter, TrajectoryData, MetaData, AgentData, ScatterPlotData

converter = TrajectoryConverter(
    TrajectoryData(
        meta_data=MetaData(
            box_size=BOX_SIZE_NUMPY_ARRAY,
            trajectory_title="Model A with parameter set 1",
        ),
        agent_data=AgentData(
            DATA_FOR_OBJECTS_MOVING_OVER_TIME
        ),
    )
)
converter.add_plot(
    ScatterPlotData(
        title="Something measured",
        xaxis_title="Time (s) or something else",
        yaxis_title="Some measurement (units)",
        xtrace=X_VALUES_NUMPY_ARRAY,
        ytraces={
            "Agent 1" : Y_VALUES_NUMPY_ARRAY,
        },
    )
)
converter.save("output_file_name")
```

[See more details](#quick-start)

<br/>

# 2. Load in the [Simularium Viewer](https://simularium.allencell.org/viewer)
Load your file in the Simularium Viewer at https://simularium.allencell.org/viewer to interactively rotate and play back your data:

![Loading a file in the Simularium Viewer](/examples/img/drag_drop.gif)

[See more details](#visualize-results)

<br/>

# 3. Share by URL 
Upload your file to a public Dropbox or Google Drive folder or an AWS S3 bucket, and use the URL https://simularium.allencell.org/viewer?trajUrl=LINK_TO_YOUR_FILE. For example, https://simularium.allencell.org/viewer?trajUrl=https://aics-simularium-data.s3.us-east-2.amazonaws.com/trajectory/endocytosis.simularium.

[See more details](#share-link-to-results)

<br/>

---
---

<br/>


## Features
* Converts 3D spatiotemporal trajectories to .simularium JSON format
* Accepts spatial trajectories from the following biological simulation engines:
    * CytoSim (https://gitlab.com/f.nedelec/cytosim)
    * MCell (https://mcell.org/)
    * MEDYAN (http://medyan.org/)
    * PhysiCell (http://physicell.org/)
    * ReaDDy (https://readdy.github.io/)
    * Smoldyn (http://www.smoldyn.org/)
    * SpringSaLaD (https://vcell.org/ssalad)
    * Molecular dynamics trajectories via MDAnalysis (https://www.mdanalysis.org/)
* Conversions for data from custom engines can be implemented using the TrajectoryConverter class
* Also accepts metrics data for plots to display alongside spatial data

We're discussing the possibility of adding the ability to export Simularium files directly with the authors of some packages.

Current rendering capabilities of the viewer:
* Spheres: by default, each agent in a scene is represented as a single sphere
* Mesh surfaces: represent each agent as a mesh (loaded from an .obj file), e.g. coarse molecular surfaces
* Multi-sphere: provide Protein Databank .pdb files
* Line representations for fibers, filaments, or bonds

Rendering capabilities planned for future:
* Volume rendering for RDME or PDE-based simulation results
* Support for .cif files and coarse-grain sphereTree files for multi-sphere rendering

<br/>

---

<br/>

## Installation
**Install Requires:** 

* Requires Python 3.7, 3.8, or 3.9

* If ReaDDy trajectories will be converted, the ReaDDy python package must be installed:
(add conda forge channel if it's not already: `conda config --add channels conda-forge`)
`conda install readdy`

**Stable Release:** `pip install simulariumio`

**Development Head:** `pip install git+ssh://git@github.com/simularium/simulariumio.git`

**Please note** that to run the Jupyter notebook examples you should also install Jupyter, either with `pip install jupyter`, or by installing SimulariumIO with the tutorial requirements: `pip install simulariumio[tutorial]`

**Install time** depends on the speed of the connection and whether optional dependencies are included, but generally takes 30 seconds to a few minutes (see [benchmarks](benchmarks/README.md) for more details).


<br/>

---

<br/>

## Quick Start

### Convert spatial trajectory from a supported engine
See the Tutorial for the simulation engine you're using for details:
* [Cytosim Tutorial](examples/Tutorial_cytosim.ipynb)
* [MCell Tutorial](examples/Tutorial_mcell.ipynb)
* [MEDYAN Tutorial](examples/Tutorial_medyan.ipynb)
* [PhysiCell Tutorial](examples/Tutorial_physicell.ipynb)
* [ReaDDy Tutorial](examples/Tutorial_readdy.ipynb)
* [Smoldyn Tutorial](examples/Tutorial_smoldyn.ipynb)
* [SpringSaLaD Tutorial](examples/Tutorial_springsalad.ipynb)
* [Molecular Dynamics Tutorial](examples/Tutorial_md.ipynb)

An overview for data from ReaDDy:
```python
import numpy as np
from simulariumio.readdy import ReaddyConverter, ReaddyData

# see ReaDDy Tutorial for parameter details
input_data = ReaddyData(
    meta_data=MetaData(
        box_size=BOX_SIZE,
    ),
    timestep=TIMESTEP,
    path_to_readdy_h5=PATH_TO_H5_FILE,
)
ReaddyConverter(input_data).save("output_file_name")
```

### Convert spatial trajectory from a custom engine
See the [Custom Data Tutorial](examples/Tutorial_custom.ipynb) for details. An overview:
```python
import numpy as np
from simulariumio import TrajectoryConverter, TrajectoryData, MetaData, AgentData

# see Custom Data Tutorial for parameter details
input_data = TrajectoryData(
    meta_data=MetaData(
        box_size=BOX_SIZE,
    ),
    agent_data=AgentData(
        times=TIMES,
        n_agents=N_AGENTS,
        viz_types=VIZ_TYPES,
        unique_ids=UNIQUE_IDS,
        types=TYPE_IDS,
        positions=POSITIONS,
        radii=RADII,
        rotations=ROTATIONS,
    )
)
TrajectoryConverter(input_data).save("output_file_name")
```

### Add metrics data to plot
See the [Plots Tutorial](examples/Tutorial_plots.ipynb) for details. An overview:
```python
import numpy as np
from simulariumio import ScatterPlotData

converter = TrajectoryConverter(input_data) # see above to create 
# see Plots Tutorial for parameter details
converter.add_plot(
    ScatterPlotData(
        title="Something measured",
        xaxis_title="Time (s) or something else",
        yaxis_title="Some measurement (units)",
        xtrace=X_VALUES,
        ytraces={
            "Agent 1" : Y_VALUES,
        },
    )
)
converter.save("output_file_name")
```

### Render with meshes or PDB files
If you'd like to render agents as meshes instead of spheres, add a `DisplayData` for each agent type you'd like to be rendered with the mesh, and specify an OBJ mesh file. Alternately, you can provide a Protein Databank (PDB) file to render atoms for a molecule. 

See the example notebook for the converter you are using to see how to add display data for that converter.
```python
display_data={
    "A" : DisplayData(
        name="Molecule A",
        display_type=DISPLAY_TYPE.PDB,
        url="https://files.rcsb.org/download/3KIN.pdb",
        color="#0080ff",
    ),
    "B" : DisplayData(
        name="Molecule B",
        display_type=DISPLAY_TYPE.OBJ,
        url="molecule_b.obj",
        color="#333333",
    ),
}
```

**Conversion time** depends on hardware, the size of the input data, and which converter is used, but generally takes between less than a minute and five minutes (see [benchmarks](benchmarks/README.md) for more details).

<br/>

---

<br/>

## Visualize results
1. In a supported browser (Firefox, Chrome, or Edge), navigate to https://simularium.allencell.org/viewer.
2. Drag the file output from SimulariumIO from your file browser onto the window or choose Load model > From your device, and select your file from the file upload dialogue.
- If your trajectory uses local geometry files, like .obj or .pdb files, load them at the same time as you load your .simularium file, either by dragging and dropping a collection of files, or by choosing multiple files in the upload dialogue.
- Currently the Viewer does not support loading folders of files, so make sure you are loading a collection of single files that does not include a folder. We're working to improve this.

<br/>

---

<br/>

## Share link to results
1. Upload your Simularium file to one of the supported public cloud providers, including Dropbox, Google Drive, or Amazon S3, and get a publicly accessible link to the file.
2. In a supported browser (Firefox, Chrome, or Edge), navigate to https://simularium.allencell.org.
3. Choose Load model > From a URL. In the dialog, provide the URL to your .simularium file and choose Load. 
- If your file uses geometry files, like .obj or .pdb files, make sure you've provided the full public URL to the files in `DisplayData`.
4. Once the file is loaded, you can copy the page URL and share this link with collaborators or post it on your website so that others can interactively view your results.

<br/>

---

<br/>

## Documentation
For full package documentation please visit [simularium.github.io/simulariumio](https://simularium.github.io/simulariumio).

<br/>

---

<br/>

## Development
See [CONTRIBUTING.md](CONTRIBUTING.md) for information related to developing the code.

