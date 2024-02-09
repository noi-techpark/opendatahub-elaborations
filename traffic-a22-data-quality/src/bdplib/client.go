// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package bdplib

import (
	"bytes"
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"os"
	"strconv"
)

type Provenance struct {
	Lineage              string `json:"lineage"`
	DataCollector        string `json:"dataCollector"`
	DataCollectorVersion string `json:"dataCollectorVersion"`
}

type DataType struct {
	Name        string            `json:"name"`
	Unit        string            `json:"unit"`
	Description string            `json:"description"`
	Rtype       string            `json:"rType"`
	Period      uint32            `json:"period"`
	MetaData    map[string]string `json:"metaData"`
}

type Station struct {
	Id            string                 `json:"id"`
	Name          string                 `json:"name"`
	StationType   string                 `json:"stationType,omitempty"` // when syncing, this needs to be null, blank string fails
	Latitude      float64                `json:"latitude"`
	Longitude     float64                `json:"longitude"`
	Origin        string                 `json:"origin"`
	ParentStation string                 `json:"parentStation,omitempty"`
	MetaData      map[string]interface{} `json:"metaData"`
}

type DataMap struct {
	Name       string             `json:"name"`
	Data       []Record           `json:"data"`
	Branch     map[string]DataMap `json:"branch"`
	Provenance string             `json:"provenance"`
}

type Record struct {
	Value     interface{} `json:"value"`
	Period    uint64      `json:"period"`
	Timestamp int64       `json:"timestamp"`
}

const syncDataTypesPath string = "/syncDataTypes"
const syncStationsPath string = "/syncStations"
const pushRecordsPath string = "/pushRecords"
const getDateOfLastRecordPath string = "/getDateOfLastRecord"
const stationsPath string = "/stations"
const provenancePath string = "/provenance"

var provenanceUuid string

var BaseUrl string = os.Getenv("BDP_BASE_URL") + "/json"

var Prv string = os.Getenv("BDP_PROVENANCE_VERSION")
var Prn string = os.Getenv("BDP_PROVENANCE_NAME")

var Origin string = os.Getenv("BDP_ORIGIN")

func SyncDataTypes(stationType string, dataTypes []DataType) {
	pushProvenance()

	slog.Debug("Syncing data types...")

	url := BaseUrl + syncDataTypesPath + "?stationType=" + stationType + "&prn=" + Prn + "&prv=" + Prv

	postToWriter(dataTypes, url)

	slog.Debug("Syncing data types done.")
}

func SyncStations(stationType string, stations []Station, syncState bool, onlyActivate bool) {
	pushProvenance()

	slog.Info("Syncing " + strconv.Itoa(len(stations)) + " " + stationType + " stations...")
	url := BaseUrl + syncStationsPath + "/" + stationType + "?prn=" + Prn + "&prv=" + Prv + "&syncState=" + strconv.FormatBool(syncState) + "&onlyActivation=" + strconv.FormatBool(onlyActivate)
	postToWriter(stations, url)
	slog.Info("Syncing stations done.")
}

func PushData(stationType string, dataMap DataMap) {
	pushProvenance()
	if dataMap.Provenance == "" {
		dataMap.Provenance = provenanceUuid
	}

	slog.Info("Pushing records...")
	url := BaseUrl + pushRecordsPath + "/" + stationType + "?prn=" + Prn + "&prv=" + Prv
	postToWriter(dataMap, url)
	slog.Info("Pushing records done.")
}

func CreateDataType(name string, unit string, description string, rtype string) DataType {
	// TODO add some checks
	return DataType{
		Name:        name,
		Unit:        unit,
		Description: description,
		Rtype:       rtype,
	}
}

func CreateStation(id string, name string, stationType string, lat float64, lon float64, origin string) Station {
	// TODO add some checks
	var station = Station{
		Name:        name,
		StationType: stationType,
		Latitude:    lat,
		Longitude:   lon,
		Origin:      origin,
		Id:          id,
	}
	return station
}

func CreateRecord(ts int64, value interface{}, period uint64) Record {
	// TODO add some checks
	record := Record{
		Value:     value,
		Timestamp: ts,
		Period:    period,
	}
	return record
}

func createDataMap() DataMap {
	var dataMap = DataMap{
		Name:       "(default)",
		Provenance: provenanceUuid,
		Branch:     make(map[string]DataMap),
	}
	return dataMap
}

// add an array of record to dataMap
func (dataMap *DataMap) AddRecords(stationCode string, dataType string, records []Record) {
	for _, record := range records {
		dataMap.AddRecord(stationCode, dataType, record)
	}
}

// add one single record to dataMap
func (dataMap *DataMap) AddRecord(stationCode string, dataType string, record Record) {
	if dataMap.Name == "" {
		*dataMap = createDataMap()
	}

	if dataMap.Branch[stationCode].Name == "" {
		dataMap.Branch[stationCode] = DataMap{
			Name:   "(default)",
			Branch: make(map[string]DataMap),
		}
		slog.Debug("new station in branch " + stationCode)
	}

	if dataMap.Branch[stationCode].Branch[dataType].Name == "" {
		dataMap.Branch[stationCode].Branch[dataType] = DataMap{
			Name: "(default)",
			Data: []Record{record},
		}
		// to assign a value to a struct in a map, this code part is needed
		// https://stackoverflow.com/a/69006398/8794667
	} else if entry, ok := dataMap.Branch[stationCode].Branch[dataType]; ok {
		entry.Data = append(entry.Data, record)
		dataMap.Branch[stationCode].Branch[dataType] = entry
	}
}

func postToWriter(data interface{}, fullUrl string) (string, error) {
	json, err := json.Marshal(data)
	if err != nil {
		slog.Error("Error unmarshalling JSON POST data")
		return "", err
	}

	client := http.Client{}
	req, err := http.NewRequest("POST", fullUrl, bytes.NewBuffer(json))
	if err != nil {
		slog.Error("Error creating http POST request")
		return "", err
	}

	req.Header = http.Header{
		"Content-Type":  {"application/json"},
		"Authorization": {"Bearer " + GetToken()},
	}

	res, err := client.Do(req)
	if err != nil {
		slog.Error("Error performing POST")
		return "", err
	}

	resb, err := io.ReadAll(res.Body)
	if err != nil {
		slog.Error("Error reading from Response body")
		return "", err
	}
	ress := string(resb)

	if res.StatusCode != http.StatusOK && res.StatusCode != http.StatusCreated {
		slog.Error("bdp POST returned with error", "statusCode", strconv.Itoa(res.StatusCode), "body", ress)
		return "", errors.New("bdp POST returned non-OK status: " + strconv.Itoa(res.StatusCode))
	}

	return ress, nil
}

func pushProvenance() {
	if len(provenanceUuid) > 0 {
		return
	}

	slog.Info("Pushing provenance...")
	slog.Info("prv: " + Prv + " prn: " + Prn)

	var provenance = Provenance{
		DataCollector:        Prn,
		DataCollectorVersion: Prv,
		Lineage:              Origin,
	}

	url := BaseUrl + provenancePath + "?&prn=" + Prn + "&prv=" + Prv

	res, err := postToWriter(provenance, url)

	if err != nil {
		slog.Error("error", "err", err)
	}

	provenanceUuid = res

	slog.Info("Pushing provenance done", "uuid", provenanceUuid)
}

func GetStations(stationType string, origin string) ([]Station, error) {
	slog.Debug("Fetching stations", "stationType", stationType, "origin", origin)

	url := BaseUrl + stationsPath + fmt.Sprintf("/%s/?origin=%s&prn=%s&prv=%s", stationType, origin, Prn, Prv)
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		return nil, fmt.Errorf("unable to create BDP HTTP Request: %w", err)
	}

	req.Header = http.Header{
		"Content-Type":  {"application/json"},
		"Authorization": {"Bearer " + GetToken()},
	}

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("error performing ninja request: %w", err)
	}

	if res.StatusCode != http.StatusOK {
		return nil, errors.New("ninja request returned non-OK status: " + strconv.Itoa(res.StatusCode))
	}

	bodyBytes, err := io.ReadAll(res.Body)
	if err != nil {
		return nil, fmt.Errorf("unable to read response body: %w", err)
	}

	result := []Station{}
	err = json.Unmarshal(bodyBytes, &result)
	if err != nil {
		return nil, fmt.Errorf("error unmarshalling response JSON to provided interface: %w", err)
	}

	// For some reason when getting stations by type, the field is not set
	for i := range result {
		result[i].StationType = stationType
	}

	return result, nil
}
