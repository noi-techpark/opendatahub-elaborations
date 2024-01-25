// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.gtfs;

public enum Timepoint {
    approximate(0), exact(1);

    public final int value;

    Timepoint(int value) {
        this.value = value;
    }
}
