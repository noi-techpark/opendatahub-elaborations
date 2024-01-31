// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package dc

import (
	"encoding/json"
	"fmt"
	"log/slog"
	"os"
	"time"
	"traffic-a22-data-quality/ninjalib"
)

var origin string = os.Getenv("ORIGIN")

var queryLatest = os.Getenv("NINJA_QUERY_LATEST")

const periodBase = 600
const periodAggregate = 86400

type NinjaMeasurement struct {
	Period    int64              `json:"mperiod"`
	Timestamp ninjalib.NinjaTime `json:"mvalidtime"`
}

type NinjaTreeData = map[string]struct { // key = stationtype
	Stations map[string]struct { // key = stationcode
		Datatypes map[string]struct { // key = datatype
			Measurements []NinjaMeasurement `json:"tmeasurements"`
		} `json:"sdatatypes"`
	} `json:"stations"`
}

type NinjaFlatData = []struct {
	StationCode string             `json:"scode"`
	TypeName    string             `json:"tname"`
	Timestamp   ninjalib.NinjaTime `json:"_timestamp"`
}

func Job() {
	sumJob()
	combineJob()
	sumUpJob()
}

func debugLogJson(j any) {
	s, _ := json.MarshalIndent(j, "", " ")
	fmt.Println(string(s))
}

func sumJob() {
	// ninja: get all the TrafficSensor stations with latest 3 datapoints, both period 10min and 1day
	var res ninjalib.NinjaResponse[NinjaTreeData]
	err := ninjalib.GetRequest(queryLatest, &res)
	if err != nil {
		slog.Error("error", err)
		return
	}

	type todoStation struct {
		lastBase      time.Time
		lastAggregate time.Time
	}

	var todos = make(map[string]map[string]todoStation)

	for _, stations := range res.Data {
		for stationCode, station := range stations.Stations {
			for typeName, dataType := range station.Datatypes {
				for _, m := range dataType.Measurements {
					var lastBase time.Time
					var lastAggregate time.Time
					if m.Period == periodBase {
						lastBase = m.Timestamp.Time
					}
					if m.Period == periodAggregate {
						lastAggregate = m.Timestamp.Time
					}

					// Determine which stations we have to make history requests for
					if lastBase.Sub(lastAggregate).Seconds() > periodAggregate {
						if todos[stationCode] == nil {
							todos[stationCode] = make(map[string]todoStation)
						}
						todos[stationCode][typeName] = todoStation{
							lastBase:      lastBase,
							lastAggregate: lastAggregate,
						}
					}
				}
			}
		}
	}

	stripToDay := func(t time.Time) time.Time {
		return time.Date(t.Year(), t.Month(), t.Day(), 0, 0, 0, 0, t.Location())
	}

	// 	get data history from starting point until last EOD
	for stationCode, typeMap := range todos {
		for typeName, todo := range typeMap {
			// for every n months
			// start with day lastAggregate = +1 until EOD lastBase
			start := stripToDay(todo.lastAggregate).AddDate(0, 0, 1)
			end := stripToDay(todo.lastBase)

			for start.Compare(end) < 0 {
				// request end = start + 3 months
				res, err := getNinjaData(stationCode, typeName, start, end)
				if err != nil {
					slog.Error("Error requesting data from Ninja", err)
					return
				}
				debugLogJson(res)

			}
		}
	}
	// 	for each calendar day:
	// 		check for data completeness, e.g. every 10 minutes of the day is covered, else do Idontknowwhat
	// 		sum up all the 10 minute periods
	// 		create combined sum measurement
}

func getNinjaData(stationCode string, typeName string, from time.Time, to time.Time) (*ninjalib.NinjaResponse[NinjaFlatData], error) {
	req := ninjalib.DefaultNinjaRequest()
	req.AddDataType(typeName)
	req.From = from
	req.To = to
	req.Select = "scode,mvalue,tname"
	req.Where = fmt.Sprintf("and(mperiod.eq.%d,scode.eq.\"%s\")", periodBase, stationCode)
	req.Limit = -1

	var res *ninjalib.NinjaResponse[NinjaFlatData]

	err := ninjalib.HistoryRequest(req, res)
	return res, err
}

func combineJob() {
	/*
		get all TrafficSensors that don't have a parent station already
		match them by gps point or metadata and determine groupings
		create missing parent stations
	*/
}

func sumUpJob() {
	/*
		get all stations that have a parent, and their most recent 1day data
		get the parent's most recent data point
		for all parents where data point is older than children data;
			get history of children with start = most recent parent date
			build children sum
			push to parent
	*/
}

// func Job() {
// 	var parentStations []bdplib.Station
// 	// save stations by stationCode
// 	stations := make(map[string]bdplib.Station)

// 	var dataMapParent bdplib.DataMap
// 	var dataMap bdplib.DataMap

// 	facilities := GetFacilityData()

// 	ts := time.Now().UnixMilli()

// 	for _, facility := range facilities.Data.Facilities {

// 		if facility.ReceiptMerchant == identifier {
// 			parentStationCode := strconv.Itoa(facility.FacilityId)

// 			parentStation := bdplib.CreateStation(parentStationCode, facility.Description, stationTypeParent, bzLat, bzLon, origin)
// 			parentStation.MetaData = map[string]interface{}{
// 				"IdCompany":  facility.FacilityId,
// 				"City":       facility.City,
// 				"Address":    facility.Address,
// 				"ZIPCode":    facility.ZIPCode,
// 				"Telephone1": facility.Telephone1,
// 				"Telephone2": facility.Telephone2,
// 			}
// 			parentStations = append(parentStations, parentStation)

// 			freePlaces := GetFreePlacesData(facility.FacilityId)

// 			// total facility measurements
// 			freeTotalSum := 0
// 			occupiedTotalSum := 0
// 			capacityTotal := 0

// 			// freeplaces is array of a single categories data
// 			// if multiple parkNo exist, multiple entries for every parkNo and its categories exist
// 			// so iterating over freeplaces and checking if the station with the parkNo has already been created is needed
// 			for _, freePlace := range freePlaces.Data.FreePlaces {
// 				// create ParkingStation
// 				stationCode := parentStationCode + "_" + strconv.Itoa(freePlace.ParkNo)
// 				station, ok := stations[stationCode]
// 				if !ok {
// 					station = bdplib.CreateStation(stationCode, facility.Description, stationType, bzLat, bzLon, origin)
// 					station.ParentStation = parentStation.Id
// 					station.MetaData = make(map[string]interface{})
// 					stations[stationCode] = station
// 					slog.Debug("Create station " + stationCode)
// 				}

// 				switch freePlace.CountingCategoryNo {
// 				// Short Stay
// 				case 1:
// 					station.MetaData["free_limit_"+shortStay] = freePlace.FreeLimit
// 					station.MetaData["occupancy_limit_"+shortStay] = freePlace.OccupancyLimit
// 					station.MetaData["capacity_"+shortStay] = freePlace.Capacity
// 					bdplib.AddRecord(stationCode, dataTypeFreeShort, bdplib.CreateRecord(ts, freePlace.FreePlaces, 600), &dataMap)
// 					bdplib.AddRecord(stationCode, dataTypeOccupiedShort, bdplib.CreateRecord(ts, freePlace.CurrentLevel, 600), &dataMap)
// 				// Subscribed
// 				case 2:
// 					station.MetaData["free_limit_"+Subscribers] = freePlace.FreeLimit
// 					station.MetaData["occupancy_limit_"+Subscribers] = freePlace.OccupancyLimit
// 					station.MetaData["capacity_"+Subscribers] = freePlace.Capacity
// 					bdplib.AddRecord(stationCode, dataTypeFreeSubs, bdplib.CreateRecord(ts, freePlace.FreePlaces, 600), &dataMap)
// 					bdplib.AddRecord(stationCode, dataTypeOccupiedSubs, bdplib.CreateRecord(ts, freePlace.CurrentLevel, 600), &dataMap)
// 				// Total
// 				default:
// 					station.MetaData["free_limit"] = freePlace.FreeLimit
// 					station.MetaData["occupancy_limit"] = freePlace.OccupancyLimit
// 					station.MetaData["Capacity"] = freePlace.Capacity
// 					bdplib.AddRecord(stationCode, dataTypeFreeTotal, bdplib.CreateRecord(ts, freePlace.FreePlaces, 600), &dataMap)
// 					bdplib.AddRecord(stationCode, dataTypeOccupiedTotal, bdplib.CreateRecord(ts, freePlace.CurrentLevel, 600), &dataMap)
// 					// total facility data
// 					freeTotalSum += freePlace.FreePlaces
// 					occupiedTotalSum += freePlace.CurrentLevel
// 					capacityTotal += freePlace.Capacity
// 				}
// 			}
// 			// assign total facility data, if data is not 0
// 			if freeTotalSum > 0 {
// 				bdplib.AddRecord(parentStationCode, dataTypeFreeTotal, bdplib.CreateRecord(ts, freeTotalSum, 600), &dataMapParent)
// 			}
// 			if occupiedTotalSum > 0 {
// 				bdplib.AddRecord(parentStationCode, dataTypeOccupiedTotal, bdplib.CreateRecord(ts, occupiedTotalSum, 600), &dataMapParent)
// 			}
// 			if capacityTotal > 0 {
// 				parentStation.MetaData["Capacity"] = capacityTotal
// 			}
// 		}
// 	}
// 	bdplib.SyncStations(stationTypeParent, parentStations)
// 	bdplib.SyncStations(stationType, values(stations))
// 	bdplib.PushData(stationTypeParent, dataMapParent)
// 	bdplib.PushData(stationType, dataMap)
// }

// // to extract values array from map, without external dependency
// // https://stackoverflow.com/questions/13422578/in-go-how-to-get-a-slice-of-values-from-a-map
// func values[M ~map[K]V, K comparable, V any](m M) []V {
// 	r := make([]V, 0, len(m))
// 	for _, v := range m {
// 		r = append(r, v)
// 	}
// 	return r
// }
