// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>

// SPDX-License-Identifier: AGPL-3.0-or-later

package ninjalib

import (
	"encoding/json"
	"errors"
	"fmt"
	"io"
	"log/slog"
	"net/http"
	"os"
	"strconv"
	"traffic-a22-data-quality/bdplib"
)

var baseUrl = os.Getenv("ODH_NINJA_URL")
var referer = os.Getenv("NINJA_REFERER")

func GetRequest[T any](query string, result *NinjaResponse[T]) error {
	var fullUrl = baseUrl + query
	slog.Info("Ninja request with URL: " + fullUrl)

	req, err := http.NewRequest(http.MethodGet, fullUrl, nil)
	if err != nil {
		return fmt.Errorf("Unable to create Ninja HTTP Request: %w", err)
	}

	req.Header = http.Header{
		"Referer":       {referer},
		"Authorization": {"Bearer " + bdplib.GetToken()},
		"Accept":        {"application/json"},
	}

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		return fmt.Errorf("Error performing ninja request: %w", err)
	}

	if res.StatusCode != http.StatusOK {
		return errors.New("Ninja request returned non-OK status: " + strconv.Itoa(res.StatusCode))
	}

	bodyBytes, err := io.ReadAll(res.Body)
	if err != nil {
		return fmt.Errorf("Unable to read response body: %w", err)
	}

	err = json.Unmarshal(bodyBytes, result)
	if err != nil {
		return fmt.Errorf("Error unmarshalling response JSON to provided interface: %w", err)
	}

	return nil
}
