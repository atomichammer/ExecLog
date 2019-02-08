# ExecLog
Log programs on LinuxCNC
## How to install
0. Put the folder exec_log to your /home/{USER}/linuxcnc/configs/{CONFIG_NAME}/
1. Make *.py files executable (chmod u+x *.py)
2. Modify your {CONFIG_NAME}.ini
```ini
[AXIS]
...
EMBED_TAB_NAME = Exec Log
EMBED_TAB_COMMAND = halcmd loadusr -Wn gladevcp gladevcp -c gladevcp -x {XID} -u ./exec_log/exec_log.py ./exec_log/exec_log.ui
```
3. Modify your custom.hal file. Add line
```
loadusr /home/{USER}/linuxcnc/configs/{CONFIG_NAME}/exec_log/exec_logger.py
```
4. Start LinuxCNC with modified config.
