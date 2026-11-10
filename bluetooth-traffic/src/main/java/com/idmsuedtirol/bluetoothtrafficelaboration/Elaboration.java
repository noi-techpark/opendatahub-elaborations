// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.idmsuedtirol.bluetoothtrafficelaboration;

import java.io.IOException;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Timestamp;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.idmsuedtirol.bluetoothtrafficelaboration.DatabaseHelper.Station;

/**
 * The elaborations selectable by scheduler_task.function_name. Each one runs
 * its SQL (a function call returning counters) for every station of its kind.
 *
 * @author Davide Montesin <d@vide.bz>
 */
enum Elaboration {

	COUNT_BLUETOOTH("count_bluetooth_intime", "stations_bluetooth_active.sql", null, false,
			"elaboration_count_bluetooth.sql"),
	CREATE_BLUETOOTH_LHV("create_bluetooth_lhv", "stations_bluetooth_active.sql", null, false,
			"elaboration_create_bluetooth_hv.sql", "elaboration_create_bluetooth_lv.sql"),
	CREATE_MATCHES("create_matches", "stations_bluetooth_link.sql", 1, true,
			"elaboration_create_matches.sql"),
	COUNT_MATCH("count_match_intime", "stations_bluetooth_link.sql", null, false,
			"elaboration_count_matches.sql"),
	RUN_MODE("run_mode_intime", "stations_bluetooth_link.sql", null, true,
			"elaboration_mode.sql"),
	RUN_MODE_100KMH("run_mode_intime_100kmh", "stations_bluetooth_link.sql", null, true,
			"elaboration_mode_100kmh.sql"),
	COMPUTE_BSPEED("compute_bspeed", "stations_bluetooth_link.sql", null, false,
			"elaboration_speed.sql"),
	COMPUTE_BSPEED_100KMH("compute_bspeed_100kmh", "stations_bluetooth_link.sql", null, false,
			"elaboration_speed_100kmh.sql");

	private static final Logger LOG = LoggerFactory.getLogger(Elaboration.class);
	private static final DateTimeFormatter TIME = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

	private final String functionName;
	private final String stationsSql;
	/** value of the first SQL parameter; null = the task args (period in seconds) */
	private final Integer fixedParam;
	private final boolean logTime;
	private final String[] sqlFiles;

	Elaboration(String functionName, String stationsSql, Integer fixedParam, boolean logTime, String... sqlFiles) {
		this.functionName = functionName;
		this.stationsSql = stationsSql;
		this.fixedParam = fixedParam;
		this.logTime = logTime;
		this.sqlFiles = sqlFiles;
	}

	static Optional<Elaboration> forFunction(String functionName) {
		for (Elaboration e : values()) {
			if (e.functionName.equals(functionName))
				return Optional.of(e);
		}
		return Optional.empty();
	}

	/** @return a human readable summary, stored as run_output */
	String run(DatabaseHelper db, String args) throws SQLException, IOException {
		LOG.debug("Do {} elaboration with args: {}", this.functionName, args);
		List<Station> stations = db.selectStations(this.stationsSql);
		int param = this.fixedParam != null ? this.fixedParam : Integer.parseInt(args);
		// with more than one SQL the whole run is a single transaction
		boolean commitPerStation = this.sqlFiles.length == 1;

		return db.newConnection(conn -> {
			List<String> lines = new ArrayList<>();
			for (String sqlFile : this.sqlFiles) {
				try (PreparedStatement ps = conn.prepareStatement(DatabaseHelper.readResource(Elaboration.class, sqlFile))) {
					for (Station station : stations) {
						lines.add(this.runStation(ps, param, station));
						if (commitPerStation)
							conn.commit();
					}
				}
			}
			conn.commit();
			return "[" + String.join(",\n ", lines) + "]";
		});
	}

	private String runStation(PreparedStatement ps, int param, Station station) throws SQLException {
		StringBuilder line = new StringBuilder(String.format("{ id:%3d, name:%-14s", station.id(),
				"'" + station.stationcode().replace("\\", "\\\\").replace("'", "\\'") + "'"));
		ps.setInt(1, param);
		ps.setInt(2, station.id());
		long start = System.currentTimeMillis();
		try (ResultSet rs = ps.executeQuery()) {
			if (rs.next()) {
				line.append(String.format(", window_start:'%s', window_end:'%s'",
						format(rs.getTimestamp(2)), format(rs.getTimestamp(3))));
				if (this.logTime)
					line.append(String.format(", elab_time_ms: %8d", System.currentTimeMillis() - start));
				Integer[] c = (Integer[]) rs.getArray(1).getArray();
				line.append(String.format(", log:{analyzed: %4d, ins:%4d, upd:%4d, del:%4d}", c[3], c[2], c[1], c[0]));
			}
		}
		return line.append("}").toString();
	}

	private static String format(Timestamp t) {
		return t.toLocalDateTime().format(TIME);
	}
}
