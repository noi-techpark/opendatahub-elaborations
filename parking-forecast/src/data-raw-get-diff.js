#!/usr/bin/env node

// SPDX-FileCopyrightText: 2021-2025 STA AG <info@sta.bz.it>
// SPDX-FileContributor: Chris Mair <chris@1006.org>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

// ----------------------------------------------------------------------------
//
// Parking occupancy prediction
// data-raw-get-diff.js
//
// (C) 2021-2023 STA AG
//
// Consider the data already fetched in data-raw/.
// For each station (file) fetch the missing data between the latest
// timestamp already present in the file and the current timestamp.
// Add this data to the file.
//
// author: Chris Mair - chris@1006.org
//
// changelog:
// 2023-01-11 order data by timestamp (as ODH sometimes returns unordered data)
// 2022-11-03 increased curl timeout and buffer size
// 2021-12-20 initial release
//
// ----------------------------------------------------------------------------

"use strict";
let child_process = require('child_process');
let fs = require("fs");

function https_get(url) {
    url = url.replace(/'/g, "%27");
    return String(child_process.spawnSync("curl", 
        ["-L",
         "-H", "Referer: el-parking-forecast",
         "-H", "Authorization: Bearer " + process.env.oauth_token,
        , url], {"timeout": 600000, "maxBuffer": 2*1024*1024*1024}).output[1]);
}

function min_date(a, b) {
    return (a.getTime() < b.getTime()) ? a : b;
}


// ----------------------------------------------------------------------------
(function() {


    // --- get the list of files ---

    const DIR = "data-raw/";
    let filenames = fs.readdirSync(DIR);
    filenames = filenames.filter( fn => fn.endsWith(".csv"));

    // --- prepare list of stations: filename (String), scode (String), last_ts (Date) ---

    let stations = [];
    filenames.forEach( fn => {
        let parts = fn.split("__");
        if (parts.length < 3) {
            console.error(`fatal: invalid filename ${fn}`);
            process.exit(1);
        }
        let lines = fs.readFileSync(DIR + fn, "utf8").split("\n");

        let last_line = lines[lines.length - 1];
        if (last_line === undefined) {
            console.error(`warning: no line in file ${fn} - skipped`);
            return;
        }
        let match = last_line.match(/"\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d.\d+\+\d+"/);
        if (!match) {
            console.error(`warning: no timestamp in last line of file ${fn} - skipped`);
            return;
        }
        let last_ts = new Date(match[0]);
        if (isNaN(last_ts)) {
            console.error(`warning: invalid timestamp in last line of file ${fn} - skipped`);
            return;
        }
        stations.push({ filename: fn, scode: parts[1], last_ts: last_ts });
    });


    // --- now ---
    const NOW = new Date();

    // --- for each station fetch the new data and append it to the file ---

    stations.forEach( station => {

        let from_date = station.last_ts;
        from_date.setSeconds(from_date.getSeconds() + 1); // add 1 second (will correctly overflow)

        // we compute min(NOW, from_date + 60 days) as the upper bound so not to exceed this range
        let to_date = new Date(from_date);
        to_date.setSeconds(to_date.getSeconds() + 86400 * 60); // add 60 days (will correctly overflow)
        to_date = min_date(NOW, to_date);

        // debug print
        // console.log(station.scode + " " + from_date.toISOString() + " " + to_date.toISOString());

        let data_url = `https://mobility.api.opendatahub.com/v2/flat/ParkingStation/occupied/${from_date.toISOString()}/${to_date.toISOString()}?limit=-1&distinct=true&select=mvalue,mvalidtime,mperiod&where=and%28scode.eq.%22${station.scode}%22%2Csactive.eq.true%29`
        let data;
        try {
            data = JSON.parse(https_get(data_url));
        } catch (ex) {
            console.error(`warning: fetching data failed for ${data_url} (JSON parse error) - skipped`);
            return;
        }
        if (data.data == undefined) {
            console.error(`warning: fetching data failed for ${data_url} (no field 'data') - skipped`);
            // console.log(data);
            return;
        }
        let lines = [];
        data.data.forEach( point => {
            //  interesting point fields:
            //     mperiod: 300,
            //     mvalidtime: '2021-03-10 08:20:00.358+0000',
            //     mvalue: 484
            //
            lines.push(`"${point.mvalidtime}","${point.mvalue}"`);
        });

        if (lines.length === 0) {
            console.error(`warning: no new data for ${data_url} - skipped`);
            return;
        }

        fs.appendFileSync(DIR + station.filename, "\n" + lines.sort().join("\n"));

        console.log(station.filename);
        console.log("    " + station.scode);
        console.log("    " + station.last_ts);
        console.log("    append " + (lines.length) + " data points");

    });

})();
