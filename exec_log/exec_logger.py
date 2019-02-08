#!/usr/bin/python
from sys import exit
import subprocess
import time
import linuxcnc

s = linuxcnc.stat()
out_filepath = '/home/{USER}/linuxcnc/configs/{CONFIG_NAME}/exec_log.csv'
state = 0
start_time = 0
finish_time = 0

# main cycle
while 1:
    # check program data every 5 seconds
    time.sleep(5)

    # check for the linuxcnc process state
    if 1 > subprocess.Popen(['ps','-C','linuxcnc'], stdout=subprocess.PIPE).communicate()[0].count('linuxcnc'):
        # exit if no linuxcnc process found
        exit(1)

    try:
        # update lcnc state data
        s.poll()
    except linuxcnc.error, detail:
        # exit if any lcnc error
        exit(1)
    else:
        if state == 0:
          if s.spindle_enabled > 0:
            start_time = int(time.time())
            state = 1
        elif state == 1:
          if s.spindle_enabled == 0:
            stop_time = int(time.time())
            # write new data to the output file
            f = open(out_filepath, 'a')
            f.write(str(s.file) + ',' + str(start_time) + ',' + str(stop_time) + '\n')
            f.flush()
            f.close()
            state = 0
        else:
          state = 0
exit(0)
