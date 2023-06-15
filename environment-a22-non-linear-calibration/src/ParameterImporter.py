# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

import csv
import json

def getParameters():
    f = open('processorParameters.csv',)
    data = csv.reader(f, delimiter=',')
    data_map = {}
    type_mapping = {
        "8":"O3",
        "12":"PM10",
        "13":"PM2.5",
        "14":"NO2-Alphasense",
        "15":"NO-Alphasense"
    }
    next(data, None)
    for row in data:
        station_id = 'AUGEG4_' + row[0]
        type_id =type_mapping[row[1]]
        type_map = data_map.get(station_id,{})
        temp_map = type_map.get(type_id,{})
        parameter_map = {
            "a": row[5],
            "b": row[6],
            "c": row[7],
            "d": row[8],
            "e": row[9],
            "f": row[10],
            "calc_version": row[11]
        }
        if len(str(row[2])) == 0:
            temp_map['lowtemp']= parameter_map
        else:
            temp_map['hightemp']= parameter_map
        type_map[type_id] = temp_map
        data_map[station_id] = type_map
    return data_map
