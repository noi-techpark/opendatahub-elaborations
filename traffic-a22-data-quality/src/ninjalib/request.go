// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package ninjalib

import "time"

type Repr string

const (
	FlatNode  Repr = "flat,node"
	TreeNode  Repr = "tree,node"
	FlatEdge  Repr = "flat,edge"
	TreeEdge  Repr = "tree,edge"
	FlatEvent Repr = "flat,event"
	TreeEvent Repr = "tree,event"
)

type NinjaRequest struct {
	Repr     Repr `default:"FlatNode"`
	Origin   string
	Limit    int64  `default:"200"`
	Offset   uint64 `default:"0"`
	Select   string
	Where    string
	Shownull bool `default:"false"`
	Distinct bool `default:"true"`
	Timezone string

	EventOrigins []string `default:"[]string{*}"`
	EdgeTypes    []string `default:"[]string{*}"`

	Timepoint time.Time

	StationTypes []string `default:"[]string{*}"`
	DataTypes    []string `default:"[]string{*}"`

	From time.Time
	To   time.Time
}

func (nr NinjaRequest) AddStationType(stationType string) {
	nr.StationTypes = append(nr.StationTypes, stationType)
}
func (nr NinjaRequest) AddDataType(dataType string) {
	nr.DataTypes = append(nr.DataTypes, dataType)
}
func (nr NinjaRequest) AddEdgeType(edgeType string) {
	nr.EdgeTypes = append(nr.EdgeTypes, edgeType)
}
func (nr NinjaRequest) AddEventOrigin(eventOrigin string) {
	nr.EventOrigins = append(nr.EventOrigins, eventOrigin)
}
