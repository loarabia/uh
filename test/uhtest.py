#-----------------------------------------------------------------------------
# <copyright file="uhtest.py" company="www.letstakeovertheworld.com">
# (c) Copyright Larry Olson.
# This source is subject to the New BSD License (BSD)
# See http://uh.codeplex.com/license
# All other rights reserved.
# </copyright>
# <author> Larry Olson </author>
# <date> 2.13.2010 </date>
# <summary> 
# Tests the uh option parsing and commandline handling.
# </summary>
#-----------------------------------------------------------------------------

# The modules for the project live under /src.
import sys
sys.path.append("../src")

import os
import re
import shutil
import subprocess
import unittest

import uh

class Test_UHArguments(unittest.TestCase):
    """
    Test the UHArguments class. Verifying the defaults is enough.
    Checking getters and setter is probably overkill.
    """

    def setUp(self):
        self.uh_args = uh.UHArguments()

    def testinit(self):
        self.assertTrue(self.uh_args.header_filename == None)
        self.assertTrue(self.uh_args.searchdir == ".")
    
    def testset(self):
        self.uh_args.header_filename = "foo.h"
        self.uh_args.searchdir = "/"

        self.assertTrue(self.uh_args.header_filename == "foo.h")
        self.assertTrue(self.uh_args.searchdir == "/")


class Test_handle_cmdline(unittest.TestCase):
    """
    Test the handle_cmdline function.
    """

    def test_toomanyargs(self):
        sys.argv.append("bar.h")
        sys.argv.append("/")
        sys.argv.append("aaa")

        (options, args, err) = uh.handle_cmdline()

        self.assertTrue(err)
        self.assertTrue(err == uh.BAD_ARGS)

    def test_toofewargs(self):
        (options, args, err) = uh.handle_cmdline()

        self.assertTrue(err)
        self.assertTrue(err == uh.BAD_ARGS)

    def test_defaults(self):
        sys.argv.append("bam.h")

        (options, args, err) = uh.handle_cmdline()

        self.assertFalse(err)
        self.assertFalse(options.do_rename)
        self.assertTrue(args.header_filename == "bam.h")
        self.assertTrue(args.searchdir == ".")

    def test_do_renameflag(self):
        sys.argv.append("-r")
        sys.argv.append("baz.h")

        (options, args, err) = uh.handle_cmdline()

        self.assertFalse(err)
        self.assertTrue(options.do_rename)
        self.assertTrue(args.header_filename == "baz.h")
        self.assertTrue(args.searchdir == ".")

    def tearDown(self):
        """
        Clean out the cmd line arguments after each run. uhtest.py
        should be all that is left.
        """
        while( len(sys.argv) > 1):
            sys.argv.pop()


class Test_Main(unittest.TestCase):
    """
    Test the main function itself.
    
    Uses a subprocess to execute the tool since the main method itself really
    doesn't have any noticeable side-effects except in the rename case.

    """

    def test_optional_dir(self):
        pass

    def test_header_filename(self):
        output = subprocess.check_output(["python","../src/uh.py","rootInclude.h"])
        self.assertTrue(output != b"")

        output_lines = output.split(bytes(os.linesep,"utf_8"))
        self.assertEquals( len(output_lines) , 7 )

        self.assertTrue(  \
            re.search(b"\\\\fakeproject\\\\test.c",output_lines[0]) != None) 
        self.assertTrue(re.search(b"Start 0 End 24", output_lines[1]) != None)
        self.assertTrue( \
            re.search(b"\\\\source\\\\test.c",output_lines[3]) != None) 
        self.assertTrue(re.search(b"Start 28 End 52", output_lines[4]) != None)


    def test_do_rename(self):
        pass


class TestOptions:
    """
    Create a fake Options object with object model similar to what OpionParser
    would generate
    """

    def __init__(self):
        self.do_rename = False


if __name__ == '__main__':
    unittest.main()
