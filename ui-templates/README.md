# UI Templates
These JSON objects define templates for capturing user data from a UI and using it to set the parameters of SimulariumIO objects in order to visualize simulation trajectories.


## Data types
Different types of data need to be collected. Some of the data types are "base" HTML Form Input types, and some are "custom" types that contain parameters of the base types or other custom types. Some custom types are "main" types for visualizing data from a specific simulation engine.

Each custom data type has:
* `python::module` - Python module
* `python::object` - Python class for the object to populate
* `parameters` - a mapping of names of members of the Python class to information about how to set them. For each:
  * `name` - the name to display next to the UI Input element
  * `data_type` - the data type to collect, either a base or custom data type
  * `description` - a description of this field to help the user
  * `required` - is this field required in order to submit?
  * some types also have additional parameter information

### Main types
* `smoldyn_data` - information for populating a `SmoldynData` to visualize a trajectory from Smoldyn
* (more coming soon)

### Base types

* `number`
* `text`
* `url`
* `color`


### Custom types

* `meta_data`
* `coordinates_xyz`
  * parameters are indices of items in a list to be provided as a single argument to `numpy.array()`
* `camera_data`
* `model_meta_data`
* `mapping`
  * requires additional parameter information:
    * `key_name` - the name to display next to the UI Input element for the key
    * `key_data_type` - name of the data type tp collect for the key
    * `value_name` - the name to display next to the UI Input element for the value
    * `value_data_type` - name of the data type tp collect for the value
* `display_data`
* `enum`
  * requires additional parameter information:
    * `python::module` - Python module for the enum
    * `python::object` - Python name of the enum
    * `options` - enum values that a user can choose
* `unit_data`
