import os
import pickle
from typing import Any


def stage_file(obj: Any, path: str):
    """Stage object to file.

    Stage object with pickle to file using corresponding path. Before that, checks if path exists and if it does, rename
    it by appending suffix `_old`. Additionally, checks if path with suffix `_old` exists and if it does, removes it.

    Parameters
    ----------
    obj : Any
        Object to be staged.

    path : str
        Path to file.
    """
    if os.path.exists(path):
        if os.path.exists(path + '_old'):
            os.remove(path + '_old')

        os.rename(path, path + '_old')

    with open(path, 'wb') as f:
        pickle.dump(obj, f)
