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

	parents := combine(children)

	bdp.SyncStations(parentStationType, parents, true, false)
	bdp.SyncStations(baseStationType, children, false, false)

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
			p.MetaData = makeMetaData(c)

			parents[pId] = p
		}

		c.ParentStation = pId
		children[i] = c
	}
	return maps.Values(parents)
}

const a22metadata = "a22_metadata"

func makeMetaData(c bdplib.Station) map[string]any {
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
