#!/usr/bin/python
# -*- coding: utf-8 -*-
# filesystem operations

def writeFile(filename, content):
    """ write content passed as a variable to a file
        Args:
            filename -- the filename to write to (string)
            content  -- content to be written to the file (string)
        Returns:
            status   -- True if file was successfully writen, else False
            errmsg   -- None if write succeeded, else an error message (string)
    """
    try:
        with open(filename, 'w') as f:
            f.write(content)
        return True, None
    except IOError:
        errormsg = 'Error: Could not write %(file)s\n' % { "file": filename }
        errormsg += 'Make sure the path is correct and your user has write permissions for it.'
        return False, errormsg