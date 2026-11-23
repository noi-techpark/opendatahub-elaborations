# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

from pollution_computer.manager.pollution_computation import PollutionComputationManager


def test_only_windows_before_latest_record_are_kept():
    t0 = datetime(2026, 11, 23, 10, 0, tzinfo=timezone.utc)
    measures = [SimpleNamespace(valid_time=t0 + timedelta(minutes=10 * i)) for i in range(4)]
    latest = measures[-1].valid_time

    kept = PollutionComputationManager._drop_unfinished_windows(measures, latest)

    assert kept == measures[:3]


def test_nothing_kept_if_only_latest_window_present():
    t = datetime(2026, 11, 23, 10, 0, tzinfo=timezone.utc)
    assert PollutionComputationManager._drop_unfinished_windows([SimpleNamespace(valid_time=t)], t) == []
