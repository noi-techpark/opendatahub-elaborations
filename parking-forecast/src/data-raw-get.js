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
        {"timeout": 600000, "maxBuffer": 2*1024*1024*1024}
    );
    console.log("CURL: end   download at " + (new Date()));
    let stdout = String(result.output[1]);
    let stderr = String(result.output[2]);
    let match = stdout.match(/{CURL_STATUS_START_4925}(.+?){CURL_STATUS_END_4925}/);
    if (match) { // old curl doesn't support writing -w to stderr, so we need a workaround with regexp
        console.log("CURL: metrics: " + match[1]);
        stdout = stdout.replace(/(.+?){CURL_STATUS_START_4925}(.+?){CURL_STATUS_END_4925}(.+?)/s,'$1$3');
    } else {
        console.log("CURL: cannot regexp metrics (?)");
    }
    console.log("CURL: start first 200 chars of response");
    console.log(stdout.substring(0,200) + "\n");
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
(function() {

    let stations_url = "https://mobility.api.opendatahub.com/v2/flat/ParkingStation/occupied/latest?limit=-1&distinct=true&where=sactive.eq.true&select=scode,sname";
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

    let from_date = "2022-01-01T00:00:00.000Z";
    let to_date   = (new Date()).toISOString();

    let ix = 0;
    stations.data.sort( (a, b) => (a.scode < b.scode)).forEach( station => {
        /* interesting station fields:
             scode: '103',
             scoordinate: [Object],
             smetadata: [Object],
             sname: 'P03 - Piazza Walther',
             sorigin: 'FAMAS',
             stype: 'ParkingStation'
         */

        let limit = 50000
        let lines = [];
        let name = station.scode + "__" + String(station.sname).replace(/[.\s\/:]/g, "_") + ".csv";

        // loop for paging, or we risk bombing the API
        while(true){
            let offset = lines.length
            let data_url = `https://mobility.api.opendatahub.com/v2/flat/ParkingStation/occupied/${from_date}/${to_date}?limit=${limit}&offset=${offset}&distinct=true&select=mvalue,mvalidtime,mperiod&where=and%28scode.eq.%22${station.scode}%22%2Csactive.eq.true%29`
            let data;
            console.log("\n------");
            try {
                data = JSON.parse(https_get(data_url));
            } catch (ex) {
                console.log("KO - skip " + name + " as I cannot parse the JSON");
                // likely some form of API error
                process.exit(1);
            }
            if (data.data === undefined) {
                console.log("KO - skip " + name + " as the JSON misses the expected data field");
                return;
            }

            data.data.forEach( point => {
                /* interesting point fields:
                    mperiod: 300,
                    mvalidtime: '2021-03-10 08:20:00.358+0000',
                    mvalue: 484
                 */
                lines.push(`"${point.mvalidtime}","${point.mvalue}"`);
            });

            if (data.data.length < limit) {
                break;
            }
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
