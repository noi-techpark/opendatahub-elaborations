// SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
//
// SPDX-License-Identifier: AGPL-3.0-or-later

package it.unibz.tsmodel;

import javax.servlet.ServletConfig;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;

import org.springframework.context.ApplicationContext;
import org.springframework.scheduling.concurrent.ThreadPoolTaskScheduler;

import io.sentry.Sentry;
import it.unibz.tsmodel.forecast.ForecastCron;

public class MainServlet extends HttpServlet
{
   Thread t;
   
   ApplicationContext ac;
   
   @Override
   public void init(ServletConfig config) throws ServletException
   {
      Sentry.init("https://XXX:XXX@crashbox.davide.bz/4?async=false");
      super.init(config);
      Sentry.capture("MainServlet.init");
      new Thread(new Runnable()
      {
         @Override
         public void run()
         {
            try
            {
               ac = Main.main(null);
            }
            catch (Exception exxx)
            {
               Sentry.capture(exxx);
            }
         }
      }).start();
   }

   @Override
   public void destroy()
   {
      Sentry.capture("MainServlet.destroy");
      super.destroy();
      ThreadPoolTaskScheduler scheduler = ac.getBean(ForecastCron.class).getScheduler();
      // shutdown scheduler
      long start = System.currentTimeMillis();
      
      //scheduler.setWaitForTasksToCompleteOnShutdown(true);
      //scheduler.setAwaitTerminationSeconds(20);
      scheduler.shutdown();
      for (int i = 0; i < 100; i++)
      {
         if (scheduler.getActiveCount() == 0)
            break;
         try
         {
            Thread.sleep(1000);
         }
         catch (InterruptedException e)
         {
            // TODO Auto-generated catch block
            e.printStackTrace();
         }
      }
      long stop = System.currentTimeMillis();
   }
}
