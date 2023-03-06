#!/usr/bin/env python3

# Contest Management System - http://cms-dev.github.io/
# Copyright © 2013 Luca Wehrstedt <luca.wehrstedt@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""A class to update a dump created by CMS.

Used by DumpImporter and DumpUpdater.

This adapts the dump to some changes in the model introduced in commits
483ee85965f527cbc459ebe7e010c6854661b6eb
e051ee4d2667ba381a24c7b1764a6d9c3d792b45
d66951d3149a954fb0b81b6015e8e0b060020152

"""


class Updater:

    def __init__(self, data):
        assert data["_version"] == 2
        self.objs = data

    def run(self):
        for k, v in self.objs.items():
            if k.startswith("_"):
                continue
            if v["_class"] == "User":
                if v["email"] == "":
                    v["email"] = None
                if v["ip"] == "0.0.0.0":
                    v["ip"] = None

        return self.objs
