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

import java.io.IOException;
import java.io.StringWriter;

import javax.servlet.ServletConfig;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import io.github.cdimascio.dotenv.Dotenv;

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
