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
from os.path import join

from uhnormalizer import HeaderNormalizer


class Test_HeaderNormalizer(unittest.TestCase):
    """
    Test the HeaderNormalizer class.
    """

    def test_finds_header_files(self):
                
        hn = HeaderNormalizer(False)
        candidate_files = hn.find_files_containing_headers(".\scenarios")

        rootdir = "scenarios\\fakeproject"

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

    def test_find_header_in_file(self):
        hn = HeaderNormalizer(False)

        file1 = "scenarios\\fakeproject\\source\\test.c"
        file2 = "scenarios\\fakeproject\\test.c"
        header = "rootInclude.h"

        (start, len) = hn.find_header_in_file(header,file1)

        self.assertEquals(start, 11)
        self.assertEquals(len,  13)

        (start, len) = hn.find_header_in_file(header,file2)

        self.assertEquals(start,  11)
        self.assertEquals(len,  13)

if __name__ == '__main__':
    unittest.main()
