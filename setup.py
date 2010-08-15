#-----------------------------------------------------------------------------
# <copyright file="setup.py" company="www.letstakeovertheworld.com">
# (c) Copyright Larry Olson.
# This source is subject to the New BSD License (BSD)
# See http://uh.codeplex.com/license
# All other rights reserved.
# </copyright>
# <author> Larry Olson </author>
# <date> 8.14.2010 </date>
# <summary> 
# setup script to install the uh.py tool
# </summary>
#-----------------------------------------------------------------------------
from distutils.core import setup
setup(name='uh',
    version='1.0',
    package_dir={'': 'src'},
    packages=[''],
    scripts=['src/uh.py']
    )

