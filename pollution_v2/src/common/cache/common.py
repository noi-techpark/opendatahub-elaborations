# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from __future__ import absolute_import, annotations

import json
import logging
import os
import sqlite3
import time
from abc import ABC, abstractmethod
from enum import Enum
from json import JSONDecodeError
from typing import Optional, TypeVar, Generic, Type

logger = logging.getLogger("pollution_v2.common.cache.common")


class TrafficManagerClass(Enum):

    POLLUTION = "POLLUTION"
    VALIDATION = "VALIDATION"
    DISPERSAL = "DISPERSAL"


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


class LocalCache(Generic[CacheDataType], ABC):
    """SQLite-backed key/value cache. Delete the db file to reset all checkpoints."""

    def __init__(self, db_path: str, cache_data_type: Type[CacheDataType]) -> None:
        self._cache_data_type = cache_data_type
        self._db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires_at REAL
                )
            """)

    def get(self, key: str) -> Optional[CacheDataType]:
        logger.debug(f"Getting cached data for key [{key}]")
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM cache WHERE key = ? AND (expires_at IS NULL OR expires_at > ?)",
                (key, time.time()),
            ).fetchone()
        if row is None:
            logger.debug(f"No data for key [{key}]")
            return None
        try:
            return self._cache_data_type.from_repr(json.loads(row[0]))
        except JSONDecodeError as e:
            logger.exception(f"Could not parse cached data for key [{key}]", exc_info=e)
            raise

    def set(self, data: CacheDataType, ttl: Optional[int] = None) -> None:
        """
        :param data: the data to cache
        :param ttl: time to live in seconds; None means no expiry
        """
        expires_at = time.time() + ttl if ttl else None
        logger.debug(f"Caching data for key [{data.unique_id()}] and ttl [{ttl}].")
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO cache (key, value, expires_at) VALUES (?, ?, ?)",
                (data.unique_id(), json.dumps(data.to_repr()), expires_at),
            )
