/*

BluetoothTrafficElaboration: various elaborations of traffic data

Copyright (C) 2017 IDM Südtirol - Alto Adige - Italy

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

*/
package com.idmsuedtirol.bluetoothtrafficelaboration;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;

import org.apache.commons.io.IOUtils;

import com.idmsuedtirol.bluetoothtrafficelaboration.ElaborationsInfo.TaskInfo;

/**
 * @author Davide Montesin <d@vide.bz>
 */
public class DatabaseHelper {

	private final String jdbcUrl;

	String schedulerTaskSql;

	static interface ConnectionReady<T> {
		T connected(Connection conn) throws SQLException, IOException;
	}

	public DatabaseHelper(String jdbcUrl) throws IOException, ClassNotFoundException {
		super();
		Class.forName("org.postgresql.Driver");
		this.jdbcUrl = jdbcUrl;
		this.schedulerTaskSql = readResource(this.getClass(), "scheduler_task.sql");
	}

	<T> T newConnection(ConnectionReady<T> onReady) throws SQLException, IOException {
		Connection conn = DriverManager.getConnection(this.jdbcUrl);
		try {
			conn.setAutoCommit(false);
			conn.createStatement().execute("SET search_path to elaboration, intimev2, public");
			T result = onReady.connected(conn);
			return result;
		} finally {
			conn.rollback();
			conn.close();
		}
	}

	int newUpdate(final String sql, final Object[] args) throws SQLException, IOException {
		int result = this.newConnection(new ConnectionReady<Integer>() {

			@Override
			public Integer connected(Connection conn) throws SQLException {
				PreparedStatement ps = conn.prepareStatement(sql);
				for (int i = 0; i < args.length; i++) {
					ps.setObject(i + 1, args[i]);
				}
				int result = ps.executeUpdate();
				if (result < 1)
					throw new IllegalStateException();
				conn.commit();
				return result;
			}
		});
		return result;
	}

	int newCommand(final String sql) throws SQLException, IOException {
		int result = this.newConnection(new ConnectionReady<Integer>() {
			@Override
			public Integer connected(Connection conn) throws SQLException {
				conn.createStatement().executeUpdate(sql);
				conn.commit();
				return 0;
			}
		});
		return result;
	}

	ArrayList<Station> newSelectBluetoothStations() throws SQLException, IOException {
		ArrayList<Station> result = this.newConnection(new ConnectionReady<ArrayList<Station>>() {
			@Override
			public ArrayList<Station> connected(Connection conn) throws SQLException, IOException {
				ArrayList<Station> result = new ArrayList<Station>();
				String query = readResource(this.getClass(), "stations_bluetooth_active.sql");
				ResultSet rs = conn.createStatement().executeQuery(query);
				while (rs.next()) {
					Station station = new Station();
					station.id = rs.getInt("id");
					station.stationcode = rs.getString("stationcode");
					result.add(station);
				}
				return result;
			}
		});
		return result;
	}

	ArrayList<Station> newSelectLinkStations() throws SQLException, IOException {
		ArrayList<Station> result = this.newConnection(new ConnectionReady<ArrayList<Station>>() {
			@Override
			public ArrayList<Station> connected(Connection conn) throws SQLException, IOException {
				ArrayList<Station> result = new ArrayList<Station>();
				String query = readResource(this.getClass(), "stations_bluetooth_link.sql");
				ResultSet rs = conn.createStatement().executeQuery(query);
				while (rs.next()) {
					Station station = new Station();
					station.id = rs.getInt("id");
					station.stationcode = rs.getString("stationcode");
					result.add(station);
				}
				return result;
			}
		});
		return result;
	}

	ArrayList<TaskInfo> newSelectTaskInfo() throws SQLException, IOException {
		ArrayList<TaskInfo> result = this.newConnection(new ConnectionReady<ArrayList<TaskInfo>>() {
			@Override
			public ArrayList<TaskInfo> connected(Connection conn) throws SQLException {
				ArrayList<TaskInfo> result = new ArrayList<TaskInfo>();

				ResultSet rs = conn.createStatement().executeQuery(DatabaseHelper.this.schedulerTaskSql);
				while (rs.next()) {
					TaskInfo taskInfo = new TaskInfo();
					taskInfo.id = rs.getLong("id");
					taskInfo.calc_order = rs.getInt("calc_order");
					taskInfo.function_name = rs.getString("function_name");
					taskInfo.args = rs.getString("args");
					taskInfo.enabled = rs.getString("enabled").equals("T");
					taskInfo.running = rs.getBoolean("running");
					taskInfo.last_start_time = rs.getString("last_start_time");
					taskInfo.last_duration = rs.getString("last_duration");
					taskInfo.last_status = rs.getString("last_status");
					taskInfo.same_status_since = rs.getString("same_status_since");
					taskInfo.last_run_output = rs.getString("last_run_output");
					result.add(taskInfo);
				}

				return result;
			}
		});
		return result;

	}

	static String readResource(Class relativeTo, String name) throws IOException {
		InputStream in = relativeTo.getResourceAsStream(name);
		ByteArrayOutputStream out = new ByteArrayOutputStream();
		IOUtils.copy(in, out);
		in.close();
		out.close();
		String result = new String(out.toByteArray(), "utf-8");
		return result;
	}

}
