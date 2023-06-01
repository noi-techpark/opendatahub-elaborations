// Copyright (C) 2017 IDM Südtirol - Alto Adige - Italy
// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.idmsuedtirol.bluetoothtrafficelaboration;

import java.io.IOException;
import java.sql.Array;
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.util.ArrayList;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import org.apache.commons.lang3.StringEscapeUtils;

import com.idmsuedtirol.bluetoothtrafficelaboration.DatabaseHelper.ConnectionReady;

/**
 * @author Davide Montesin <d@vide.bz>
 */
public class ElaborationCountBluetooth {

	private static Logger LOG = LoggerFactory.getLogger(ElaborationCountBluetooth.class);

	static final SimpleDateFormat SDF = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");

	static String doElaboration(DatabaseHelper databaseHelper, final String args) throws SQLException, IOException {
		LOG.debug("Do count elaboration with args: " + args);
		final ArrayList<Station> activeStations = databaseHelper.newSelectBluetoothStations();

		String result = databaseHelper.newConnection(new ConnectionReady<String>() {
			@Override
			public String connected(Connection conn) throws SQLException, IOException {
				String sql = DatabaseHelper.readResource(this.getClass(), "elaboration_count_bluetooth.sql");
				PreparedStatement ps = conn.prepareStatement(sql);
				StringBuilder result = new StringBuilder("[");
				for (int s = 0; s < activeStations.size(); s++) {
					Station station = activeStations.get(s);
					result.append(String.format("%s{ id:%3d, name:%-14s",
							s == 0 ? "" : " ",
							station.id,
							"'" + StringEscapeUtils.escapeEcmaScript(station.stationcode) + "'"));
					ps.setInt(1, Integer.parseInt(args));
					ps.setInt(2, station.id);
					ResultSet rs = ps.executeQuery();
					if (rs.next()) {
						Timestamp window_start = rs.getTimestamp(2);
						Timestamp window_end = rs.getTimestamp(3);
						result.append(String.format(", window_start:'%s', window_end:'%s'",
								SDF.format(window_start),
								SDF.format(window_end)));
						Array array = rs.getArray(1);
						Integer[] counters = (Integer[]) array.getArray();
						result.append(String.format(", log:{analyzed: %4d, ins:%4d, upd:%4d, del:%4d}}",
								counters[3],
								counters[2],
								counters[1],
								counters[0]));
					} else {
						result.append("}");
					}
					result.append(s < activeStations.size() - 1 ? ",\n" : "");
					conn.commit();
				}
				return result.toString() + "]";
			}
		});
		return result;
	}
}
