# SPDX-FileCopyrightText: NOI Techpark <digital@noi.bz.it>
#
# SPDX-License-Identifier: AGPL-3.0-or-later

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import yaml

class Parametri:
    def __init__(self, file_yaml):
        with open(file_yaml, 'r') as file:
            self.parametri = yaml.safe_load(file)
    def layer1(self, param):
        return self.parametri['Layer1'][param]
    def layer1_1(self, param):
        return self.parametri['Layer1_1'][param]
    def layer2(self, param):
        return self.parametri['Layer2'][param]
