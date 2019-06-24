from __future__ import print_function
import sys


def log(msg):
    # pass
    sys.stderr.write(str(msg)+"\n")
    sys.stderr.flush()
