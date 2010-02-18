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

    def test_finds_headers_ext_h(self):
                
        hn = HeaderNormalizer(False)
        hn.find_files_containing_headers(".\scenarios")

        rootdir = "scenarios\\fakeproject"

        self.assertTrue(join( rootdir, "rootInclude.h") in hn.candidateFiles)
        self.assertTrue(join( rootdir, "rootInclude.hpp") in hn.candidateFiles)

        self.assertTrue( join( rootdir, "Fake.txt") not in hn.candidateFiles)

        rootdir = join(rootdir, "capsheads")
        self.assertTrue(join( rootdir, "rootInclude.H") in hn.candidateFiles)
        self.assertTrue(join( rootdir, "rootInclude.HPP") in hn.candidateFiles)
        
        self.assertTrue( join( rootdir, "dummy.txt") not in hn.candidateFiles)
        

        

    def test_init(self):
        hn = HeaderNormalizer(False) 

        self.assertFalse(hn.do_rename)

        self.assertTrue(len(hn.candidateFiles) == 0)

        self.assertTrue(len(hn.header_file_extensions) == 2)
        self.assertTrue(".h" in hn.header_file_extensions)
        self.assertTrue(".hpp" in hn.header_file_extensions)

        self.assertTrue(len(hn.filetypes_containing_headers) == 4)
        self.assertTrue(".h" in hn.filetypes_containing_headers)
        self.assertTrue(".hpp" in hn.filetypes_containing_headers)
        self.assertTrue(".c" in hn.filetypes_containing_headers)
        self.assertTrue(".cpp" in hn.filetypes_containing_headers)


        hn = HeaderNormalizer(True)
        self.assertTrue(hn.do_rename)
        self.assertTrue(len(hn.candidateFiles) == 0)

        self.assertTrue(len(hn.header_file_extensions) == 2)
        self.assertTrue(".h" in hn.header_file_extensions)
        self.assertTrue(".hpp" in hn.header_file_extensions)

        self.assertTrue(len(hn.filetypes_containing_headers) == 4)
        self.assertTrue(".h" in hn.filetypes_containing_headers)
        self.assertTrue(".hpp" in hn.filetypes_containing_headers)
        self.assertTrue(".c" in hn.filetypes_containing_headers)
        self.assertTrue(".cpp" in hn.filetypes_containing_headers)


if __name__ == '__main__':
    unittest.main()
