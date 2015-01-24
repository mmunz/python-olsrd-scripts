#!/usr/bin/python
# -*- coding: utf-8 -*-

# Generate basic statistics in json format containing:
# - nodes count
# - list of node ips
# - links count
# - internet gateway count
#
# To use this script you have to set some variables - see below.
#
# The number are received by parsing the output of the olsr
# jsoninfo plugin.
#
# example output written to the output file:
#
# {
#    "inetgws": 2, 
#    "nodes": {
#        "count": 3, 
#        "ips": [
#            "10.0.0.1", 
#            "10.0.0.2", 
#            "10.0.0.3", 
#        ]
#    }, 
#    "links": 6
# }

import os
import json
import sys

libPath = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'lib')
configPath = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'config')
sys.path.insert(1, libPath)
sys.path.append(configPath)
from olsrd_jsoninfo import getTopo, uniqueIPs, inetHNA, getHNA
from fs import writeFile
from config import config

### Configuration: see config/config.py
 
host = config["jsoninfo"]["host"]
port = config["jsoninfo"]["port"]
outputPath = config["stats"]["outputPath"]
outputFile = os.path.join(outputPath, "olsr-stats.json")


def main():
    topo = getTopo(host, port)
    nodes = uniqueIPs(topo)
    countNodes = len(nodes)
    countLinks = len(topo)
    hna = getHNA(host, port)
    countInetHNA = len(inetHNA(hna))

    data = {
	'nodes' : {
            "count": countNodes,
            "ips" : nodes
        },
	'links' : countLinks,
        'inetgws': countInetHNA
    }
    
    data = json.dumps(data, indent=4) + "\n"

    status, errmsg = writeFile(outputFile, data)
    
    if status:
        print 'Update of %(file)s successful. %(nodes)s nodes, %(links)s links, %(inetgws)s internet gateways' % { "file": outputFile, "nodes": countNodes, "links": countLinks, "inetgws": countInetHNA }
    else:
        print ('Update failed.')
        print(errmsg)

if __name__ == "__main__":
    main()
