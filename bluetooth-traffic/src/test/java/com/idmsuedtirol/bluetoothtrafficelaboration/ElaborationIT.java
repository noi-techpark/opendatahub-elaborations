// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.idmsuedtirol.bluetoothtrafficelaboration;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;

import java.io.IOException;
import java.sql.SQLException;
import java.util.List;

import org.junit.Before;
import org.junit.Test;

import com.idmsuedtirol.bluetoothtrafficelaboration.DatabaseHelper.Task;

public class ElaborationIT {
	private DatabaseHelper databaseHelper;

	@Before
	public void setup() {
		databaseHelper = new DatabaseHelper(System.getenv("JDBC_URL"));
	}

	@Test
	public void testCountBluetooth() throws IOException, SQLException {
		List<Task> tasks = databaseHelper.selectTasks();
		assertFalse(tasks.isEmpty());
		assertNotNull(tasks.get(0).args());
		assertFalse(tasks.get(0).args().isEmpty());
		assertNotNull(Elaboration.COUNT_BLUETOOTH.run(databaseHelper, tasks.get(0).args()));
	}
}
