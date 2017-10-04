This is a repository for various one-off NationStates related python scripts. All scripts are written in Python 3 and are provided as-is under a GPLv3 license.

# Endorsement Graph

`generate_links.py` and `generate_links_from_dump.py`

These scripts can be used to generate network graph datasets from a region's WA 
nations. It will generate a list of nodes and edges as CSV files that can quickly be imported into a program like
[Gephi](http://gephi.org/).

Configuration options can be found inside the scripts themselves.

`generate_links.py` will use the NS API to gather live data. Due to API constraints, this is very slow, especially for
large regions. `generate_links_from_dump.py` uses the NS API dumps to quickly process large regions.

# Login Script

`login.py` in conjunction with `login.json`

This script uses new-ish API support for login authentication to keep a set of puppets alive. In conjunction with a `cron` job or other task scheduler, it can be used keep a large set of puppets alive.

Configuration is handled by `login.json`, which has the following format:

```json
{
    "encrypted": false,
    "user_agent": "your email here",
    "nations": {
        "nation name 1": "password 1",
        "nation name 2": "password 2"
    }
}
``` 

After the first run, `login.py` will ask to replace plain-text passwords in the configuration file with authentication hashes provided by the NationStates API. This will not occur if any nation fails to login with the supplied password.

# Manual Recruitment

`recruitment_list.py`

Generates a text file of newly founded/refounded nations, 8 to a line and comma-separated for easy use when manually recruiting. The script uses the API to verify each nation has not blocked recruitment telegrams before adding them to its list.

Configuration options can be found inside the script itself.
