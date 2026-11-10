// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.idmsuedtirol.bluetoothtrafficelaboration;

import java.util.concurrent.CountDownLatch;
import java.util.concurrent.atomic.AtomicBoolean;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

/**
 * Runs all elaborations once and exits; scheduling is up to the caller (k8s
 * CronJob). On SIGTERM the running task is finished and the remaining ones are
 * skipped. Exit code is 1 if the run itself could not be executed.
 */
public final class Main {

	private static final Logger LOG = LoggerFactory.getLogger(Main.class);

	private Main() {
	}

	public static void main(String[] args) {
		String jdbcUrl = System.getenv("JDBC_URL");
		if (jdbcUrl == null || jdbcUrl.isBlank()) {
			LOG.error("JDBC_URL is not set");
			System.exit(1);
		}

		AtomicBoolean stop = new AtomicBoolean();
		CountDownLatch finished = new CountDownLatch(1);
		Runtime.getRuntime().addShutdownHook(new Thread(() -> {
			if (finished.getCount() == 0)
				return;
			LOG.info("Shutdown requested");
			stop.set(true);
			try {
				finished.await();
			} catch (InterruptedException e) {
				Thread.currentThread().interrupt();
			}
		}));

		int exitCode = 0;
		try {
			new ElaborationRunner(new DatabaseHelper(jdbcUrl), stop::get).run();
		} catch (Exception e) {
			LOG.error("Error executing elaborations", e);
			exitCode = 1;
		} finally {
			finished.countDown();
		}
		System.exit(exitCode);
	}
}
