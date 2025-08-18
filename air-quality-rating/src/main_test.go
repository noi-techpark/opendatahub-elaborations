// SPDX-FileCopyrightText: 2025 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package main

import (
	"encoding/json"
	"fmt"
	"os"
	"testing"

	"github.com/noi-techpark/go-timeseries-client/odhts"
	"gotest.tools/v3/assert"
)

func TestElaboration_GetInitialState(t *testing.T) {
	// Read the file contents
	byteValue, err := os.ReadFile("./testdata/echargingtree.json")
	assert.NilError(t, err, "cant read file")

	var o odhts.Response[DtoTreeData]
	err = json.Unmarshal(byteValue, &o)
	assert.NilError(t, err, "cant unmarshal json")
	et := mapNinja2ElabTree(o)

	bt, err := json.Marshal(et)
	assert.NilError(t, err, "cant marshal json")
	fmt.Printf("%s", string(bt))
}
