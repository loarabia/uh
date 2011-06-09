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
# This is a library of functions that the tool actually uses to search for and 
# rename headers.
# </summary>
#-----------------------------------------------------------------------------

import os
import re

from os.path import join, splitext, normpath

class HeaderNormalizer:

    def __init__(self):

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
        with open(file,"rb") as fd:
            contents = fd.read()

            patternBytes = bytes("#include\s+\""+header+"\"" ,"utf_8")
            pattern = re.compile(patternBytes, re.IGNORECASE )
            matches = pattern.finditer(contents)

            patternBytes = bytes(r"[\r\b]+", "utf_8")
            pattern = re.compile(patternBytes, re.IGNORECASE)
            eolMatches = pattern.finditer(contents)
      
            # find the line number of the matches and puth them in an easier to maniupate state
            newLinePos = -1 
            prevNewLinePos = -1
            lineNum = 0 
            eolMatch = None
            for m in matches:
                while newLinePos < m.start():
                    try:
                        prevNewLinePos = newLinePos 
                        eolMatch = next(eolMatches)
                        newLinePos = eolMatch.end()
                        lineNum += 1
                    except StopIteration:
                        lineNum += 1
                        break
                if eolMatch.start() > m.start():
                    newLinePos = prevNewLinePos
                    
                matchesData.append( MatchData(lineNum, newLinePos, m.start(), m.end(), m.group(0)))
        return matchesData 

    def rename_headers_in_file(self, header, file):
        """
        Searches a file for all header includes that matche the passed header
        and replaces them in the file.

        The current replacement mechanism will replace the entire line so that
        the line in the file contains just the include. Any extra space or
        other not include statement data on the line will be removed.
        """
        print("Renaming Header" + header)
        matches = self.find_header_in_file(header, file)
        patternString = bytes("#include \""+header+"\"","utf_8")# + os.linesep

        with open(file, "rb+") as fd:

            for m in matches:
                fd.seek(m.start)
                fd.write(patternString)
                # pad out the rest of the line
                while fd.tell() < m.end:
                    fd.write(b" ")

class MatchData:

    def __init__(self, line, lineOffset, start, end, string):
        assert(line >= 0) 
        #assert(lineOffset >= 0) 
        assert(start >= 0) 
        assert(end >= 0) 
        assert(end - start >= 0) 
        self.line = line
        self.lineOffset = lineOffset
        self.start = start
        self.end = end
        self.string = string
        self.length = end - start
        assert(self.start - self.lineOffset >= 0) 
        self.col = self.start - self.lineOffset
        assert(self.line >= 0) 
        #assert(self.lineOffset >= 0) 
        assert(self.start >= 0) 
        assert(self.end >= 0) 
        assert(self.length >= 0) 
        assert(self.col >= 0) 
