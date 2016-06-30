# python-olsrd-scripts
Some scripts to get and parse (some, not all) infos from various olsrd plugins (jsoninfo, nameservice, dotdraw)

## Scripts

### olsrd-stats.py
Reads olsrd_jsoninfo output and writes some basic statistics in json format containing:
- node count
- list of node ips
- link count
- internet gateway count

### ffapi-update-nodes.py
Updates a [ffapi](https://github.com/freifunk/api.freifunk.net) file with current number of nodes. Also updates the list of services available in the mesh.

### topo3-json
Creates json output to be used with [TOPO3](https://github.com/mmunz/TOPO3).

## Libs

The lib/ folder contains various libs for getting info from olsrd plugins.

## Configuration

All scripts are configured using config/config.py. You need to create that file by copying config/config.example.py

## Requires
- python-pygraphviz

## Status
"Works for me."

