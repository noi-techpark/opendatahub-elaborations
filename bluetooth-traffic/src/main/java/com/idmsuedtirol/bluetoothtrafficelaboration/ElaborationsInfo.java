// Copyright (C) 2017 IDM Südtirol - Alto Adige - Italy
// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package com.idmsuedtirol.bluetoothtrafficelaboration;

import java.util.ArrayList;

/**
 * @author Davide Montesin <d@vide.bz>
 */
public class ElaborationsInfo
{
   public static class TaskInfo
   {
      long    id;
      int     calc_order;
      String  function_name;
      String  args;
      boolean enabled;
      boolean running;
      String  last_start_time;
      String  last_duration;
      String  last_status;
      String  same_status_since;
      String  last_run_output;
   }

   boolean             taskThreadAlive;
   boolean             tashThreadRunning;
   ArrayList<TaskInfo> tasks = new ArrayList<TaskInfo>();
   long                sleepingUntil;
}
