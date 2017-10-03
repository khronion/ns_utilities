# This file is part of Endorsement Graph.
# Copyright 2017 Khronion <khronion@gmail.com>
#
# Endorsement Graph is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Endorsement Graph is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Endorsement Graph.  If not, see <http://www.gnu.org/licenses/>.

import gzip
import xml.etree.cElementTree as eTree

# Configuration --------------

target = "TARGET REGION"
nation_dump = "nations.xml.gz"

# End Configuration ---------


def fix(s):
    return s.lower().replace(" ", "_")


# get list of nations
with gzip.open(nation_dump) as nation_dump:
    print("Loading data.")
    world_nations = eTree.parse(nation_dump).getroot()
    print("Loading complete.")

    uid = {}
    i = 0
    endorsements = []

    print("Processing nations.")
    for nation in world_nations:
        if fix(nation.find("REGION").text) == fix(target):
            # assign UID
            uid[fix(nation.find("NAME").text)] = i
            i += 1

            # create endorsements
            try:
                endorsement_list = nation.find("ENDORSEMENTS").text.split(",")
                for endorsement in endorsement_list:
                    endorsements.append([fix(nation.find("NAME").text), fix(endorsement)])
                    print("\t{} endorsing {}".format(fix(nation.find("NAME").text), fix(endorsement)))

            except AttributeError:
                pass  # no endorsements, skip

    print('Processing nations complete.')

    # write node list
    with open(fix(target) + ".nodes.csv", 'w') as out:
        out.write("id,Label\n")
        for nation in uid:
            out.write("{uid},{nation}\n".format(uid=uid[nation], nation=nation))

    # write edge list
    with open(fix(target) + ".edges.csv", 'w') as out:
        out.write("Source,Target\n")
        for endorsement in endorsements:
            try:
                out.write("{source},{target}\n".format(source=uid[endorsement[0]], target=uid[endorsement[1]]))
            except KeyError:
                pass  # nation has CTE'd, remove from edge list
