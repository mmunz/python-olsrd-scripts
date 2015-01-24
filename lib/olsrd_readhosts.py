#!/usr/bin/python
# -*- coding: utf-8 -*-

# reads a olsrd hosts file (written by nameservive plugin) and returns a
# dictionary with key id and value hostname

import os

def readHostsFile(hostsFile):
    """ Load the hosts file
        Args:
            hostsFile   -- full path to a hosts file written by olsrd (string)
        Returns:
            ret -- a dictionary with ip -> hostname mappings (dict) if the file
                   was readable. Else returns False.
    """
    if not os.access(hostsFile, os.R_OK):
        print 'Error: Could not read %(file)s.' % { "file": hostsFile }
        print 'Make sure the path is correct and your user has read permissions.'
        return False
    
    ret = {}
    with open(hostsFile, 'r') as f:
        for line in f:
            if not line.startswith(("#", "\n", "127.0.0.1", "::1")):
                linesplit = line.split()
                if len(linesplit) > 1:
                    id = linesplit[0]
                    hostname = linesplit[1]
                    ret[id] = hostname
        f.closed
        
    return ret
