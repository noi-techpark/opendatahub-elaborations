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
