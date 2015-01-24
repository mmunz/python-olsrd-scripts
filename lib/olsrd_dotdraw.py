#!/usr/bin/python
# -*- coding: utf-8 -*-
# functions to get info from olsrd-dotdraw plugin

import os
import sys
import socket
import re
import pygraphviz as pgv

libPath = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), 'lib')
sys.path.insert(1, libPath)
from olsrd_readhosts import readHostsFile

def renderDotPlain(dotRaw):
    """ render olsrd_dotdraw output using graphviz plain output format
        Args:
            dotRaw   -- raw output from olsrd_dotdraw (string)
        Returns:
            ret      -- The rendered layout in plain format (string)
    """
    G=pgv.AGraph(dotRaw,
        strict=False,
        directed=True,
    );
    # these settings don't seem to work - > investigate
    # until then make the multiplier in parseDot higher (300 instead of 72)
    # to get a larger canvas
    G.graph_attr["size"]= "16,10"
    G.graph_attr.update(n="4")
    G.graph_attr.update(rowsize="2")
    G.layout()
    ret = G.draw(format='plain')
    return ret

def parseDot(dotRaw, hostsFile=None):
    """ Parses dotdraw raw output into a list of dicts
        Args:
            dotRaw    -- dotRaw input (string)
            hostsFile -- if given, try to resolve ips to hostnames using this
                         hosts file and use the hostnames as label
        Returns:
            ret      -- list of dictionaries containing nodes and edges (list)
            
        Format, see http://www.graphviz.org/doc/info/output.html#d:plain
        Node: name x y width height label style shape color fillcolor
        Edge: tail head n x1 y1 .. xn yn [label xl yl] style color
        
        Example output:
        
        {
            'nodes': [
                {
                    'y': 212,
                    'x': 385,
                    'shape': 'box',
                    'id': '10.0.0.1',
                    'label': '10.0.0.1'
                    'type': 'HNA'
                },
                {
                    'y': 235,
                    'x': 352,
                    'shape': 'ellipse',
                    'id': '10.0.0.2',
                    'label': 'testnode.olsr'
                }
            ],
             'edges': [
                {
                    'color': 'green',
                    'source': '10.0.0.1',
                    'label': '1.000',
                    'id': '10.0.0.1-10.0.0.2',
                    'target': '10.0.0.2'
                },
                {
                    'color': 'green',
                    'source': '10.0.0.2',
                    'label': '1.000',
                    'id': '10.0.0.2-10.0.0.1',
                    'target': '10.0.0.1'
                },
            ]
        }
        
        id is in the format <source>-<target>
        
        label in the output is either the link quality metric or in case the
        edge is an HNA the string "HNA".
        
        color is computed from the link quality metric.
        
    """
    hosts = None
    if hostsFile:
        hosts = readHostsFile(hostsFile)
        
    out = {
        "nodes": [],
        "edges": []
    }
    lines = renderDotPlain(dotRaw).split("\n")
    for l in lines:
        ldict = l.split(" ") 

        if ldict[0] == 'graph':
            pass
        elif ldict[0] == 'node':
            id = ldict[1].strip('"')
            # dotdraw uses inches. convert to pixel by multiplying with 72
            # size setting doesn't work for the graph - so use 300 as multiplier
            # to produce a larger graph
            data = {
                "id"    : id,
                "label" : id,
                "x"     : int(float(ldict[2]) * 300),
                "y"     : int(float(ldict[3]) * 300),
                "shape" : ldict[8]
            }
            # add a type depending on shape
            # diamond = HNA
            # ellipse = normal router
            if data["shape"] == "diamond":
                data["type"] = "HNA"
            
            # resolve host names
            if hosts and id in hosts:
                data["label"] = hosts[id]
                
            out["nodes"].append(data)

        if ldict[0] == 'edge':
            lq = False

            try:
                lq = float(ldict[12].strip('"'))
                lq = round(lq, 3)
            except ValueError:
                lineColor = '#ccc'

            if lq:
                if lq < 2:
                    lineColor = "green"
                elif lq < 4:
                    lineColor = "orange"
                else:
                    lineColor = "red"
                    
            source = ldict[1].strip('"')
            target = ldict[2].strip('"')
            
            data = {
                "id": '%s-%s' % (source, target),
                "source": source,
                "target": target,
                "color": lineColor
            }
            if lq:
                data["label"] = "{0:1.3f}".format(lq)
            else:
                data["label"] = "HNA"




            out["edges"].append(data)

    return out

def getDot(host, port):
    """ Get the output from olsrd_dotdraw plugin and return it
        Args:
            hostname -- Ip address or hostname of a host with olsrd_dotdraw (string)
            port     -- Port number to connect to (int)
        Returns:
            status   -- True if connection was successful, else False
            ret      -- dotdraw output or errormsg if the request failed (string)
    """
    ret = ''
    try:
        response = ''
        s = socket.socket()
        s.settimeout(10)
        s.connect((host, port))
        buffer = s.recv(4096)
        while buffer:
            response += buffer
            buffer = s.recv(4096)
            
    except socket.error, e:
        errmsg = 'Error, could not connect to %(host)s:%(port)s\n' % {"host": host, "port": port}
        errmsg += 'Error code: %s - %s\n' % (e.errno, e.strerror)
        errmsg += 'Make sure the host is reachable and the dotdraw plugin is running there.'
        return False, errmsg

    # sometimes dotdraw returns two graphs - thats why we filter only for the
    # first here
    ret = re.search('digraph(.*?)}', response, flags=re.DOTALL).group(0)
    return True, ret

