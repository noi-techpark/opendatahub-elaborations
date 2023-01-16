from __future__ import absolute_import, annotations

import json
import logging
from abc import ABC, abstractmethod
from json import JSONDecodeError
from typing import Optional, TypeVar, Generic, Type

import redis

logger = logging.getLogger("pollution_connector.cache.redis_cache")


class CacheData(ABC):

    @abstractmethod
    def to_repr(self) -> dict:
        pass

    @staticmethod
    @abstractmethod
    def from_repr(raw_data: dict) -> CacheData:
        pass

    @abstractmethod
    def unique_id(self) -> str:
        pass


CacheDataType = TypeVar("CacheDataType", bound=CacheData)


class RedisCache(Generic[CacheDataType], ABC):

    def __init__(self, r: redis.Redis, cache_data_type: Type[CacheDataType]) -> None:
        self._cache_data_type = cache_data_type
        self._r = r

    def get(self, key: str) -> Optional[CacheDataType]:
        logger.info(f"Getting cached data for key [{key}]")
        result = self._r.get(key)
        if result is not None:
            try:
                result = self._cache_data_type.from_repr(json.loads(result))
            except JSONDecodeError as e:
                logger.exception(f"Could not parse cached data for key [{key}]", exc_info=e)
                raise e
        else:
            logger.debug(f"No data for key [{key}]")

        return result

    def set(self, data: CacheDataType, ttl: Optional[int] = None) -> None:
        """
        Cache the data in dict format inside the redis db.

        :param data: the data to cache
        :param key: the key to save the data
        :param ttl: the time to live of the data entry (expressed in seconds)
        """
        logger.info(f"Caching data for key [{data.unique_id()}] and ttl [{ttl}].")
        if ttl:
            self._r.set(data.unique_id(), json.dumps(data.to_repr()), ex=ttl)
        else:
            self._r.set(data.unique_id(), json.dumps(data.to_repr()))
