from pathlib import Path
from typing import List

from pydantic import BaseModel, Field


class SemphenConfigurations(BaseModel):
    """
    Class for defining the Exomiser configurations in tool_specific_configurations field,
    within the input_dir config.yaml
    Args:
        environment (str): Environment to run Exomiser, i.e., local/docker
        exomiser_software_directory (Path): Directory name for Exomiser software directory
        analysis_configuration_file (Path): The file name of the analysis configuration file located in the input_dir
        max_jobs (int): Maximum number of jobs to run in a batch
        application_properties (ApplicationProperties): application.properties configurations
        output_formats: List(str): List of raw output formats.
        post_process (PostProcessing): Post-processing configurations
    """

    environment: str = Field(...)
    path_to_semphen: str = Field(...)
    path_to_phenio: str = Field(...)
