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
###################################################################################
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


_ = metro_util.init_translation('metro_read_station')


class Metro_string2dom_observation_ref(Metro_string2dom):

    # redefined methods
    def start(self):
        Metro_string2dom.start(self)
        self.__string2dom()

    #  private methods
    def __string2dom(self):
        if self.infdata_exist('OBSERVATION_REF'):
            pObservation_ref = self.get_infdata_reference('OBSERVATION_REF')
            sObservation_ref = pObservation_ref.get_input_information()
            try:
                domObservation_ref = self._convert_string2dom(sObservation_ref)
            except metro_error.Metro_xml_error as inst:
                sMessage = _("Fatal Error when converting observation_ref ") + \
                           _("string to DOM. The error is:\n%s") % (str(inst))
                metro_logger.print_message(metro_logger.LOGGER_MSG_STOP, sMessage)
            else:
                pObservation_ref.set_input_information(domObservation_ref)
        else:
            sMessage = _("Error, no observation_ref string to convert.\n") + \
                       _("You can safely remove this module from the ") +\
                       _("EXECUTION SEQUENCE\nif you don't need it")
            metro_logger.print_message(metro_logger.LOGGER_MSG_WARNING, sMessage)


