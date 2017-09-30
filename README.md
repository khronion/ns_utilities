# Endorsement Graph

This is repository contains a set of scripts that you can use to generate network graph datasets from a region's WA 
nations. It will generate a list of nodes and edges as CSV files that can quickly be imported into a program like
[Gephi](http://gephi.org/).

`generate_links.py` will use the NS API to gather live data. Due to API constraints, this is very slow, especially for
large regions. `generate_links_from_dump.py` uses the NS API dumps to quickly process large regions.