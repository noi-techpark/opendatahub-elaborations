// SPDX-FileCopyrightText: 2026 NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package forest

import (
	"bytes"
	"encoding/gob"
	"fmt"
)

// Marshal serializes a forest to a compact binary blob for storage in
// store.SaveModel.
func Marshal(f *Forest) ([]byte, error) {
	var buf bytes.Buffer
	if err := gob.NewEncoder(&buf).Encode(f); err != nil {
		return nil, fmt.Errorf("encoding forest: %w", err)
	}
	return buf.Bytes(), nil
}

func Unmarshal(blob []byte) (*Forest, error) {
	var f Forest
	if err := gob.NewDecoder(bytes.NewReader(blob)).Decode(&f); err != nil {
		return nil, fmt.Errorf("decoding forest: %w", err)
	}
	return &f, nil
}
