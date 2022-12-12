# UI Templates
These JSON objects define templates for capturing user data from a UI and using it to set the parameters of SimulariumIO objects in order to visualize simulation trajectories.


## Data types
Different types of data need to be collected. Some of the data types are "base" HTML Form Input types, and some are "custom" types that contain parameters of the base types or other custom types. Some custom types are "main" types for visualizing data from a specific simulation engine.

Each custom data type has:
* `python::module` - Python module
* `python::object` - Python class for the object to populate
* `parameters` - a dict of names of members of the Python class mapped to information about how to set them. For each:
  * `name` - the name to display next to the UI Input element
  * `data_type` - the data type to collect, either a base or custom data type
  * `description` - instructions for the user about how to fill this field
  * `required` - is this field required in order to submit?
  * `default` - the default value to use if none is provided by user, if not provided for a required field, the default is `None`
  * `match` - a regex pattern to validate the data against (optional)
  * `help` - additional information to help the user, including what default value will be used (optional)
  * some types also have additional parameter information

### Main types
* `smoldyn_data` - information for populating a `SmoldynData` to visualize a trajectory from Smoldyn
* `cytosim_data` - information for populating a `CytosimData` to visualize a trajectory from Cytosim
* `medyan_data` - information for populating a `MedyanData` to visualize a trajectory from Medyan
* `springsalad_data` - information for populating a `SpringsaladData` to visualize a trajectory from SpringSaLaD
* `cellpack_data` - information for populating a `CellpackData` to visualize a trajectory from Cellpack

### Base types

* `float`
* `text`
* `url`
* `color`
* `boolean`

### Custom types

* `meta_data`
* `coordinates_xyz`
  * parameters are indices of items in a list to be provided as a single argument to `numpy.array()`
* `camera_data`
* `model_meta_data`
* `collection` - collect an extensible list of information and use it to create a dict
  * requires additional parameter information:
    * `length` - number of items to start with
    * `extendible`- can the user add more items?
    * `key_item` - requires the same fields as `parameters` items
    * `value_item` - requires the same fields as `parameters` items
* `display_data`
* `enum`
  * requires additional parameter information:
    * `python::module` - Python module for the enum
    * `python::object` - Python name of the enum
    * `options` - enum values that a user can choose
* `time_unit_data`
* `space_unit_data`
* `cytosim_object_info`
