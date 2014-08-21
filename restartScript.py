from subprocess import Popen, PIPE, call
from os import path

basedir = path.dirname(path.realpath(__file__))

Popen(["ps axf | grep server.py | grep -v grep | awk '{print \"kill -9 \" $1}' | sh"],stdout=PIPE,shell=True)

Popen(["python3 server.py"],shell=True)
