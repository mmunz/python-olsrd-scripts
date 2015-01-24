#!/usr/bin/python
# some functions to get info from olsrd-jsoninfo

import os
import socket
import json
import time

def getTopo(host, port):
    """ Get the topology information from jsoninfo and return a dictionary
        Args:
            host -- ip or hostname of a host where olsrd jsoninfo is reachable (string)
            port -- port of the jsoninfo plugin (int)
        Returns:
            topo -- Dictionary containing the topology information (dict)
    """
    response = ''
    try:
        s = socket.socket()
        s.settimeout(10)
        s.connect((host, port))
        s.send('/topology')
        buffer = s.recv(4096)
        while buffer:
            response += buffer
            buffer = s.recv(4096)
    except socket.error, e:
        print 'Error, could not connect to %(host)s:%(port)s' % {"host": host, "port": port}
        print 'Make sure the host is reachable and jsoninfo is running there.'
        exit()

    topo = {}
    if response != '':
        topo = json.loads(response)['topology']
    else:
        print 'Could not get any info from jsoninfo on %(host)s:%(port)s' % {"host": host, "port": port}
        print 'Does it accept connections from this host?'
        exit()
    return topo

def getHNA(host, port):
    """ Get the hna information from jsoninfo and return a dictionary """
    response = ''
    try:
        s = socket.socket()
        s.settimeout(10)
        s.connect((host, port))
        s.send('/hna')
        buffer = s.recv(4096)
        while buffer:
            response += buffer
            buffer = s.recv(4096)
    except socket.error, e:
        print 'Error, could not connect to %(host)s:%(port)s' % {"host": host, "port": port}
        print 'Make sure the host is reachable and jsoninfo is running there.'
        exit()

    hna = {}
    if response != '':
        hna = json.loads(response)['hna']
    else:
        print 'Could not get any info from jsoninfo on %(host)s:%(port)s' % {"host": host, "port": port}
        print 'Does it accept connections from this host?'
        exit()
    return hna

def uniqueIPs(topo):
    """ Iterate over a topology dictionary and create an array of unique node ips """
    ips = []
    for t in topo:
        ip = t['destinationIP']
        if not ip in ips:
            ips.append(ip)
    return ips

def inetHNA(topo):
    """ Iterate over a topology dictionary and create an array with all internet gateways """
    gws = []
    for t in topo:
        dest = t['destination']
        if dest == '0.0.0.0':
            gws.append(t['gateway'])
    return gws


