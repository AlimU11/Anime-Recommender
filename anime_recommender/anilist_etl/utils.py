import os
import pickle
from typing import Any


def stage_file(obj: Any, path: str) -> None:
    if os.path.exists(path):
        if os.path.exists(path + '_old'):
            os.remove(path + '_old')

        os.rename(path, path + '_old')

    with open(path, 'wb') as f:
        pickle.dump(obj, f)
