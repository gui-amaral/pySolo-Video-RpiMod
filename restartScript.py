from subprocess import call

call(["ps axf | grep server.py | grep -v grep | awk '{print \"kill -9 \" $1}' | sh"],shell=True)

call(["python3 server.py"],shell=True)
