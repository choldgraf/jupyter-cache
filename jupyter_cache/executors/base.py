from abc import ABC, abstractmethod
import logging
import pkg_resources
from typing import List, Optional

from jupyter_cache.base import JupyterCacheAbstract

# TODO abstact
from jupyter_cache.cache.db import NbCacheRecord

ENTRY_POINT_GROUP = "jupyter_executors"

base_logger = logging.getLogger(__name__)


class ExecutionError(Exception):
    pass


class JupyterExecutorAbstract(ABC):
    """An abstract class for executing notebooks in a cache."""

    def __init__(self, cache: JupyterCacheAbstract, logger=None):
        self._cache = cache
        self._logger = logger or logging.getLogger(__name__)

    @property
    def cache(self):
        return self._cache

    @property
    def logger(self):
        return self._logger

    @abstractmethod
    def run_and_cache(
        self,
        filter_uris: Optional[List[str]] = None,
        filter_pks: Optional[List[int]] = None,
    ) -> List[NbCacheRecord]:
        """Run execution, stage successfully executed notebooks and return their URIs

        Parameters
        ----------
        filter_uris: list
            If specified filter the staged notebooks to execute by these URIs
        filter_pks: list
            If specified filter the staged notebooks to execute by these PKs
        """
        pass


def load_executor(
    entry_point: str, cache: JupyterCacheAbstract, logger=None
) -> JupyterExecutorAbstract:
    """Retrieve an initialised JupyterExecutor from an entry point."""
    entry_points = list(pkg_resources.iter_entry_points(ENTRY_POINT_GROUP, entry_point))
    if len(entry_points) == 0:
        raise ImportError(
            "Entry point not found: {}.{}".format(ENTRY_POINT_GROUP, entry_point)
        )
    if len(entry_points) != 1:
        raise ImportError(
            "Multiple entry points found: {}.{}".format(ENTRY_POINT_GROUP, entry_point)
        )
    execute_cls = entry_points[0].load()
    return execute_cls(cache=cache, logger=logger)
