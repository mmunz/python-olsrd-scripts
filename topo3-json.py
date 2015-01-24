#!/usr/bin/python
# -*- coding: utf-8 -*-
# this script generates json output suitable for cytoscape.js by parsing and
# modifying the output of the olsrd dotdraw plugin.
# The raw output from dotdraw plugin is rendered using graphviz/neato to a text
# file to get the nodes coordinates on the canvas.

import json
import os
import socket
import sys
import time

libPath = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'lib')
sys.path.insert(1, libPath)
from fs import writeFile
from olsrd_dotdraw import getDot, parseDot 
configPath = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'config')
sys.path.append(configPath)
from config import config

### Configuration - see config/config.py
dotDrawHost = config["dotdraw"]["host"]
dotDrawPort = config["dotdraw"]["port"]
workingDir = config["topo3"]["outputPath"]
dotolsr = workingDir + '/topo-olsr-raw.dot'
outputFile = workingDir + '/topo3.json'
hostsFile = config["nameservice"]["hostsFile"]
# hosts that do peering via IC-VPN. They have a ot of HNAs, so we want to be able
# to filter these in the graph. Set to False to disable this feature.
ICVPNHosts = config["topo3"]["ICVPNHosts"]


def format_cytoscape(topo):
    """ Format output for cytoscape.js
    
        Args:
            topo -- a topology table returned by olsrd_dordraw.parseDot() (dict)
        Returns:
            ret -- formatted data for cytoscape.js (dict)
    """
    ret = {
        "nodes": [],
        "edges": []
    }
    for node in topo["nodes"]:
        data = {
            "data": {
                "id": node["id"],
                "label": node["label"],
            },
            "position": {
                "x": node["x"],
                "y": node["y"]
            }
        }
        if "type" in node:
            data["data"]["type"] = node["type"]
        if "group" in node:
            data["data"]["group"] = node["group"]
            
        ret["nodes"].append(data)
        
    for edge in topo["edges"]:
        data = {
            "data": {
                "id": edge["id"],
                "source": edge["source"],
                "target": edge["target"],
                "color": edge["color"],
                "label": edge["label"]
            }
        }
        if "group" in edge:
            data["data"]["group"] = edge["group"]
        ret["edges"].append(data)
        
    return ret

def get_metainfo():
    """ Get a dict of meta information
    
        Returns:
            meta -- meta information (dict)
            
        Example output:
            {
                'generated_on': 1422135974,
                'generated_by': 'localhost'
            }
    """
    meta = {
        "generated_on": int(time.time()),
        "generated_by": socket.gethostname()
    }
    return meta
    

def main():
    """ main function: get infos and write them to a file """
    
    status, dotRaw = getDot(dotDrawHost, dotDrawPort)
    if status == False:
        print('Error getting data from olsrd dotdraw plugin.')
        print(dotRaw)
        exit()
        
    out = parseDot(dotRaw, hostsFile=hostsFile)

    # Mark icvpn targets so we can filter them out in the graph
    if len(ICVPNHosts) > 0:
        icvpnNetworks = []
        for edge in out["edges"]:
            if edge['source'] in ICVPNHosts and edge["label"] == "HNA":
                edge["group"] = "icvpn"
                edge['color'] == 'blue'
                icvpnNetworks.append(edge["target"])

        # Mark all nodes which are hnas for icvpn:
        for node in out["nodes"]:
            if node["id"] in icvpnNetworks:
                #print("mark node " + node['id'] + " as icvpn")
                node['group'] = "icvpn"
    
    # now reformat the output to a format cytoscape undestands
    out = {
        "cyto": format_cytoscape(out),
        "meta": get_metainfo()
    }
    
    status, errmsg = writeFile(outputFile, json.dumps(out))
    
    if status:
        print('Update of %s successful.' % outputFile)
    else:
        print ('Update failed.')
        print(errmsg)
        

if __name__ == "__main__":
    main()