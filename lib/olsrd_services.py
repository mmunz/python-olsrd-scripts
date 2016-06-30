#!/usr/bin/python
# -*- coding: utf-8 -*-

# read a services file written by the olsrd_nameservice plugin and returns
# a dict with its lines

import os
import requests
import urllib3

def getServices(uri, verifySSL=True):
    """ read services from a file written by the olsrd_services plugin
    
        Args:
            uri -- url or full path to the services file (string)
            verifySSL -- Enable SSl certificate verification when the uri is a https url (bool)
        Returns:
            topo -- Dictionary containing known services (dict)
    """
    
    if not uri or uri == '':
        errmsg = "no uri given, cannot get services"
        return False, errmsg

    ret = []

    if uri.startswith("http://") or uri.startswith("https://"):
        urllib3.disable_warnings()
	r = requests.get(uri, verify=verifySSL)
        if r.status_code == 200:
            ret = r.text.splitlines()
        else:
            errmsg = "Could not download %(uri)s, the error code was %(ec)s" % { "uri": uri, "ec": r.status_code }
    else:
        if not os.access(uri, os.R_OK):
            errmsg = 'Error: Could not read %(file)s.' % { "file": uri }
            errmsg += 'Make sure the path is correct and your user has read and write permissions.'
            return False, errmsg
        with open(uri, 'r') as services:
            ret = services.read().splitlines()
            services.closed

    return ret, None
