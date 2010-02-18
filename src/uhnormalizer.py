#-----------------------------------------------------------------------------
# <copyright file="uhnormalizer.py" company="www.letstakeovertheworld.com">
# (c) Copyright Larry Olson.
# This source is subject to the New BSD License (BSD)
# See http://uh.codeplex.com/license
# All other rights reserved.
# </copyright>
# <author> Larry Olson </author>
# <date> 2.13.2010 </date>
# <summary> 
# Handles the invocation of the update header tool by parsing options and
# executing the appropriate renaming functionality.
# </summary>
#-----------------------------------------------------------------------------

import os
import re

from os.path import join, splitext, normpath

class HeaderNormalizer:

    def __init__(self, do_rename):
        self.do_rename = do_rename

        self.candidate_files = []
        self.header_file_extensions = [".h",".hpp"]

        # Copy the list instead of passing a reference
        self.filetypes_containing_headers = self.header_file_extensions[:]
        self.filetypes_containing_headers.append(".cpp")
        self.filetypes_containing_headers.append(".c")

    def find_files_containing_headers(self, searchdir):
        for root, dirs, files in os.walk(searchdir):
            
            for file in files:
                ext = splitext(file)[1]
                if( ext.lower() in self.filetypes_containing_headers):
                    self.candidate_files.append( normpath(join(root,file)))
       
