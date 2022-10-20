import multiprocessing.pool as mpp


def istarmap(self, func, iterable, chunksize=1):
    """Iterable version of starmap. Allows using starmap with tqdm and pass parameters to the pools in predefined order.

    Parameters
    ----------
    self : mpp.Pool
        multiprocessing pool object
    func : function
        function to apply to each element of iterable
    iterable : iterable
        iterable to apply func to
    chunksize : int, default: 1
        number of elements to apply func to at once

    Returns
    -------
    result : list
        list of results
    """
    self._check_running()
    if chunksize < 1:
        raise ValueError('Chunksize must be 1+, not {0:n}'.format(chunksize))

    task_batches = mpp.Pool._get_tasks(func, iterable, chunksize)
    result = mpp.IMapIterator(self)
    self._taskqueue.put(
        (
            self._guarded_task_generation(result._job, mpp.starmapstar, task_batches),
            result._set_length,
        ),
    )
    return (item for chunk in result for item in chunk)


mpp.Pool.istarmap = istarmap
