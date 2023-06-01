-- SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
--
-- SPDX-License-Identifier: AGPL-3.0-or-later

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
-- Davide Montesin <d@vide.bz>


with tasks as
(
   select id, 
	       calc_order, 
	       function_name, 
	       args, 
	       enabled, 
	       -- status,
	       status = 'RUNNING' running
     from scheduler_task task
    where calc_order is not null
)
,
tasks_last_run_id as
(
   select *,
	       (
	          select id
	            from scheduler_run run
	           where run.task_id = tasks.id
	           order by run.start_time desc, run.id desc
	           limit 1
	       ) as last_run_id
     from tasks
)
,
tasks_last_run as
(
   select tasks_last_run_id.*,
          last_run.start_time as last_start_time,
          to_char(last_run.stop_time - last_run.start_time,'hh24:mi:ss') as last_duration,
          last_run.status as last_status,
          last_run.run_output as last_run_output
     from tasks_last_run_id
     left outer join scheduler_run last_run on tasks_last_run_id.last_run_id = last_run.id
)
,
tasks_last_run_status_since as
(
   select coalesce(to_char(extract( epoch from (last_start_time - (
             select max(start_time)
               from scheduler_run since
              where since.task_id = tasks_last_run.id
                and since.status != tasks_last_run.last_status
          )))/(3600*24), '999990.000'), 'always') same_status_since,
          (
          select last_start_time -max(start_time)
               from scheduler_run since
              where since.task_id = tasks_last_run.id
                and since.status != tasks_last_run.last_status
          ),
          *
     from tasks_last_run
)
select *
  from tasks_last_run_status_since
 order by calc_order
