from pydantic import BaseModel, Field


class SemphenConfigurations(BaseModel):
    """
    Class for defining the semphen configurations in tool_specific_configurations field,
    within the input_dir config.yaml
    Args:
        environment (str): Environment to run semphen, i.e., local/docker (only local supported)
        path_to_semphen (str): File path to semphen.py 
        path_to_phenio (str): File path to phenio.db file
    """

    environment: str = Field(...)
    path_to_semphen: str = Field(...)
    path_to_phenio: str = Field(...)
