# This file is part of ns_utilities
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

import xml.etree.cElementTree as et
import urllib.request
import urllib.error
import time

# Configuration

region = "Region Goes Here"
user_agent = "User Nation <email goes here>"
rate = 40 / 30
out_file = "nations.txt"  # Rename this as you desire. You can use an absolute or relative path.
refounds = False  # Set to False to instead target feeders

# End Configuration

mode = {True: "https://www.nationstates.net/cgi-bin/api.cgi?q=happenings;view=region.osiris,balder,lazarus;filter=founding",
        False: "https://www.nationstates.net/cgi-bin/api.cgi?q=happenings;view=region.the_pacific,the_north_pacific,the_west_pacific,the_east_pacific,the_south_pacific;filter=founding"}

with open(out_file, 'w') as out:
    headers = {'User-Agent': user_agent + " Recruitment Query"}
    query = urllib.request.Request(
        mode[refounds],
        headers=headers)

    events = et.fromstring(urllib.request.urlopen(query).read().decode()).find('HAPPENINGS')
    time.sleep(rate)

    counter = 0
    buffer = ""
    for event in events:
        nation = event.find('TEXT').text.split('@@')[1]
        try:
            # test if nation can be recruited
            nation_query = urllib.request.Request(
                "https://www.nationstates.net/cgi-bin/api.cgi?nation=" + nation + "&q=tgcanrecruit&from="
                + region.lower().replace(" ", "_"), headers=headers)
            time.sleep(rate)

            # check if nation eligible for recruitment
            if "TGCANRECRUIT>1" in urllib.request.urlopen(nation_query).read().decode():
                print(nation + " is eligible for recruitment.")
                buffer += nation + ','
                counter += 1
                if counter >= 8:
                    buffer = buffer[:-1] + '\n'
                    out.write(buffer)
                    counter = 0
                    buffer = ""
            else:
                print(nation + " is ineligible for recruitment.")
        except urllib.error.HTTPError:
            print(nation + " is invalid.")

    # flush remaining nations to output
    out.write(buffer[:-1])
    print("Data written to " + out_file)
