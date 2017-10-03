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

import time
import json
import urllib.request
import urllib.error


def fix(s):
    return s.lower().replace(" ", "_")

with open('login.json', 'r') as config:
    config = json.load(config)

query = "https://www.nationstates.net/cgi-bin/api.cgi?nation={}&q=ping"
errors = False

for nation in config['nations']:
    print("Logging in to " + fix(nation))
    # prepare headers
    if config['encrypted']:
        api_call = urllib.request.Request(url=query.format(fix(nation)),
                                          headers={'User-Agent': 'login.py in use by ' + config['user_agent'],
                                                   'X-Autologin': config['nations'][nation]})
    else:
        api_call = urllib.request.Request(url=query.format(fix(nation)),
                                          headers={'User-Agent': 'login.py in use by ' + config['user_agent'],
                                                   'X-Password': config['nations'][nation]})

    # log into nations
    try:
        with urllib.request.urlopen(api_call) as response:
            config['nations'][nation] = response.info()['X-autologin']
    except urllib.error.HTTPError:
        print("Failed to login to " + fix(nation) + ". Did you provide the correct password?")
        errors = True  # flag for login errors, skip encryption stage
    time.sleep(1)

# dump file
if not config['encrypted'] and not errors:
    if fix(input("Do you want to encrypt the configuration file?")) == 'y':
        print("Encrypting passwords in configuration file.")
        config['encrypted'] = True
        with open('login.json', 'w') as out:
            json.dump(config, out, indent=4)