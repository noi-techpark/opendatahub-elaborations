// Copyright (C) 2017 IDM Südtirol - Alto Adige - Italy
// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.idmsuedtirol.bluetoothtrafficelaboration;

import java.io.IOException;
import java.io.StringWriter;

import javax.servlet.ServletConfig;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.annotation.JsonAutoDetect.Visibility;
import com.fasterxml.jackson.databind.ObjectMapper;

/**
 * @author Davide Montesin <d@vide.bz>
 */
public class BluetoothTrafficElaborationServlet extends HttpServlet {

	private static final Logger LOG = LoggerFactory.getLogger(BluetoothTrafficElaborationServlet.class);

	DatabaseHelper databaseHelper;

	TaskThread taskThread;

	@Override
	public void init(ServletConfig config) throws ServletException {
		LOG.info("Servlet initialization");
		try {
			super.init(config);
			this.databaseHelper = createDatabaseHelper();
			this.taskThread = new TaskThread(this.databaseHelper);
			this.taskThread.start();
		} catch (Exception exxx) {
			LOG.error("Servlet initialization failed: {}", exxx.getMessage());
			throw new ServletException(exxx);
		}

	}

	static DatabaseHelper createDatabaseHelper() throws IOException, ClassNotFoundException {
		// docker-compose loads .env vars to environment
		System.getenv("JDBC_URL");
		String jdbcUrl = System.getenv("JDBC_URL");
		DatabaseHelper result = new DatabaseHelper(jdbcUrl);
		return result;
	}

	@Override
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		try {
			ElaborationsInfo elaborationsInfo = new ElaborationsInfo();
			elaborationsInfo.taskThreadAlive = this.taskThread.isAlive();
			synchronized (this.taskThread.exclusiveLock) {
				elaborationsInfo.tashThreadRunning = !this.taskThread.sleeping;
				elaborationsInfo.sleepingUntil = this.taskThread.sleepingUntil;
			}

			elaborationsInfo.tasks.addAll(this.databaseHelper.newSelectTaskInfo());

			ObjectMapper mapper = new ObjectMapper();
			mapper.setVisibility(mapper.getVisibilityChecker().withFieldVisibility(Visibility.NON_PRIVATE));
			StringWriter sw = new StringWriter();
			mapper.writeValue(sw, elaborationsInfo);
			resp.getWriter().write(sw.toString());
		} catch (Exception exxx) {
			LOG.error("Getting data failed: {}", exxx.getMessage());
			throw new ServletException(exxx);
		}
	}

	@Override
	public void destroy() {
		super.destroy();
		this.taskThread.interrupt();
		try {
			this.taskThread.join();
		} catch (InterruptedException e) {
			// TODO should never happens: notify crashbox or throw a RuntimeException
			LOG.error("Destroy failed: {}", e.getMessage());
			e.printStackTrace();
		}
	}
}
