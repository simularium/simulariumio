from IPython.display import Image
from simulariumio.springsalad import SpringsaladConverter, SpringsaladData
from simulariumio import DisplayData, DISPLAY_TYPE, MetaData, ModelMetaData, InputFileData

example_data = SpringsaladData(
    sim_view_txt_file=InputFileData(
        file_path="/Users/margotriggi/Documents/Postdoc/Tests/Test_export.txt",
    ),
    meta_data=MetaData(
        trajectory_title="Some parameter set",
        model_meta_data=ModelMetaData(
            title="Antigen Antibody binding model",
            version="8.1",
            authors="A Modeler",
            description=(
                "An agent-based model run with some parameter set"
            ),
            doi="10.1016/j.bpj.2016.02.002",
            source_code_url="https://github.com/simularium/simulariumio",
            source_code_license_url="https://github.com/simularium/simulariumio/blob/main/LICENSE",
            input_data_url="https://allencell.org/path/to/native/engine/input/files",
            raw_output_data_url="https://allencell.org/path/to/native/engine/output/files",
        ),
    ),
        display_data={
        "CYAN": DisplayData(
            name="Antibody",
            radius=1.0,
            display_type=DISPLAY_TYPE.OBJ,
            url="Antibody.obj",
            color="#73E5FF",
        ),
        "ORANGE": DisplayData(
            name="Antigen",
            radius=1.0,
            display_type=DISPLAY_TYPE.OBJ,
            url="Antigen.obj",
            color="#FFC673",
        ),
    },
        draw_bonds=True,
)


SpringsaladConverter(example_data).save("test_simularium_MayaTrajectory")
