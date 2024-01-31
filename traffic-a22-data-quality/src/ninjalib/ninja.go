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
	"traffic-a22-data-quality/bdplib"
)

const RequestTimeFormat = "2006-01-02T15:04:05.000-0700"

var BaseUrl = os.Getenv("ODH_NINJA_URL")
var referer = os.Getenv("NINJA_REFERER")

func ar2Path(ar []string) string {
	if len(ar) == 0 {
		return "*"
	}
	var ret string
	for i, s := range ar {
		ret += s
		if i < len(ar)-1 {
			ret += ","
		}
	}
	return ret
}

func makeHistoryPath(req *NinjaRequest) string {
	return fmt.Sprintf("/v2/%s/%s/%s/%s/%s",
		req.Repr,
		ar2Path(req.StationTypes),
		ar2Path(req.DataTypes),
		req.From.Format(RequestTimeFormat),
		req.To.Format(RequestTimeFormat))
}

func makeQueryParam(query *url.Values, name string, value any, defaultValue any) {
	if value != defaultValue {
		query.Add(name, fmt.Sprint(value))
	}
}

func makeQuery(req *NinjaRequest) *url.Values {
	query := &url.Values{}
	makeQueryParam(query, "origin", req.Origin, "")
	makeQueryParam(query, "limit", req.Limit, 200)
	makeQueryParam(query, "offset", req.Offset, 0)
	makeQueryParam(query, "select", req.Select, "")
	makeQueryParam(query, "where", req.Where, "")
	makeQueryParam(query, "shownull", req.Shownull, false)
	makeQueryParam(query, "distinct", req.Distinct, true)
	makeQueryParam(query, "timezone", req.Timezone, "")
	return query
}

func HistoryRequest[T any](req *NinjaRequest, result *NinjaResponse[T]) error {
	u, err := url.Parse(BaseUrl)
	if err != nil {
		return fmt.Errorf("Unable to parse Base URL form config: %w", err)
	}
	u.Path += makeHistoryPath(req)
	u.RawQuery = makeQuery(req).Encode()
	return GetRequestURL[T](u, result)
}

func GetRequest[T any](query string, result *NinjaResponse[T]) error {
	url, _ := url.Parse(BaseUrl + query)
	return GetRequestURL[T](url, result)
}

func GetRequestURL[T any](reqUrl *url.URL, result *NinjaResponse[T]) error {
	slog.Debug("Ninja request with URL: " + reqUrl.String())

	req, err := http.NewRequest(http.MethodGet, reqUrl.String(), nil)
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
