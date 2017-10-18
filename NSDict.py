# NSDict - Generate dictionaries from Nationstates API queries and dumps
# Copyright 2017 Khronion <khronion@gmail.com>
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# The software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the software.  If not, see <http://www.gnu.org/licenses/>.

import xml.etree.cElementTree as ElementTree
import xml.etree.ElementTree
import collections
import gzip


class EntityDict(collections.OrderedDict):
    """Extended ordered dict that contains every game in the region and all their attributes"""

    class Entity(object):
        """Simple utility class to allow object notation access to data"""
        def __init__(self, attr, kind=''):
            self.kind = kind
            self.__dict__.update(attr)

    def __init__(self, dump, entity_tag, entity_name, int_types, float_types):
        super().__init__()
        try:
            self.entity_tree = ElementTree.fromstring(dump)
        except xml.etree.ElementTree.ParseError:
            try:
                with gzip.open(dump) as entities_xml:
                    try:
                        self.entity_tree = ElementTree.parse(entities_xml).getroot()
                    except xml.etree.ElementTree.ParseError:
                        raise RuntimeError("Invalid dump or API query.")
            except OSError:
                with open(dump) as entities_xml:
                    try:
                        self.entity_tree = ElementTree.parse(entities_xml).getroot()
                    except xml.etree.ElementTree.ParseError:
                        raise RuntimeError("Invalid dump or API query.")

        for entity in self.entity_tree.iter(entity_tag):
            attributes = {}
            name = None

            # Store all attributes in dictionary. This approach guarantees new shards are automatically included.
            for attribute in entity:
                if attribute.tag == entity_name:
                    name = attribute.text.lower()
                elif attribute.tag in int_types:  # deal with ints
                    attributes[attribute.tag.lower()] = int(attribute.text)
                elif attribute.tag in float_types:  # deal with floats
                    attributes[attribute.tag.lower()] = float(attribute.text)
                else:
                    attributes[attribute.tag.lower()] = attribute.text
                # handle special cases
                self._custom_attribute_process(attribute, attributes)
            # store data
            self._post_entity_process(attributes)
            self[name] = self.Entity(attributes, entity_tag)

        # handle special cases
        self._post_process()

    def _custom_attribute_process(self, attribute, attributes):
        """This can be overriden to do processing after an attribute is parsed"""
        pass

    def _post_entity_process(self, attributes):
        """This can be overriden to do processing on a dictionary of attributes generated after an entity is parsed"""
        pass

    def _post_process(self):
        """This can be overriden to do processing once EntityDict is done populating itself from the xml"""
        pass


class NationDict(EntityDict):
    def __init__(self, dump):
        super().__init__(dump, 'NATION', 'NAME',
                         ['POPULATION', 'FACTBOOKS', 'DISPATCHES', 'FIRSTLOGIN', 'LASTLOGIN'],
                         ['TAX'])

    def _custom_attribute_process(self, attribute, attributes):
        if attribute.tag == 'ENDORSEMENTS':
            if attribute.text is not None:
                attributes['endorsements'] = attribute.text.split(',')
            else:
                attributes['endorsements'] = []
        elif attribute.tag == 'FREEDOM':
            attributes['freedom'] = {}
            for freedom in attribute:
                attributes['freedom'][freedom.tag] = freedom.text
        elif attribute.tag == 'FREEDOMSCORES':
            attributes['freedomscores'] = {}
            for score in attribute:
                attributes['freedomscores'][score.tag] = int(score.text)
        elif attribute.tag == 'GOVT':
            attributes['govt'] = {}
            for priority in attribute:
                attributes['govt'][priority.tag.lower()] = float(priority.text)
        elif attribute.tag == 'DEATHS':
            attributes['deaths'] = {}
            for cause in attribute:
                name = cause.attrib[list(cause.attrib.keys())[0]]
                attributes['deaths'][name] = float(cause.text)


class RegionDict(EntityDict):
    def __init__(self, dump):
        super().__init__(dump, 'REGION', 'NAME',
                         ['NUMNATIONS', 'LASTUPDATE', 'DELEGATEVOTES', 'FIRSTLOGIN', 'LASTLOGIN'],
                         ['TAX', 'PUBLICSECTOR'])

    def _custom_attribute_process(self, attribute, attributes):
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
                    attributes['officers'].append(self.Entity(officer, 'OFFICER'))

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

    def _post_entity_process(self, attributes):
        """Handle cumulative population generation"""
        try:
            last = self[next(reversed(self))]
            attributes['cumulative_population'] = last.cumulative_population + last.numnations
        except StopIteration:
            attributes['cumulative_population'] = 0

    def _post_process(self):
        """Derive useful world analyses from dataset"""
        self.total_population = next(reversed(self.values())).cumulative_population
        self.total_regions = len(self)
        self.update_start = list(self.items())[0][1].lastupdate
        self.update_end = list(self.items())[-1][1].lastupdate
        self.update_length = list(self.items())[-1][1].lastupdate - list(self.items())[0][1].lastupdate

        self.reverse_lookup = collections.OrderedDict()
        for region in self:
            for nation in self[region].nations:
                self.reverse_lookup[nation] = region