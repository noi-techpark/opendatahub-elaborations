// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.opendatahub.enumClasses;

public enum agency_lang {
	Italian(1), English(2), French(3), Spanish(4), Japanese(5), Null(0);

	private final int value;

	agency_lang(final int newValue) {
		value = newValue;
	}

	public int getValue() {
		return value;
	}

	public static agency_lang valueOf(int i) {
		if (i == 1) {
			return Italian;
		} else if (i == 2) {
			return English;
		} else if (i == 3) {
			return French;
		} else if (i == 4) {
			return Spanish;
		} else if (i == 5) {
			return Japanese;
		} else {
			return Null;
		}
	}
}
