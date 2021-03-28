import sys


def send(msg):
    sys.stdout.write(msg+"\n")
    sys.stdout.flush()


def log(msg):
    sys.stderr.write(str(msg)+"\n")
    sys.stderr.flush()
