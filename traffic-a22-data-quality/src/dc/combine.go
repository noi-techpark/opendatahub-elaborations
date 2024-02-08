// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package dc

import (
	"regexp"
	"strings"
	"traffic-a22-data-quality/bdplib"

	"golang.org/x/exp/maps"
)

func combineJob() error {
	children, err := bdplib.GetStations(stationType, "A22")
	if err != nil {
		return err
	}

	parents := combine(children)

	bdplib.SyncStations(parentStationType, parents, true, false)
	bdplib.SyncStations(stationType, children, false, false)

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

			parents[pId] = p
		}

		c.ParentStation = pId
		children[i] = c
	}
	return maps.Values(parents)
}

var reName = regexp.MustCompile(`\(corsia di (\w|\s)+, `)

func nameWithoutLane(n string) string {
	return reName.ReplaceAllString(n, "(")
}

var reDirection = regexp.MustCompile(`direzione (\w+)\)`)

func nameDirection(n string) string {
	return reDirection.FindStringSubmatch(n)[1]
}
