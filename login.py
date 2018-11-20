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


try:
    with open('login.json', 'r') as cfg:
        config = json.load(cfg)
except json.decoder.JSONDecodeError:
    input("Invalid JSON file! Hit ENTER to terminate.")
    exit()

query = "https://www.nationstates.net/cgi-bin/api.cgi?nation={}&q=ping"
errors = False

# log into nations with plaintext passwords and store hashes
hashes = {}
for nation in config['nations']:
    print("Logging in to " + fix(nation))

    # prepare header
    api_call = urllib.request.Request(url=query.format(fix(nation)),
                                      headers={'User-Agent': 'login.py in use by ' + config['user_agent'],
                                               'X-Password': config['nations'][nation]})

    # log into nation
    try:
        with urllib.request.urlopen(api_call) as response:
            hashes[nation] = response.info()['X-autologin']  # store hash
    except urllib.error.HTTPError:
        print("Failed to login to " + fix(nation) + ". Did you provide the correct password?")
    time.sleep(1)

# log into nations with password hashes
try:
    for nation in config['encrypted']:
        print("Logging in to " + fix(nation))

        # prepare header
        api_call = urllib.request.Request(url=query.format(fix(nation)),
                                          headers={'User-Agent': 'login.py in use by ' + config['user_agent'],
                                                   'X-Autologin': config['encrypted'][nation]})

        # log into nation
        try:
            with urllib.request.urlopen(api_call) as response:
                pass
        except urllib.error.HTTPError:
            print("Failed to login to " + fix(nation) + ". If you have changed its password, please re-add to login.json "
                                                        "as a new nation.")
        time.sleep(1)
except TypeError:
    pass

# dump file
if len(config['nations']) > 0 and fix(input("Do you want to encrypt the configuration file? (y/n) ")) == 'y':
    print("Encrypting passwords in configuration file.")

    # store encrypted hash and delete plain-text hash
    for nation in hashes:
        del config['nations'][nation]
        config['encrypted'][nation] = hashes[nation]

    with open('login.json', 'w') as out:
        json.dump(config, out, indent=4)
