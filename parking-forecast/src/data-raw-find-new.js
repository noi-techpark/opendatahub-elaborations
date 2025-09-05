#!/usr/bin/env node

// SPDX-FileCopyrightText: 2021-2025 STA AG <info@sta.bz.it>
// SPDX-FileContributor: Chris Mair <chris@1006.org>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

// ----------------------------------------------------------------------------
//
// Parking occupancy prediction
// data-raw-find-new.js
//
// (C) 2024 STA AG
//
// Fetch list of stations and compare to files in data-raw/ to see if there
// is a new station that should be added.
//
// author: Chris Mair - chris@1006.org
//
// changelog:
// 2024-11-18 initial release
//
// ----------------------------------------------------------------------------

"use strict";

let child_process = require('child_process');
let fs = require("fs");

function https_get(url) {
    url = url.replace(/'/g, "%27");
    return String(child_process.spawnSync("curl", ["-H", "Referer: el-parking-forecast", "-L", url], {"timeout": 600000, "maxBuffer": 2*1024*1024*1024}).output[1]);
}

let zeropad = num => {
    let str = String(num);
    while (str.length < 2) {
        str = "0" + str;
    }
    return str;
};

// ----------------------------------------------------------------------------
(function() {

    // --- get the list of already known scodes and the next index ---

    const DIR = "data-raw/";
    let filenames = fs.readdirSync(DIR);
    filenames = filenames.filter( fn => fn.endsWith(".csv"));

    let known_scodes = [];
    let ix = 0;
    filenames.forEach( fn => {
        let parts = fn.split("__");
        if (parts.length < 3) {
            console.error(`fatal: invalid filename ${fn}`);
            process.exit(1);
        }
        known_scodes.push(parts[1]);
        ix = Number(parts[0]);
    });

    // --- get list of active stations from ODH

    let stations_url = "https://mobility.api.opendatahub.com/v2/flat/ParkingStation?limit=-1&distinct=true&where=sactive.eq.true";
    let stations;
    try {
        stations = JSON.parse(https_get(stations_url));
    } catch (ex) {
        console.log("ERROR: cannot parse JSON for stations_url - this is fatal, bailing out");
        process.exit(1);
    }
    if (stations.data === undefined) {
        console.log("ERROR: JSON for stations_url misses the expected data field - this is fatal, bailing out");
        process.exit(1);
    }

    let to_date   = new Date();
    let from_date = new Date(to_date);
    from_date.setSeconds(from_date.getSeconds() - 86400 * 99); // subtract 1 day (will correctly overflow)

    stations.data.sort( (a, b) => (a.scode < b.scode)).forEach( station => {

        /* interesting station fields:
             scode: '103',
             scoordinate: [Object],
             smetadata: [Object],
             sname: 'P03 - Piazza Walther',
             sorigin: 'FAMAS',
             stype: 'ParkingStation'
        */

        if (known_scodes.includes(station.scode)) {
            console.log("info: SKIP scode = " + station.scode + " is already known");
            return;
        }

        // try to fetch data for the last 24 hours to see if this is not dead

        console.log("info: NEW  scode = " + station.scode + " is a candidate for a new station");

        let data_url = `https://mobility.api.opendatahub.com/v2/flat/ParkingStation/occupied/${from_date.toISOString()}/${to_date.toISOString()}?limit=-1&distinct=true&select=mvalue,mvalidtime,mperiod&where=and%28scode.eq.%22${station.scode}%22%2Csactive.eq.true%29`
        let name = station.scode + "__" + String(station.sname).replace(/[.\s\/:]/g, "_") + ".csv";
        let ready = false;
        let data;
        try {
            data = JSON.parse(https_get(data_url));
        } catch (ex) {
            console.log("  KO as I cannot parse the JSON");
            console.log(data);
            return;
        }
        if (data.data === undefined) {
            console.log("  KO as the JSON misses the expected data field");
            return;
        }

        let lines = [];
        data.data.forEach( point => {
            /* interesting point fields:
                mperiod: 300,
                mvalidtime: '2021-03-10 08:20:00.358+0000',
                mvalue: 484
             */
            lines.push(`"${point.mvalidtime}","${point.mvalue}"`);
        });

        if (lines.length < 10) {
            console.log("  KO as there are too few data points (" + lines.length + ")");
            console.log("filename would have been: "  + (zeropad(ix + 1) + "__" + name));
            return;
        } else {
            let csv = zeropad(++ix) + "__" + name;
            console.log("  OK (" + lines.length + " lines): " + csv);
            fs.writeFileSync("data-raw/" + csv, lines.sort().join("\n"));
        }
    });

})();
