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
    "user_agent": "Your email or other identifier goes here",
    "nations": {
        "nation one": "password one",
        "nation two": "password two"
    },
    "encrypted": {
        "nation three": "hash goes here",
        "nation four": "hash goes here"
    }
}
``` 

After a successful run with no login errors, `login.py` will offer to replace plain-text passwords in the configuration file with authentication hashes provided by the NationStates API. If you need to add additional nations later, add them under "nations" using the same format as above.

# Manual Recruitment

`recruitment_list.py`

Generates a text file of newly founded/refounded nations, 8 to a line and comma-separated for easy use when manually recruiting. The script uses the API to verify each nation has not blocked recruitment telegrams before adding them to its list.

Configuration options can be found inside the script itself.

# RegionDict

`RegionDict.py`

Converts a region daily dump file into an `OrderedDict`-like object for easy use. `RegionDict` objects can be treated like other dictionary-like objects. Individual regions are keyed to their names (all lowercase, underscores instead of spaces). 

All shards included in the daily dump can be accessed as attributes of their individual dictionary item. Shard names are in lowercase, unlike the daily dump XML.

Example use:

```python
import RegionDict
regions = RegionDict.RegionDict()

for region in regions:
    print(region.name + ", " + region.numnations + " nations.")
```

This will print every single region in the game and their populations.

RegionDict is flexible enough to automatically include new shards as they are included in the daily dump, but will not properly handle numerical types until updated to specifically accommodate those shards.