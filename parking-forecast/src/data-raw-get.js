#!/usr/bin/env node

// SPDX-FileCopyrightText: 2021-2025 STA AG <info@sta.bz.it>
// SPDX-FileContributor: Chris Mair <chris@1006.org>
//
// SPDX-License-Identifier: CC0-1.0

// ----------------------------------------------------------------------------
//
// Parking occupancy prediction
// data-raw-get.js
//
// (C) 2021-2023 STA AG
//
// Fetch all parking occupancy data for the indicated period
// (refer to from_date, to_date) from
//
// https://analytics.opendatahub.com
//
// and store the data into CSV files in dir "data-raw-candidate/"
// (one for each parking place).
//
// author: Chris Mair - chris@1006.org
//
// changelog:
// 2023-01-11 order data by timestamp (as ODH sometimes returns unordered data)
// 2022-11-18 added very verbose debug-logging to curl;
//            made the download resilient against all kind of things
//            that can go wrong:
//              - if getting the list of car parks fails,
//                exit immediately with exit code 1
//              - if getting data fails, skip the car park
//              - if the data contains <= 10 data points,
//                skip the car park as well
//              - at the end, if at least 5 car parks were written,
//                exit with exit code 0, otherwise 1
// 2022-11-18 added debug output from curl
// 2022-11-03 increased curl timeout and buffer size
// 2022-11-03 bugfix: set upper date limit to now (instead of 2022-03-31)
// 2021-08-15 skip stations with less than 10 data points
// 2021-04-11 added unique index prefix to filenames; used external
//            programm (curl) to fetch web data more reliably 
//            
// 2021-03-16 initial release
//
// ----------------------------------------------------------------------------

"use strict";
let child_process = require('child_process');
let fs = require("fs");

function https_get(url) {
    url = url.replace(/'/g, "%27");

    console.log("CURL: " + url);
    console.log("CURL: start download at " + (new Date()));
    let result = child_process.spawnSync("curl",
        ["--silent",
            "--compressed",
            "-w", "{CURL_STATUS_START_4925}status=%{http_code} size=%{size_download} conn=%{time_connect} ttfb=%{time_starttransfer} total=%{time_total}{CURL_STATUS_END_4925}\n",
            "-L",
            "-H", "Referer: el-parking-forecast",
            "-H", "Authorization: Bearer " + process.env.oauth_token,
            url],
        { "timeout": 600000, "maxBuffer": 2 * 1024 * 1024 * 1024 }
    );
    console.log("CURL: end   download at " + (new Date()));
    let stdout = String(result.output[1]);
    let stderr = String(result.output[2]);
    let match = stdout.match(/{CURL_STATUS_START_4925}(.+?){CURL_STATUS_END_4925}/);
    if (match) { // old curl doesn't support writing -w to stderr, so we need a workaround with regexp
        console.log("CURL: metrics: " + match[1]);
        stdout = stdout.replace(/(.+?){CURL_STATUS_START_4925}(.+?){CURL_STATUS_END_4925}(.+?)/s, '$1$3');
    } else {
        console.log("CURL: cannot regexp metrics (?)");
    }
    console.log("CURL: start first 200 chars of response");
    console.log(stdout.substring(0, 200) + "\n");
    console.log("CURL: end first 200 chars of response");
    return stdout;
}

let zeropad = num => {
    let str = String(num);
    while (str.length < 2) {
        str = "0" + str;
    }
    return str;
};

// ----------------------------------------------------------------------------
(function () {
    let stations_url = "https://mobility.api.opendatahub.com/v2/flat/ParkingStation/occupied/latest?limit=-1&distinct=true&where=sactive.eq.true&select=scode,sname,mvalidtime";
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

    let from_date = new Date("2022-01-01T00:00:00.000Z");
    let one_week_ago = new Date((new Date).getTime() - 7 * 24 * 60 * 60 * 1000);
    let ix = 0;
    let batch_interval = 60 * 24 * 60 * 60 * 1000; // 2 months

    stations.data.sort((a, b) => (a.scode < b.scode)).forEach(station => {
        let lines = [];
        let name = station.scode + "__" + String(station.sname).replace(/[.\s\/:]/g, "_") + ".csv";
        let to_date = new Date(new Date(station.mvalidtime).getTime() + 1000);

        // Skip if station has no up to date data, we can't predict on it anyway
        if (to_date < one_week_ago) {
          console.log("SKIP - " + name + " - last update more than 1 week old (" + station.mvalidtime + ")");
          return;
        }

        // Loop through 3-month batches
        let current_start = new Date(from_date);
        while (current_start < to_date) {
            let current_end = new Date(current_start.getTime() + batch_interval);
            if (current_end > to_date) {
                current_end = new Date(to_date);
            }

            let start_iso = current_start.toISOString();
            let end_iso = current_end.toISOString();
            let data_url = `https://mobility.api.opendatahub.com/v2/flat/ParkingStation/occupied/${start_iso}/${end_iso}?limit=-1&distinct=true&select=mvalue,mvalidtime,mperiod&where=and%28scode.eq.%22${station.scode}%22%2Csactive.eq.true%29`;

            let data;
            console.log("\n------");
            try {
                data = JSON.parse(https_get(data_url));
            } catch (ex) {
                console.log("KO - skip " + name + " as I cannot parse the JSON");
                process.exit(1);
            }
            if (data.data === undefined) {
                console.log("KO - skip " + name + " as the JSON misses the expected data field");
                return;
            }

            data.data.forEach(point => {
                lines.push(`"${point.mvalidtime}","${point.mvalue}"`);
            });

            // Move to next 3-month period
            current_start = new Date(current_end);
        }

        if (lines.length > 10) {
            let csv = zeropad(ix++) + "__" + name;
            console.log("OK (" + lines.length + " lines): " + csv);
            fs.writeFileSync("data-raw-candidate/" + csv, lines.sort().join("\n"));
        } else {
            console.log("KO - skip " + name + " with " + lines.length + " lines");
            return;
        }
    });

    if (ix >= 5) {
        console.log(ix + " stations saved, all good");
        process.exit(0);
    }
    console.log(ix + " stations saved. This is too few, I will return an error");
    process.exit(1);
})();