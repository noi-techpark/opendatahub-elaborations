// Copyright (C) 2017 IDM Südtirol - Alto Adige - Italy
// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.idmsuedtirol.bluetoothtrafficelaboration;

import java.io.IOException;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.sql.Timestamp;
import java.util.Optional;
import java.util.function.BooleanSupplier;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.idmsuedtirol.bluetoothtrafficelaboration.DatabaseHelper.Task;

/**
 * Runs all configured elaborations once, in order. After the first failure the
 * remaining ones are skipped (they may depend on each other).
 *
 * @author Davide Montesin <d@vide.bz>
 */
public class ElaborationRunner {

	private static final Logger LOG = LoggerFactory.getLogger(ElaborationRunner.class);

	private final DatabaseHelper db;
	private final BooleanSupplier stopRequested;

	public ElaborationRunner(DatabaseHelper db, BooleanSupplier stopRequested) {
		this.db = db;
		this.stopRequested = stopRequested;
	}

	public void run() throws SQLException, IOException {
		LOG.info("Start elaboration...");
		boolean someTaskFailed = false;
		for (Task task : this.db.selectTasks()) {
			long startTime = System.currentTimeMillis();
			this.db.newUpdate("update scheduler_task set status = ?, last_run_time = ? where id = ?",
					"RUNNING", new Timestamp(startTime), task.id());

			String status;
			String output = "";
			if (someTaskFailed) {
				status = "PREV-FAIL";
			} else {
				try {
					output = this.execute(task);
					status = "DONE";
				} catch (Exception e) {
					LOG.error("Elaboration execution failed", e);
					someTaskFailed = true;
					status = "FAIL";
					StringWriter sw = new StringWriter();
					e.printStackTrace(new PrintWriter(sw));
					output = sw.toString();
				}
			}

			this.db.newUpdate("update scheduler_task set status = ? where id = ?", status, task.id());
			this.db.newUpdate("insert into scheduler_run (task_id, status, start_time, stop_time, run_output) "
					+ "values (?,?,?,?,?)",
					task.id(), status, new Timestamp(startTime), new Timestamp(System.currentTimeMillis()), output);

			if (this.stopRequested.getAsBoolean())
				return;
		}
		this.db.newCommand("analyze measurementhistory");
		this.updateLastElaborationCache();
		LOG.info("Elaboration done.");
	}

	private String execute(Task task) throws SQLException, IOException {
		Optional<Elaboration> elaboration = Elaboration.forFunction(task.functionName());
		if (elaboration.isEmpty()) {
			LOG.warn("Unknown elaboration function '{}', nothing to do", task.functionName());
			return "";
		}
		return elaboration.get().run(this.db, task.args());
	}

	private void updateLastElaborationCache() throws SQLException, IOException {
		String sql = DatabaseHelper.readResource(ElaborationRunner.class, "last_elaboration_cache.sql");
		this.db.newConnection(conn -> {
			try (Statement st = conn.createStatement(); ResultSet rs = st.executeQuery(sql)) {
				rs.next();
				LOG.debug("last elaboration cache: {} inserted, {} updated", rs.getInt("nr_insert"), rs.getInt("nr_update"));
			}
			conn.commit();
			return null;
		});
	}
}
