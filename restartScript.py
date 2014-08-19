from subprocess import Popen, PIPE, call
from os import path, kill
from signal import SIGTERM

basedir=path.dirname(path.realpath(__file__))

def pid():
    proc = Popen(["pgrep", "-f", "python3 "+path.join(basedir,"server.py")],stdout=PIPE)
    try:
        pid=int(proc.pid)
    except:
        pid = None
    proc.stdout.close()
    return pid

pid = pid()

try:
    kill(pid,SIGTERM)
    call(['python3','server.py'])
except KeyboardInterrupt:
    pass
