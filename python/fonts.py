#!/usr/bin/env python

print "getting fonts..."

from scribus import *

print "{0}".format(scribus.getFontNames())
