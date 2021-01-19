#!/usr/bin/env python

print "Checking fonts..."

from scribus import *

print "{0}".format(scribus.getFontNames())
