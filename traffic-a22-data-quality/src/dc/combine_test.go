// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package dc

import (
	"reflect"
	"testing"

	"github.com/noi-techpark/go-bdp-client/bdplib"
)

func TestMangleName(t *testing.T) {
	r := "SEZIONE DI RILEVAMENTO KM. 228+200 (direzione sud)"

	if nameWithoutLane(s1872_3.Name) != r {
		t.Fail()
	}
}
func TestDirection(t *testing.T) {
	if nameDirection(s1871_1.Name) != "nord" || nameDirection(s1872_3.Name) != "sud" {
		t.Fail()
	}
}

var s1871_sud = bdplib.CreateStation("A22:1871:sud", "SEZIONE DI RILEVAMENTO KM. 227+600 (direzione sud)", "TrafficDirection", 10.913511, 45.410031, "A22")
var s1871_loc = bdplib.CreateStation("A22:1871", "SEZIONE DI RILEVAMENTO KM. 227+600 (direzione", "TrafficLocation", 10.913511, 45.410031, "A22")

var s1871_1 = bdplib.CreateStation("A22:1871:1", "SEZIONE DI RILEVAMENTO KM. 227+600 (corsia di marcia nord, direzione nord)", "TrafficSensor", 10.913511, 45.410031, "A22")
var s1871_2 = bdplib.CreateStation("A22:1871:2", "SEZIONE DI RILEVAMENTO KM. 227+600 (corsia di sorpasso nord, direzione nord)", "TrafficSensor", 10.913511, 45.410031, "A22")
var s1872_3 = bdplib.CreateStation("A22:1872:3", "SEZIONE DI RILEVAMENTO KM. 228+200 (corsia di marcia sud, direzione sud)", "TrafficSensor", 10.912266, 45.406126, "A22")
var s1872_4 = bdplib.CreateStation("A22:1872:4", "SEZIONE DI RILEVAMENTO KM. 228+200 (corsia di sorpasso sud, direzione sud)", "TrafficSensor", 10.912266, 45.406126, "A22")
var s1871_nord = bdplib.CreateStation("A22:1871:nord", "SEZIONE DI RILEVAMENTO KM. 227+600 (direzione nord)", "TrafficDirection", 10.913511, 45.410031, "A22")
var s1872_sud = bdplib.CreateStation("A22:1872:sud", "SEZIONE DI RILEVAMENTO KM. 228+200 (direzione sud)", "TrafficDirection", 10.912266, 45.406126, "A22")

func TestCombineLocations(t *testing.T) {
	locationStationType = "TrafficLocation"
	r := combineLocations([]bdplib.Station{s1871_nord, s1871_sud})
	if len(r) != 1 {
		t.Fatal("Expected 1 location station, got", len(r))
	}
	if !reflect.DeepEqual(r[0], s1871_loc) {
		t.Error("Location station not equal: ", r[0], s1871_loc)
	}
}

func TestCombine(t *testing.T) {
	directionStationType = "TrafficDirection"
	r := combineDirections([]bdplib.Station{s1871_1, s1871_2})
	if !reflect.DeepEqual(r[0], s1871_nord) {
		t.Error("Combined station not equal: ", r[0], s1871_nord)
	}
	r = combineDirections([]bdplib.Station{s1872_3, s1872_4})
	if !reflect.DeepEqual(r[0], s1872_sud) {
		t.Error("Combined station not equal: ", r[0], s1872_sud)
	}
}
