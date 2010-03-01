#-----------------------------------------------------------------------------
# <copyright file="uhtestrunner.py" company="www.letstakeovertheworld.com">
# (c) Copyright Larry Olson.
# This source is subject to the New BSD License (BSD)
# See http://uh.codeplex.com/license
# All other rights reserved.
# </copyright>
# <author> Larry Olson </author>
# <date> 2.28.2010 </date>
# <summary> 
# Combines all of the suites together into a single location to be run.
# </summary>
#-----------------------------------------------------------------------------

import unittest
import uhnormalizertest
import uhtest

uh_suite = unittest.TestSuite()
loader = unittest.TestLoader()

uh_suite.addTests(loader.loadTestsFromModule(uhtest))
uh_suite.addTests(loader.loadTestsFromModule(uhnormalizertest))

if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(uh_suite)
