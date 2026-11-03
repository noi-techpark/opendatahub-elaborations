# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import threading
import time
from datetime import datetime
from types import SimpleNamespace
from typing import List
from unittest.mock import MagicMock

import pytest

from common.manager.traffic_station import TrafficStationManager
from common.settings import DEFAULT_TIMEZONE

DOWNLOAD_S = 0.15
UPLOAD_S = 0.25


class _Manager(TrafficStationManager):
    """Manager with fake download/upload which record what happens and when."""

    def __init__(self, fail_upload_of_batch: int = None, fail_download_of_batch: int = None):
        super().__init__(MagicMock(), MagicMock(), None)
        self.events: List[tuple] = []
        self.fail_upload_of_batch = fail_upload_of_batch
        self.fail_download_of_batch = fail_download_of_batch
        self.upload_threads = set()
        self._lock = threading.Lock()

    def _log(self, name, day):
        with self._lock:
            self.events.append((name, day, time.monotonic()))

    def at(self, name, day):
        return next(t for n, d, t in self.events if n == name and d == day)

    def names(self):
        return [(n, d) for n, d, _ in self.events]

    def _get_manager_code(self) -> str:
        return "TEST"

    def get_input_connector(self):
        return MagicMock()

    def get_output_connector(self):
        return MagicMock()

    def _get_data_types(self):
        return []

    def _build_from_entries(self, input_entries):
        return None

    def get_starting_date(self, *args, **kwargs):
        start = DEFAULT_TIMEZONE.localize(datetime(2026, 1, 1))
        return start, start

    def _get_latest_date(self, *args, **kwargs):
        return DEFAULT_TIMEZONE.localize(datetime(2027, 1, 1))

    def _download_data_and_compute(self, start_date, to_date, stations):
        day = start_date.day
        self._log("download_start", day)
        time.sleep(DOWNLOAD_S)
        if day == self.fail_download_of_batch:
            raise RuntimeError("download failed")
        self._log("download_end", day)
        return [object()] * 10

    def _upload_data(self, input_entries, output_alternative_connector=None):
        day = self._current_upload_day
        self.upload_threads.add(threading.current_thread().name)
        self._log("upload_start", day)
        time.sleep(UPLOAD_S)
        if day == self.fail_upload_of_batch:
            raise RuntimeError("upload failed")
        self._log("upload_end", day)

    def _upload_entries(self, entries, start_date, to_date, stations):
        self._current_upload_day = start_date.day
        return super()._upload_entries(entries, start_date, to_date, stations)

    def _update_cache(self, to_date, stations):
        self._log("cache", to_date.day)


def _run(manager: _Manager, days: int = 4):
    stations = [SimpleNamespace(code="A22:1:1")]
    start = DEFAULT_TIMEZONE.localize(datetime(2026, 1, 1))
    end = DEFAULT_TIMEZONE.localize(datetime(2026, 1, 1 + days))
    return manager.run_computation(stations, start, end, batch_size=1, keep_looking_for_input_data=False)


def test_upload_overlaps_next_download_but_never_other_uploads():
    manager = _Manager()
    stats = _run(manager)

    assert stats.batches == 4 and stats.entries == 40
    # uploads are strictly sequential and chronological, in a single background thread
    uploads = [(d, manager.at("upload_start", d), manager.at("upload_end", d)) for d in (1, 2, 3, 4)]
    for (_, _, end), (_, next_start, _) in zip(uploads, uploads[1:]):
        assert end <= next_start
    assert len(manager.upload_threads) == 1 and threading.current_thread().name not in manager.upload_threads
    # the next batch is downloaded while the previous one is still being uploaded
    for day in (1, 2, 3):
        assert manager.at("download_start", day + 1) < manager.at("upload_end", day)
    # downloads never overlap each other
    for day in (1, 2, 3):
        assert manager.at("download_end", day) <= manager.at("download_start", day + 1)


def test_checkpoint_moves_only_after_the_upload_and_in_order():
    manager = _Manager()
    _run(manager)

    cache_days = [d for n, d, _ in manager.events if n == "cache"]
    assert cache_days == [2, 3, 4, 5]
    for day in (1, 2, 3, 4):
        assert manager.at("cache", day + 1) >= manager.at("upload_end", day)
    for day in (1, 2, 3):
        assert manager.at("cache", day + 1) <= manager.at("upload_start", day + 1)


def test_pipelining_is_faster_than_sequential():
    pipelined = _Manager()
    t0 = time.monotonic()
    _run(pipelined)
    pipelined_s = time.monotonic() - t0

    sequential = _Manager()
    sequential._pipelined_uploads = False
    t0 = time.monotonic()
    _run(sequential)
    sequential_s = time.monotonic() - t0

    assert sequential_s > 4 * (DOWNLOAD_S + UPLOAD_S) * 0.95
    # the last upload cannot be hidden and an upload can only hide behind a download: 3 overlaps of the shorter one
    assert pipelined_s < sequential_s - 3 * min(DOWNLOAD_S, UPLOAD_S) * 0.8


def test_failed_upload_stops_the_run_and_nothing_later_is_uploaded_or_checkpointed():
    manager = _Manager(fail_upload_of_batch=2)
    with pytest.raises(RuntimeError, match="upload failed"):
        _run(manager)

    names = manager.names()
    assert ("upload_start", 3) not in names and ("upload_start", 4) not in names
    # batch 1 is checkpointed, the failed batch 2 and the later ones are not
    assert [d for n, d in names if n == "cache"] == [2]


def test_failed_download_still_finishes_and_checkpoints_the_running_upload():
    manager = _Manager(fail_download_of_batch=3)
    with pytest.raises(RuntimeError, match="download failed"):
        _run(manager)

    names = manager.names()
    assert ("upload_end", 2) in names
    assert [d for n, d in names if n == "cache"] == [2, 3]
    assert ("upload_start", 3) not in names
