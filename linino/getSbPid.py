import re
import os
import subprocess


def command():

 	proc = subprocess.Popen( ("ps"), stdin = subprocess.PIPE, stdout = subprocess.PIPE, close_fds = True)
 	stdout_text, stderr_text = proc.communicate()

 	process = "python"
 	script = "spacebrew.py"
 	regex_str = " *(\d+) +root +\d+ [ \w]+" + process + " .*" + script 
 	# regex_str_osx = " *(\d+) +\w+ +\d+[ :\d\w.]+python.*spacebrew.py"
 	pid_regex = re.compile( regex_str )
 	pid_arr = pid_regex.findall( stdout_text )
 	pid_str = ''

	if len( pid_arr ) > 0:
		for idx, pid in enumerate( pid_arr ):
			pid_str += pid
			if idx < ( len( pid_arr ) - 1 ): pid_str += ' '
			else: pid_str += '\n'

	else: pid_str = 'N'

	print pid_str


if __name__ == "__main__":
	command()
