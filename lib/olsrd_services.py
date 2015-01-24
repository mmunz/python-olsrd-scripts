#!/usr/bin/python
# -*- coding: utf-8 -*-

# read a services file written by the olsrd_nameservice plugin and returns
# a dict with its lines

import os

def getServices(filename):
    """ read services from a file written by the olsrd_services plugin
    
        Args:
            filename -- full path to the services file (string)
        Returns:
            topo -- Dictionary containing the topology information (dict)
    """
    
    if not filename or filename == '':
        errmsg = "no filename given, cannot get services"
        return False, errmsg

    ret = []
    if not os.access(filename, os.R_OK):
        errmsg = 'Error: Could not read %(file)s.' % { "file": filename }
        errmsg += 'Make sure the path is correct and your user has read and write permissions.'
        return False, errmsg
    with open(filename, 'r') as services:
        ret = services.read().splitlines()
        services.closed
    return ret, None