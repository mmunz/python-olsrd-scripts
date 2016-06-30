#!/usr/bin/python
# -*- coding: utf-8 -*-

# reads a olsrd hosts file (written by nameservive plugin) and returns a
# dictionary with key id and value hostname

import os
import urllib3
import requests

def readHostsFile(uri, verifySSL=True):
    """ Load the hosts file
        Args:
            uri   -- full path or URL to a hosts file written by olsrd (string)
        Returns:
            ret -- a dictionary with ip -> hostname mappings (dict) if the file
                   was readable. Else returns False.
    """

    if uri.startswith("http://") or uri.startswith("https://"):
        urllib3.disable_warnings()
        r = requests.get(uri, verify=verifySSL)
        if r.status_code == 200:
            ret = {}
            for line in r.text:
                if not line.startswith(("#", "\n", "127.0.0.1", "::1")):
                    linesplit = line.split()
                    if len(linesplit) > 1:
                        id = linesplit[0]
                        hostname = linesplit[1]
                        ret[id] = hostname
        else:
            errmsg = "Could not download %(uri)s, the error code was %(ec)s" % { "uri": uri, "ec": r.status_code }
    else:
        if not os.access(uri, os.R_OK):
            print 'Error: Could not read %(file)s.' % { "file": uri }
            print 'Make sure the path is correct and your user has read permissions.'
            return False

        ret = {}
        with open(uri, 'r') as f:
            for line in f:
                if not line.startswith(("#", "\n", "127.0.0.1", "::1")):
                    linesplit = line.split()
                    if len(linesplit) > 1:
                        id = linesplit[0]
                        hostname = linesplit[1]
                        ret[id] = hostname
            f.closed
        
    return ret
