#-----------------------------------------------------------------------------
# <copyright file="uhtest.py" company="www.letstakeovertheworld.com">
# (c) Copyright Larry Olson.
# This source is subject to the New BSD License (BSD)
# See http://uh.codeplex.com/license
# All other rights reserved.
# </copyright>
# <author> Larry Olson </author>
# <date> 2.17.2010 </date>
# <summary> 
# Tests the uh option parsing and commandline handling.
# </summary>
#-----------------------------------------------------------------------------

# The modules for the project live under /src.
import sys
sys.path.append("../src")

import unittest
from os.path import join, normpath
from os import remove

from uhnormalizer import HeaderNormalizer


class Test_HeaderNormalizer(unittest.TestCase):
    """
    Test the HeaderNormalizer class.
    """

    def test_finds_header_files(self):
                
        hn = HeaderNormalizer(False)
        candidate_files = hn.find_files_containing_headers("scenarios")

        rootdir = join("scenarios","fakeproject")

        self.assertTrue(join(rootdir, "rootInclude.h") in candidate_files)
        self.assertTrue(join(rootdir, "rootInclude.hpp") in candidate_files)
        self.assertTrue(join(rootdir, "test.c") in candidate_files)

        self.assertTrue(join(rootdir, "Fake.txt") not in candidate_files)

        rootdir = join(rootdir, "capsheads")
        self.assertTrue(join(rootdir, "rootInclude.H") in candidate_files)
        self.assertTrue(join(rootdir, "rootInclude.HPP") in candidate_files)
        self.assertTrue(join(rootdir, "test.CPP") in candidate_files)
        
        self.assertTrue(join(rootdir, "dummy.txt") not in candidate_files)
        
    def test_init(self):
        hn = HeaderNormalizer(False) 

        self.assertFalse(hn.do_rename)

        self.assertTrue(len(hn.header_file_extensions) == 2)
        self.assertTrue(".h" in hn.header_file_extensions)
        self.assertTrue(".hpp" in hn.header_file_extensions)
        self.assertTrue(".c" not in hn.header_file_extensions)
        self.assertTrue(".cpp" not in hn.header_file_extensions)

        self.assertTrue(len(hn.filetypes_containing_headers) == 4)
        self.assertTrue(".h" in hn.filetypes_containing_headers)
        self.assertTrue(".hpp" in hn.filetypes_containing_headers)
        self.assertTrue(".c" in hn.filetypes_containing_headers)
        self.assertTrue(".cpp" in hn.filetypes_containing_headers)


        hn = HeaderNormalizer(True)
        self.assertTrue(hn.do_rename)

        self.assertTrue(len(hn.header_file_extensions) == 2)
        self.assertTrue(".h" in hn.header_file_extensions)
        self.assertTrue(".hpp" in hn.header_file_extensions)
        self.assertTrue(".c" not in hn.header_file_extensions)
        self.assertTrue(".cpp" not in hn.header_file_extensions)

        self.assertTrue(len(hn.filetypes_containing_headers) == 4)
        self.assertTrue(".h" in hn.filetypes_containing_headers)
        self.assertTrue(".hpp" in hn.filetypes_containing_headers)
        self.assertTrue(".c" in hn.filetypes_containing_headers)
        self.assertTrue(".cpp" in hn.filetypes_containing_headers)

    def test_find_header_in_file_included_once(self):
        hn = HeaderNormalizer(False)

        file1 = join("scenarios","fakeproject","source","test.c")
        file2 = join("scenarios","fakeproject","test.c")
        header = "rootInclude.h"

        matches = hn.find_header_in_file(header,file1)
        self.assertEquals(len(matches), 1)

        self.assertEquals(matches[0].start, 28)
        self.assertEquals(matches[0].end, 52)
        self.assertEquals(matches[0].length, 24)
        self.assertEquals(matches[0].string, b"#include \"rootInclude.H\"")

        matches = hn.find_header_in_file(header,file2)
        self.assertEquals(len(matches), 1)

        self.assertEquals(matches[0].start, 0)
        self.assertEquals(matches[0].end, 24)
        self.assertEquals(matches[0].length, 24)
        self.assertEquals(matches[0].string, b"#include \"rootInclude.h\"")

    def test_find_header_in_file_include_multiple(self):
        hn = HeaderNormalizer(False)

        header ="header1.h"
        file = join("scenarios","fakeproject","test.c")

        matches = hn.find_header_in_file(header,file)

        self.assertEquals(len(matches),2)
        self.assertEquals(matches[0].string, b"#include \"header1.H\"")
        self.assertEquals(matches[0].start, 26)
        self.assertEquals(matches[1].string, b"#include \"header1.h\"")
        self.assertEquals(matches[1].start, 98)

    def test_rename_headers_in_file(self):
        header = "header1.h"
        file = join("scenarios","fakeproject","test.c")
        fileCopy = join("scenarios","fakeproject","testCopy.c")

        fd = open(file,"rb")
        contents = fd.read()
        fd.close()

        tfd = open(fileCopy, "wb")
        tfd.write(contents)
        tfd.close()

        hn = HeaderNormalizer(True) 
        hn.rename_headers_in_file(header, fileCopy)

        matches = hn.find_header_in_file(header, fileCopy)
        remove(fileCopy)

        self.assertEquals(len(matches),2)
        self.assertEquals(matches[0].string, b"#include \"header1.h\"")
        self.assertEquals(matches[0].start, 26)
        self.assertEquals(matches[1].string, b"#include \"header1.h\"")
        self.assertEquals(matches[1].start, 98)

    def test_rename_headers_in_file_extra_spaces(self):
        header = "aaaaaaaaaa.h"
        file = join("scenarios","fakeproject","test.c")
        fileCopy = join("scenarios","fakeproject","testCopyCopy.c")

        fd = open(file,"rb")
        contents = fd.read()
        fd.close()

        tfd = open(fileCopy, "wb")
        tfd.write(contents)
        tfd.close()

        hn = HeaderNormalizer(True) 
        matches = hn.find_header_in_file(header,fileCopy)
        self.assertEquals(len(matches),1)
    
        hn.rename_headers_in_file(header, fileCopy)
        matches = hn.find_header_in_file(header, fileCopy)
        self.assertEquals(len(matches),1)
       
        # check that the include line doesn't have any extra cruft
        tfd = open(fileCopy, "rb")
        tfd.seek(matches[0].end)
        data = tfd.read(5)
        self.assertTrue(data != b"aa.h\"")

        tfd.close()
        #remove(fileCopy)


if __name__ == '__main__':
    unittest.main()
