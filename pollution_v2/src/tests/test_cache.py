# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import time
from datetime import datetime, timezone
from pathlib import Path

import pytest

from common.cache.computation_checkpoint import ComputationCheckpoint, ComputationCheckpointCache


@pytest.fixture
def cache(tmp_path: Path) -> ComputationCheckpointCache:
    return ComputationCheckpointCache(str(tmp_path / "test_cache.db"))


def _checkpoint(station_code: str = "TEST-001") -> ComputationCheckpoint:
    return ComputationCheckpoint(
        station_code=station_code,
        checkpoint_dt=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
        manager_code="POLLUTION",
    )


def test_set_and_get(cache: ComputationCheckpointCache) -> None:
    cp = _checkpoint()
    cache.set(cp)
    result = cache.get(cp.unique_id())
    assert result is not None
    assert result.station_code == cp.station_code
    assert result.checkpoint_dt == cp.checkpoint_dt
    assert result.manager_code == cp.manager_code


def test_get_missing_key_returns_none(cache: ComputationCheckpointCache) -> None:
    assert cache.get("nonexistent-key") is None


def test_overwrite(cache: ComputationCheckpointCache) -> None:
    cp1 = _checkpoint()
    cache.set(cp1)

    cp2 = ComputationCheckpoint(
        station_code=cp1.station_code,
        checkpoint_dt=datetime(2024, 6, 1, 0, 0, 0, tzinfo=timezone.utc),
        manager_code=cp1.manager_code,
    )
    cache.set(cp2)

    result = cache.get(cp1.unique_id())
    assert result.checkpoint_dt == cp2.checkpoint_dt


def test_ttl_expiry(cache: ComputationCheckpointCache) -> None:
    cp = _checkpoint()
    cache.set(cp, ttl=1)
    assert cache.get(cp.unique_id()) is not None
    time.sleep(1.1)
    assert cache.get(cp.unique_id()) is None


def test_no_ttl_does_not_expire(cache: ComputationCheckpointCache) -> None:
    cp = _checkpoint()
    cache.set(cp)
    # Without TTL entries should persist indefinitely; we just verify it's still there
    assert cache.get(cp.unique_id()) is not None


def test_different_manager_codes_are_independent(cache: ComputationCheckpointCache) -> None:
    cp_poll = ComputationCheckpoint("STA-1", datetime(2024, 1, 1, tzinfo=timezone.utc), "POLLUTION")
    cp_valid = ComputationCheckpoint("STA-1", datetime(2024, 2, 1, tzinfo=timezone.utc), "VALIDATION")

    cache.set(cp_poll)
    cache.set(cp_valid)

    assert cache.get(cp_poll.unique_id()).checkpoint_dt == cp_poll.checkpoint_dt
    assert cache.get(cp_valid.unique_id()).checkpoint_dt == cp_valid.checkpoint_dt
