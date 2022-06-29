package com.idmsuedtirol.bluetoothtrafficelaboration;

import static org.junit.Assert.assertFalse;
import static org.junit.Assert.assertNotNull;

import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.URL;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.Properties;

import org.junit.Before;
import org.junit.Test;

import com.idmsuedtirol.bluetoothtrafficelaboration.ElaborationsInfo.TaskInfo;

public class ElaborationIT {
	private final Properties props = new Properties();
	private DatabaseHelper databaseHelper;
	@Before
	public void setup() throws FileNotFoundException, IOException, ClassNotFoundException {
		  URL resource = getClass().getClassLoader().getResource("app.properties");
		  props.load(new FileInputStream(resource.getFile()));
		  String jdbcUrl = props.getProperty("jdbc.connectionString");
		  databaseHelper = new DatabaseHelper(jdbcUrl);

	}
	@Test
	public void testCountBluetooth() throws ClassNotFoundException, IOException, SQLException {
		ArrayList<TaskInfo> newSelectTaskInfo = databaseHelper.newSelectTaskInfo();
		assertNotNull(newSelectTaskInfo);
		assertFalse(newSelectTaskInfo.isEmpty());
		assertNotNull(newSelectTaskInfo.get(0).args);
		assertFalse(newSelectTaskInfo.get(0).args.isEmpty());
		String args = newSelectTaskInfo.get(0).args;
		String doElaboration = ElaborationCountBluetooth.doElaboration(databaseHelper, args);
		assertNotNull(doElaboration);
	}

}
