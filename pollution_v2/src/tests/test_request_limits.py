# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import threading
import time

from common.connector.common import api_request_slot


def test_slot_is_shared_per_api_url():
    assert api_request_slot("https://reader.test") is api_request_slot("https://reader.test")
    assert api_request_slot("https://reader.test") is not api_request_slot("https://writer.test")


def test_one_request_at_a_time_per_api_but_independent_apis():
    active = {"reader": 0, "writer": 0}
    peak = {"reader": 0, "writer": 0}
    both_peak = 0
    lock = threading.Lock()

    def request(api: str):
        nonlocal both_peak
        with api_request_slot(f"https://{api}.test"):
            with lock:
                active[api] += 1
                peak[api] = max(peak[api], active[api])
                both_peak = max(both_peak, sum(active.values()))
            time.sleep(0.01)
            with lock:
                active[api] -= 1

    threads = [threading.Thread(target=request, args=(api,)) for api in ["reader", "writer"] * 8]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert peak == {"reader": 1, "writer": 1}
    # a read and a write may overlap, which is what allows the pipelining
    assert both_peak == 2
