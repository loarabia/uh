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
        search_dir = os.path.join("scenarios","fakeproject","source")

        output = runTool("rootInclude.h",search_dir)
        self.assertTrue(output != b"")

        output_lines = output.split(bytes(os.linesep,"utf_8"))
        self.assertEquals( len(output_lines), 4)

        #matchStr = bytes(os.path.join("source","test.c"),"utf_8")
        matchStr = b"source.test\.c"
        self.assertNotEqual( re.search(matchStr ,output_lines[0]) ,None) 
        self.assertTrue(re.search(b"Start 28 End 52", output_lines[1]) != None)


    def test_header_filename(self):
        output = runTool("rootInclude.h")
        self.assertNotEqual(output , b"")

        output_lines = output.split(bytes(os.linesep,"utf_8"))
        self.assertEqual( len(output_lines) , 7 )

        #matchStr = bytes( os.path.join("fakeproject","test.c"),"utf_8")
        # fakeproject/test.c
        matchStr = b"fakeproject.test\.c"
        self.assertNotEqual(re.search(matchStr,output_lines[0]), None) 
        self.assertNotEqual(re.search(b"Start 0 End 24", output_lines[1]),None)

        #matchStr = bytes(os.path.join("source","test.c"),"utf_8")
        # source/test.c
        matchStr = b"source.test\.c"
        self.assertNotEqual(re.search(matchStr, output_lines[3]),  None) 
        self.assertNotEqual(re.search(b"Start 28 End 52",output_lines[4]),None)


    def test_do_rename(self):
        # Be careful working with this test case and  test_header_filename
        # test_header_filename runs from the test directory and therefore if
        # this test directory (tempscenarios) isn't cleaned up, it will throw
        # off test_header_filename because that test is searching from the 
        # current working directory which should in this case be uh/test.
        shutil.copytree("scenarios","tempscenarios") 
        output = runTool("rootInclude.h","tempscenarios",rename=True)

        origFile = os.path.join("scenarios","fakeproject","source","test.c")
        newFile = os.path.join("tempscenarios","fakeproject","source","test.c")
        origFd = open(origFile, "r")
        newFd = open(newFile, "r")

        origContents = origFd.read()
        newContents = newFd.read()
        origFd.close()
        newFd.close()

        shutil.rmtree("tempscenarios")

        self.assertNotEqual(origContents, newContents)

        oldPattern = "rootInclude\.H"
        newPattern = "rootInclude\.h"
        self.assertEqual( re.search(oldPattern, newContents), None)
        self.assertNotEqual( re.search(newPattern, newContents), None)

def runNativeTool(header_file, search_dir=None, rename=False):
    """
    This runs the native version of the command and returns the output string.
    """
    tool = os.oath.join("..","src","uh")

    commandLine = [tool, header_file, search_dir]
    assrt(commandLine != None)
    commandLine = fixupCommandLine(commandLine, header_file, search_dir)
    assrt(commandLine != None)
    return runCommandLine(commandLine, "")

def runTool(header_file, search_dir=None, rename=False):
    """
    This runs the command and returns the output string.

    The purpose behind this method is to abstract away the differences between
    Mac, Windows, and Linux as far as the name of the tool.
    """
    command = "python"
    altCommand = "python3"
    tool = os.path.join("..","src","uh.py")

    commandLine = [command, tool, header_file, search_dir]
    commandLine = fixupCommandLine(commandLine, search_dir, rename)
    return runCommandLine(commandLine, altCommand)

def fixupCommandLine(command_line, search_dir, rename):
    if search_dir == None:
        command_line.pop()
    
    if rename:
        command_line.insert(2,"-r")

    return command_line

def runCommandLine(command_line, altCommand):
    try:
        result = subprocess.check_output(command_line, stderr=subprocess.PIPE)
    except:
        command_line[0] = altCommand
        result = subprocess.check_output(command_line, stderr=subprocess.PIPE)
    return result

class TestOptions:
    """
    Create a fake Options object with object model similar to what OpionParser
    would generate
    """

    def __init__(self):
        self.do_rename = False


if __name__ == '__main__':
    unittest.main()
