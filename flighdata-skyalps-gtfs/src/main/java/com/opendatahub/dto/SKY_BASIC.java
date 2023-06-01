// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.dto;
import java.io.Serializable;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import java.lang.String;
@JsonIgnoreProperties(ignoreUnknown = false)
public class SKY_BASIC implements Serializable {

    /**
     *
     */
    private static final long serialVersionUID = 1L;
    private fare fare;
    private Double minimumPriceOneWay;
    private Double minimumPriceRoundTrip;

    public SKY_BASIC() {

    }

    public fare getFare() {
        return fare;
    }

    public void setFare(fare fare) {
        this.fare = fare;
    }

    public Double getMinimumPriceOneWay() {
        return minimumPriceOneWay;
    }

    public void setMinimumPriceOneWay(Double minimumPriceOneWay) {
        this.minimumPriceOneWay = minimumPriceOneWay;
    }

    public Double getMinimumPriceRoundTrip() {
        return minimumPriceRoundTrip;
    }

    public void setMinimumPriceRoundTrip(Double minimumPriceRoundTrip) {
        this.minimumPriceRoundTrip = minimumPriceRoundTrip;
    }

    public SKY_BASIC(fare fare, Double minimumPriceOneWay, Double minimumPriceRoundTrip) {
        super();
        this.fare = fare;
        this.minimumPriceOneWay = minimumPriceOneWay;
        this.minimumPriceRoundTrip = minimumPriceRoundTrip;
    }

    @Override
    public String toString() {
        return "SKY_BASIC [fare=" + fare + ", minimumPriceOneWay=" + minimumPriceOneWay + ", minimumPriceRoundTrip=" + minimumPriceRoundTrip + "]";
    }

}
