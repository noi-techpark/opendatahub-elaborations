// Copyright (C) 2017 IDM Südtirol - Alto Adige - Italy
// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.idmsuedtirol.bluetoothtrafficelaboration;

import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;

/**
 * @author Davide Montesin <d@vide.bz>
 */
public class DatabaseHelper {

	record Station(int id, String stationcode) {
	}

	record Task(long id, String functionName, String args) {
	}

	@FunctionalInterface
	interface ConnectionReady<T> {
		T connected(Connection conn) throws SQLException, IOException;
	}

	private final String jdbcUrl;

	public DatabaseHelper(String jdbcUrl) {
		this.jdbcUrl = jdbcUrl;
	}

	/** Runs onReady in a transaction that is rolled back unless it commits. */
	<T> T newConnection(ConnectionReady<T> onReady) throws SQLException, IOException {
		try (Connection conn = DriverManager.getConnection(this.jdbcUrl)) {
			try {
				conn.setAutoCommit(false);
				try (Statement st = conn.createStatement()) {
					st.execute("SET search_path to elaboration, intimev2, public");
				}
				return onReady.connected(conn);
			} finally {
				conn.rollback();
			}
		}
	}

	int newUpdate(String sql, Object... args) throws SQLException, IOException {
		return this.newConnection(conn -> {
			try (PreparedStatement ps = conn.prepareStatement(sql)) {
				for (int i = 0; i < args.length; i++) {
					ps.setObject(i + 1, args[i]);
				}
				int result = ps.executeUpdate();
				if (result < 1)
					throw new IllegalStateException("No row updated: " + sql);
				conn.commit();
				return result;
			}
		});
	}

	void newCommand(String sql) throws SQLException, IOException {
		this.newConnection(conn -> {
			try (Statement st = conn.createStatement()) {
				st.executeUpdate(sql);
			}
			conn.commit();
			return null;
		});
	}

	List<Station> selectStations(String sqlResource) throws SQLException, IOException {
		String sql = readResource(DatabaseHelper.class, sqlResource);
		return this.newConnection(conn -> {
			List<Station> result = new ArrayList<>();
			try (Statement st = conn.createStatement(); ResultSet rs = st.executeQuery(sql)) {
				while (rs.next()) {
					result.add(new Station(rs.getInt("id"), rs.getString("stationcode")));
				}
			}
			return result;
		});
	}

	List<Task> selectTasks() throws SQLException, IOException {
		String sql = readResource(DatabaseHelper.class, "scheduler_task.sql");
		return this.newConnection(conn -> {
			List<Task> result = new ArrayList<>();
			try (Statement st = conn.createStatement(); ResultSet rs = st.executeQuery(sql)) {
				while (rs.next()) {
					result.add(new Task(rs.getLong("id"), rs.getString("function_name"), rs.getString("args")));
				}
			}
			return result;
		});
	}

	static String readResource(Class<?> relativeTo, String name) throws IOException {
		try (InputStream in = relativeTo.getResourceAsStream(name)) {
			return new String(in.readAllBytes(), StandardCharsets.UTF_8);
		}
	}
}
