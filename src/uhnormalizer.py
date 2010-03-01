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

        self.header_file_extensions = [".h",".hpp"]

        # Copy the list instead of passing a reference
        self.filetypes_containing_headers = self.header_file_extensions[:]
        self.filetypes_containing_headers.append(".cpp")
        self.filetypes_containing_headers.append(".c")

    def find_files_containing_headers(self, searchdir):
        """
        Searches for all C and CPP source and header files beneath searchdir.
        Each file is added to a candidate list of files stored on the object
        as self.candidate_files as a side effect of calling this method. 
        
        returns a list of candidate files
        """
        candidate_files = []
        
        for root, dirs, files in os.walk(searchdir):
            
            for file in files:
                ext = splitext(file)[1]
                if( ext.lower() in self.filetypes_containing_headers):
                    candidate_files.append( normpath(join(root,file)))

        return candidate_files

    def find_header_in_file(self, header, file):
        """
        Searches a file for all header includes that match the passed header.

        Returns a list of MatchData objects describing the location of the
        header lines.
        """
        matchesData = []

        # Work in Binary mode to bypass the tweaking of newlines that python
        # does on Windows
        fd = open(file,"rb")
        contents = fd.read()
        fd.close()

        patternString = "#include\s+\""+header+"\"" 
        patternBytes = bytes(patternString,"utf_8")
        pattern = re.compile(patternBytes, re.IGNORECASE )
        matches = pattern.finditer(contents)

        for m in matches:
            matchesData.append( MatchData(m.start(), m.end(), m.group(0)))

        return matchesData 

    def rename_headers_in_file(self, header, file):
        """
        Searches a file for all header includes that matche the passed header
        and replaces them in the file.

        The current replacement mechanism will replace the entire line so that
        the line in the file contains just the include. Any extra space or
        other not include statement data on the line will be removed.
        """
        matches = self.find_header_in_file(header, file)
        patternString = bytes("#include \""+header+"\"","utf_8")# + os.linesep

        fd = open(file, "rb+")

        for m in matches:
            fd.seek(m.start)
            fd.write(patternString)
            # pad out the rest of the line
            while fd.tell() < m.end:
                fd.write(b" ")

        fd.close()


class MatchData:

    def __init__(self, start, end, string):
        self.start = start
        self.end = end
        self.string = string
        self.length = end - start
