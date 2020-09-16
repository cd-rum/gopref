#!/usr/bin/env python

import os
import sys

from dotmap import DotMap

def main(argv):
  id = argv[1]
  col = DotMap()
  col.black = '0,0,0,100'
  for k, v in col.items():
    print k
    print v
  print "[pdf] tested {0}".format(id)
  return 0

if __name__ == '__main__': main(sys.argv)