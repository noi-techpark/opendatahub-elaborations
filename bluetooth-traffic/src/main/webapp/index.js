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
/*
 Author: Davide Montesin <d@vide.bz>
 */
(function()
{
   window.com_idmsuedtirol_bte = function()
   {
      
      var start_time = new Date().getTime();
      
      var lastResponseText = '';

      request_data();

      function request_data()
      {
         var now = new Date().getTime();

         if (now - start_time > 1000 * 60 * 10)
         {
            alert('Press ok to continue realtime monitoring ...');
            start_time = new Date().getTime();
         }

         var xhttp = new XMLHttpRequest();
         xhttp.onreadystatechange = function()
         {
            if (this.readyState == 4)
            {
               if (this.status == 200)
               {
                  document.getElementById('last_refresh').innerText = new Date().toString();
                  if (lastResponseText != this.responseText)
                  {
                     lastResponseText = this.responseText;
                     var data = JSON.parse(this.responseText);
                     refresh_ui(data)
                  }
                  setTimeout(function()
                  {
                     request_data();
                  }, 5000);
               }
               else
               {
                  // TODO report error, then retry after some seconds
                  // alert('Error: ' + this.status)
                  setTimeout(function()
                  {
                     request_data();
                  }, 5000);
               }
            }
         };
         xhttp.open('GET', 'data', true);
         xhttp.send();
      }

      var taskRow = document.getElementById('task-row-template');
      taskRow.parentElement.removeChild(taskRow);
      var prevTaskTableRows = [];

      function refresh_ui(data)
      {

         var tasktable = document.getElementById('task');
         document.getElementById('sched_live').className = data.taskThreadAlive ? 'alive' : 'dead';
         document.getElementById('task_thread_status').className = data.tashThreadRunning ? 'running' : 'sleeping';
         document.getElementById('sleepingUntil').innerText = data.sleepingUntil == 0 ? '' : new Date(data.sleepingUntil).toString();
         var tasks = data.tasks;
         // remove previuos data
         for (var i = 0; i < prevTaskTableRows.length; i++)
         {
            prevTaskTableRows[i].parentElement.removeChild(prevTaskTableRows[i])
         }
         prevTaskTableRows = []
         for (var i = 0; i < tasks.length; i++)
         {
            var taskTr = taskRow.cloneNode(true);
            var tds = taskTr.getElementsByTagName('td');
            var task = tasks[i];
            tds[0].innerText = task.calc_order
            tds[1].innerText = task.function_name
            tds[2].innerText = task.args
            tds[3].innerText = task.enabled
            tds[4].innerText = task.last_start_time
            if (task.running)
               taskTr.className = 'RUNNING'
            else
               taskTr.className = ''
            tds[5].innerText = task.last_duration
            tds[6].innerText = task.last_status
            tds[6].className = task.last_status
            tds[7].innerText = task.same_status_since
            tds[8].getElementsByTagName('textarea')[0].value = task.last_run_output
            tasktable.appendChild(taskTr)
            prevTaskTableRows.push(taskTr);
         }
      }
   }
})();
