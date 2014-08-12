from subprocess import Popen, PIPE, call
from os import path,kill
from signal import SIGTERM

def pid():
    proc = Popen(["pgrep", "-f", "python2 "+path.join(basedir,"pvg_standalone.py")],stdout=PIPE)
    try:
        pid=int(proc.stdout.readline())
        started=True
    except:
        started=False
        pid = None
    proc.stdout.close()
    return pid, started

pid = pid()

kill(pid,SIGTERM)
call(['python3','server.py'])
