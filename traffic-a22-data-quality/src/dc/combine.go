// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package dc

import (
	"encoding/json"
	"regexp"
	"strings"

	"github.com/noi-techpark/go-bdp-client/bdplib"
	"golang.org/x/exp/maps"
)

func combineJob() error {
	children, err := bdp.GetStations(baseStationType, origin)
	if err != nil {
		return err
	}

	directions := combineDirections(children)
	locations := combineLocations(directions)

	bdp.SyncStations(locationStationType, locations, true, false)
	bdp.SyncStations(directionStationType, directions, true, false)
	bdp.SyncStations(baseStationType, children, false, false)

	return nil
}

func combineDirections(lanes []bdplib.Station) []bdplib.Station {
	dirs := make(map[string]bdplib.Station)
	for i, lane := range lanes {
		// make parent direction stations
		locId := lane.Id[0:strings.LastIndex(lane.Id, ":")]
		dId := locId + ":" + nameDirection(lane.Name)
		d, ok := dirs[dId]
		if !ok {
			name := nameWithoutLane(lane.Name)

			d = bdplib.CreateStation(dId, name, directionStationType, lane.Latitude, lane.Longitude, lane.Origin)
			// asign location as parent
			d.ParentStation = locId
			// merge metadata
			d.MetaData = makeDirectionMeta(lane)

			dirs[dId] = d
		}

		lane.ParentStation = dId
		lanes[i] = lane
	}
	return maps.Values(dirs)
}

func combineLocations(dirs []bdplib.Station) []bdplib.Station {
	type locAcc struct {
		latSum float64
		lonSum float64
		count  int
		name   string
		origin string
	}

	acc := make(map[string]*locAcc)

	for i, dir := range dirs {
		lId := dir.Id[0:strings.LastIndex(dir.Id, ":")]
		if a, ok := acc[lId]; !ok {
			acc[lId] = &locAcc{
				latSum: dir.Latitude,
				lonSum: dir.Longitude,
				count:  1,
				name:   dir.Name,
				origin: dir.Origin,
			}
		} else {
			a.latSum += dir.Latitude
			a.lonSum += dir.Longitude
			a.count++
			a.name = commonPrefix(a.name, dir.Name)
		}
		dirs[i].ParentStation = lId
	}

	locs := make([]bdplib.Station, 0, len(acc))
	for lId, a := range acc {
		lat := a.latSum / float64(a.count)
		lon := a.lonSum / float64(a.count)
		name := strings.TrimRight(a.name, " ")
		s := bdplib.CreateStation(lId, name, locationStationType, lat, lon, a.origin)
		locs = append(locs, s)
	}
	return locs
}

func commonPrefix(a, b string) string {
	i := 0
	for i < len(a) && i < len(b) && a[i] == b[i] {
		i++
	}
	return a[:i]
}

const a22metadata = "a22_metadata"

func makeDirectionMeta(c bdplib.Station) map[string]any {
	metaStr, found := c.MetaData[a22metadata].(string)
	if !found {
		return nil
	}
	m := struct {
		Autostrada  string `json:"autostrada"`
		Iddirezione string `json:"iddirezione"`
		Idspira     string `json:"idspira"`
		Metro       string `json:"metro"`
	}{}

	err := json.Unmarshal([]byte(metaStr), &m)
	if err != nil {
		return nil
	}

	ret := map[string]any{}
	ret[a22metadata] = m

	return ret
}

var reName = regexp.MustCompile(`\(corsia di (\w|\s)+, `)

func nameWithoutLane(n string) string {
	return reName.ReplaceAllString(n, "(")
}

var reDirection = regexp.MustCompile(`direzione (\w+)\)`)

func nameDirection(n string) string {
	return reDirection.FindStringSubmatch(n)[1]
}
