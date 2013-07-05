import re
import os
import subprocess

def command():

 	proc = subprocess.Popen( ("ps"), stdin = subprocess.PIPE, stdout = subprocess.PIPE, close_fds = True)
 	stdout_text, stderr_text = proc.communicate()

 	# pidRegex = re.compile(" *(\d+) +\w+ +\d+[ :\d\w.]+python.*spacebrew.py")
 	script = "spacebrew.py"
 	pidRegex = re.compile( " *(\d+) +root +\d+ [ \w]+python .*" + script )
 	pidArr = pidRegex.findall(stdout_text)
 	pidStr = ''

	if len(pidArr) > 0:
		for idx, pid in enumerate(pidArr):
			pidStr += pid
			if idx < (len(pidArr) - 1): pidStr += ' '
			else: pidStr += '\n'

	else: pidStr = 'N'

	print pidStr


if __name__ == "__main__":
	command()
