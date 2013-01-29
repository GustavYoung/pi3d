from __future__ import absolute_import, division, print_function, unicode_literals

VERSION = '0.06'

STARTUP_MESSAGE = """

  Pi3D module - version %(version)s

  Copyright (c) Tim Skillman, 2012-2013
  Copyright (c) Patrick Gaunt, 2012-2013
  Copyright (c) Tom Swirly, 2012-2013

  Updates available from www.github.com/tipam/pi3d
""" % {'version': VERSION}

VERBOSE = False

# Pick up our constants extracted from the header files with prepare_constants.py
from pi3d.constants.egl import *
from pi3d.constants.gl2 import *
from pi3d.constants.gl2ext import *
from pi3d.constants.gl import *

# Define some extra constants that the automatic extraction misses.
EGL_DEFAULT_DISPLAY = 0
EGL_NO_CONTEXT = 0
EGL_NO_DISPLAY = 0
EGL_NO_SURFACE = 0
DISPMANX_PROTECTION_NONE = 0

# Lastly, load the libraries.
def _load_library(name):
  """Try to load a shared library, report an error on failure."""
  try:
    import ctypes
    return ctypes.CDLL('lib%s.so' % name)
  except:
    from echomesh.util import Log
    Log.logger(__name__).error("Couldn't load library %s" % name)

bcm = _load_library('bcm_host')
opengles = _load_library('GLESv2')
openegl = _load_library('EGL')

