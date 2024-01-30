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
	"net/url"
	"os"
	"strconv"
	"strings"
	"traffic-a22-data-quality/bdplib"
)

const RequestTimeFormat = "2006-01-02T15:04:05.000-0700"

var BaseUrl = os.Getenv("ODH_NINJA_URL")
var referer = os.Getenv("NINJA_REFERER")

func ar2Path(ar []string) string {
	var ret string
	for i, s := range ar {
		ret += url.PathEscape(s)
		if i < len(ar)-1 {
			ret += ","
		}
	}
	return ret
}

func makeHistoryPath(req NinjaRequest) string {
	return fmt.Sprintf("/v2/%s/%s/%s/%s",
		ar2Path(req.StationTypes),
		ar2Path(req.DataTypes),
		req.From.Format(RequestTimeFormat),
		req.To.Format(RequestTimeFormat))
}

func makeQueryParam(name string, value any, defaultValue any) string {
	if value != defaultValue {
		return fmt.Sprintf("&name=%s", url.QueryEscape(fmt.Sprint(value)))
	}
	return ""
}

func makeQuery(req NinjaRequest) string {
	var query string
	query += makeQueryParam("origin", req.Origin, "")
	query += makeQueryParam("limit", req.Origin, 200)
	query += makeQueryParam("offset", req.Offset, 0)
	query += makeQueryParam("select", req.Select, "")
	query += makeQueryParam("where", req.Where, "")
	query += makeQueryParam("shownull", req.Shownull, false)
	query += makeQueryParam("distinct", req.Distinct, true)
	query += makeQueryParam("timezone", req.Timezone, "")

	return strings.Replace(query, "&", "?", 1) //make first one a question mark
}

func HistoryRequest[T any](req NinjaRequest, result *NinjaResponse[T]) error {
	var url = makeHistoryPath(req) + makeQuery(req)
	return GetRequest[T](url, result)
}

func GetRequest[T any](query string, result *NinjaResponse[T]) error {
	var fullUrl = BaseUrl + query
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
