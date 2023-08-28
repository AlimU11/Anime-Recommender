"""
Config module.

Contains the Config class, which is used to store the configuration parameters of the Web App and ETL.
"""

import yaml
from pydantic import BaseModel


class Config(BaseModel):
    """Web App and ETL configuration parameters.

    Attributes
    ----------
    chunk_size : int
        The number of records to be processed during one iteration for computing similarity scores. In order to avoid
        unnecessary load on server the process of calculating recommendations is partioned into chunks. According to
        local tests, the value of 1000 has practically no impact on calculation time, but approx. 16.7 times less
        memory is consumed. The results of chunked calculations are almost the same (corr. coef > 0.999) as for
        non-chunked calculations. The actual difference is the result of precision changes (float64 to float16 to
        reduce RAM consumption) and common 'float values inaccuracy' while the order of operations (dot product, vector
        sum and precision change) is not the same. Moreover, it was observed that the result difference might lead to
        swapping of some pairs of titles in rare cases, which is, however, has almost zero affect on the final result.

    data_path : str
        Path to the raw data file. The data DataFrame contains all features for titles.

    metadata_path : str
        Path to the metadata file. The metadata DataFrame contains column names from data and their types.

    info_path : str
        Path to the info file. The info DataFrame contains only information required to display recommendations.

    data_staged_path : str
        Path to the staged data file. The staged data file is the previous version of the data file.

    metadata_staged_path : str
        Path to the staged metadata file. The staged metadata file is the previous version of the metadata file.

    data_processed_path : str
        Path to the processed data file. The processed data file is the current version of the data file.

    pagination_size : int
        The number of results returned by the API.

    api_url : str
        The URL of the API.

    api_period : int
        The period of time for which api_limit is applied.

    api_limit : int
        The number of requests allowed per api_period.

    dropdown_item_count : int
        The number of items displayed in the dropdown menu.
    """

    chunk_size: int
    data_path: str
    metadata_path: str
    info_path: str
    data_staged_path: str
    metadata_staged_path: str
    data_processed_path: str
    pagination_size: int
    api_url: str
    api_period: int
    api_limit: int
    dropdown_item_count: int


with open('global_config.yaml', 'r') as config_path:
    yaml_config = yaml.safe_load(config_path)

config = Config(**yaml_config)
