# METRo : Model of the Environment and Temperature of Roads
# METRo is Free and is proudly provided by the Government of Canada
# Copyright (C) Her Majesty The Queen in Right of Canada, Environment Canada, 2006
#
#  Questions or bugs report: metro@ec.gc.ca
#  METRo repository: https://framagit.org/metroprojects/metro
#  Documentation: https://framagit.org/metroprojects/metro/wikis/home
#
# Code contributed by:
#  Miguel Tremblay - Canadian meteorological center
#  Francois Fortin - Canadian meteorological center
#
#  $LastChangedDate$
#  $LastChangedRevision$
##################################################################################
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA


from executable_module.metro_string2dom import Metro_string2dom
import metro_logger
import metro_error
from toolbox import metro_util


_ = metro_util.init_translation('metro_string2dom_forecast')


class Metro_string2dom_forecast(Metro_string2dom):

    # methodes redefinies
    def start(self):
        Metro_string2dom.start(self)
        self.__string2dom()

    # methodes privees
    def __string2dom(self):
        if self.infdata_exist('FORECAST'):
            pForecast = self.get_infdata_reference('FORECAST')
            sForecast = pForecast.get_input_information()
            try:
                domForecast = self._convert_string2dom(sForecast)
            except metro_error.Metro_xml_error as inst:
                sMessage = _("Fatal Error when converting forecast ") +\
                           _("string to DOM. The error is:\n%s") % (str(inst))
                metro_logger.print_message(metro_logger.LOGGER_MSG_STOP, sMessage)
            else:
                pForecast.set_input_information(domForecast)
        else:
            sMessage = _("Fatal Error, no forecast string to convert.")
            metro_logger.print_message(metro_logger.LOGGER_MSG_STOP, sMessage)
