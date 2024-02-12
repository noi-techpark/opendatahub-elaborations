// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package dc

import (
	"encoding/json"
	"regexp"
	"strings"
	"traffic-a22-data-quality/bdplib"

	"golang.org/x/exp/maps"
)

func combineJob() error {
	children, err := bdplib.GetStations(baseStationType, origin)
	if err != nil {
		return err
	}

	parents := combine(children)

	bdplib.SyncStations(parentStationType, parents, true, false)
	bdplib.SyncStations(baseStationType, children, false, false)

	return nil
}

func combine(children []bdplib.Station) []bdplib.Station {
	parents := make(map[string]bdplib.Station)
	for i, c := range children {
		pId := c.Id[0:strings.LastIndex(c.Id, ":")] + ":" + nameDirection(c.Name)
		p, ok := parents[pId]
		if !ok {
			name := nameWithoutLane(c.Name)

			p = bdplib.CreateStation(pId, name, parentStationType, c.Latitude, c.Longitude, c.Origin)
			// merge metadata
			p.MetaData = mergeMeta(p, c)

			parents[pId] = p
		}

		c.ParentStation = pId
		children[i] = c
	}
	return maps.Values(parents)
}

const a22metadata = "a22_metadata"

func mergeMeta(p, c bdplib.Station) map[string]any {
	ret := map[string]any{}

	metaStr, found := c.MetaData[a22metadata].(string)
	if !found {
		return ret
	}
	m := struct {
		Autostrada  string `json:"autostrada"`
		Iddirezione string `json:"iddirezione"`
		Idspira     string `json:"idspira"`
		Metro       string `json:"metro"`
	}{}

	err := json.Unmarshal([]byte(metaStr), &m)
	if err != nil {
		return ret
	}
	str, err := json.Marshal(m)
	if err != nil {
		return ret
	}
	ret[a22metadata] = string(str)

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
