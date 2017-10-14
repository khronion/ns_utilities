# This file is part of ns_utilities.
# Copyright 2017 Khronion <khronion@gmail.com>
#
# ns_utilities is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# ns_utilities is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with ns_utilities.  If not, see <http://www.gnu.org/licenses/>.

import xml.etree.cElementTree as ElementTree
import collections
import gzip


class RegionDict(collections.OrderedDict):
    """Extended ordered dict that contains every game in the region and all their attributes"""

    class Bunch(object):
        """Simple utility class to allow object notation access to data"""
        def __init__(self, attr):
            self.__dict__.update(attr)

    def __init__(self, dump='regions.xml.gz'):
        super(RegionDict, self).__init__()
        with gzip.open(dump) as region_xml:
            region_tree = ElementTree.parse(region_xml).getroot()

        total_population = 0  # used to calculate cumulative population
        for r in region_tree.iter("REGION"):
            attributes = {}
            name = None

            # Store all attributes in dictionary. This approach guarantees new shards are automatically included.
            num_types = ['NUMNATIONS', 'LASTUPDATE', 'DELEGATEVOTES']  # these shards should be converted to int
            for attribute in r:
                # special embassy logic
                if attribute.tag == 'EMBASSIES':
                    attributes['embassies'] = []
                    for embassy in attribute:
                        attributes['embassies'].append(embassy.text)

                # special RO logic
                elif attribute.tag == 'OFFICERS':
                    attributes['officers'] = []
                    for officer in attribute:
                        officer_attributes = {}
                        for officer_attribute in officer_attributes:
                            officer[officer_attribute.tag.lower()] = officer_attribute.text
                        if len(officer) > 0:
                            attributes['officers'].append(self.Bunch(officer))

                # special nations logic
                elif attribute.tag == 'NATIONS':
                    if attribute.text is not None:
                        attributes['nations'] = attribute.text.split(":")
                    else:
                        attributes['nations'] = []

                # special delegate logic
                elif attribute.tag == 'DELEGATE':
                    if attribute.text == '0':
                        attributes['delegate'] = None
                    else:
                        attributes['delegate'] = attribute.text

                # everything else
                else:
                    if attribute.tag == 'NAME':
                        # used as lookup key for easy searching in the future
                        name = attribute.text.lower().replace(" ", "_")
                    if attribute.tag in num_types:  # deal with numbers
                        attributes[attribute.tag.lower()] = int(attribute.text)
                    else:
                        attributes[attribute.tag.lower()] = attribute.text

            # update cumulative population total
            attributes['cumulative_population'] = total_population
            total_population += attributes['numnations']

            # store data
            self[name] = self.Bunch(attributes)

        self.total_population = next(reversed(self.values())).cumulative_population
        self.total_regions = len(self)
        self.update_start = list(self.items())[0][1].lastupdate
        self.update_end = list(self.items())[-1][1].lastupdate
        self.update_length = list(self.items())[-1][1].lastupdate - list(self.items())[0][1].lastupdate