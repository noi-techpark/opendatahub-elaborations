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

	bdplib.SyncStations(parentStationType, parents)
	bdplib.SyncStations(stationType, children)

	return nil
}

func combine(children []bdplib.Station) []bdplib.Station {
	parents := make(map[string]bdplib.Station)
	for _, c := range children {
		pId := c.Id[0:strings.LastIndex(c.Id, ":")] + ":" + getDirection(c.Name)
		p, ok := parents[pId]
		if !ok {
			name := mangleName(c.Name)

			p = bdplib.CreateStation(pId, name, parentStationType, c.Latitude, c.Longitude, c.Origin)
			// merge metadata

			parents[pId] = p
		}

		c.ParentStation = p.Id
	}
	return maps.Values(parents)
}

var reName = regexp.MustCompile(`\(corsia di (\w|\s)+, `)

func mangleName(n string) string {
	// remove lane string from name, since we are aggregating all lanes of the same direction
	return reName.ReplaceAllString(n, "(")
}

var reDirection = regexp.MustCompile(`direzione (\w+)\)`)

func getDirection(n string) string {
	return reDirection.FindStringSubmatch(n)[1]
}
