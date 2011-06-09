#! /usr/bin/python

#-----------------------------------------------------------------------------
# <copyright file="uh.py" company="www.letstakeovertheworld.com">
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
from optparse import OptionParser
from uhnormalizer import HeaderNormalizer

USAGE = \
"""
\t%prog [options] headerFileName [dir] """

NO_ERROR = 0
BAD_ARGS = 1


def main(options, args):
    hn = HeaderNormalizer()
    candidates = hn.find_files_containing_headers(args.searchdir)
    matches = []

    # Copy the list because you are removing bad candidates and if
    # you modify the list while it is driving the loop you'll get
    # unexpected results due to python's internal indexer.
    for file in candidates[:]:
        matches = hn.find_header_in_file(args.header_filename, file)
        if( len(matches) > 1):
            print("Found %d matches in %s" % (len(matches),file))
        elif( len(matches) == 1):
            print("Found %d match in %s" % (len(matches),file))
        else:
            candidates.remove(file)

        for m in matches:
            print( "\tLine %d Start %d End %d\t\t Data %s" %(m.line, m.col, m.col+m.length, m.string))
            print()

    if options.do_rename:
        for file in candidates:
            print( "Renaming to use %s in %s" %(args.header_filename, file))
            hn.rename_headers_in_file(args.header_filename, file)


def handle_cmdline():
    """
    Parses the commandline arguments and flags and provides usage
    information.
    
    Returns a tuple of (options,UHArgumentsInstance, errorCode)
    """
    uh_args = UHArguments()
    error = NO_ERROR 

    parser = OptionParser(USAGE)
    parser.add_option("-r","--rename",
            action="store_true",
            dest="do_rename",
            default=False,
            help="renames the headers prompting for each")

    (options, cmdline_args) = parser.parse_args()

    if len(cmdline_args)== 2:
        uh_args.header_filename = cmdline_args[0]
        uh_args.searchdir = cmdline_args[1]
    elif len(cmdline_args) == 1:
        uh_args.header_filename = cmdline_args[0]
    else:
        # Only emit parse errors and exit if you're running as the
        # main module. Otherwise, we expect that this module is being
        # used elsewhere (such as a test suite) or as part of another
        # application and they may want to handle their own errors.
        if __name__ == '__main__':
            parser.error("Error: must specify 1 or 2 arguments")
        else:
            error = BAD_ARGS 

    return (options, uh_args, error)


class UHArguments:
    """
    This is purely a data container which provides a clearer way to pass
    arguments from the parser to the main function.
    """

    def __init__(self):
        """
        Initializes a newly constructed UHArguments object, setting 
        the arguments to their default values.
        
        Uh will not search if the properties are their defaults.
        """
        self.header_filename = None 
        self.searchdir = "." 


# define what to do if this is used as a standalone exe instead of a module.
if __name__ == "__main__":
    (options, uh_args, err) = handle_cmdline()  

    # if __name__ is __main__ , then the error paths should all go through
    # OptionParser's error mechanism (parser.error() ). Otherwise, this is
    # being used as a library and the err object will be populated.
    #
    # This assert catches the fact that someone added error code paths that
    # didn't obey that pattern to handle_cmdline().
    assert(err == NO_ERROR)

    main( options, uh_args)
