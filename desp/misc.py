import os
import subprocess

UTIL_VERSION: str = '0.1.0'


UTIL_AUTHOR: str =  "Justuas3r"

UTIL_HELP: str = """desp - a cli utility to help all look for cheating partners.

Commands:
opdf        reveal pdf's folder in file explorer to store all candidate slips
lpdf        print all the loaded pdfs
clear       clear the stdout
ver         show utility version
help        show this help message
quit/exit   quit the utility

Other than that, you are expected to Input a Candidate name

Note:
This is just a poc, will break in many cases.

<cyan><b><ul>Working Probability</ul></b></cyan>: <green>69%</green>. Well,  because its dumb and assumes that all pdfs are identical. Though it does perform a single iteration filtering to remove a single diff to match with base-case. It uses embedded indices to harvest all the required data(hence called harvest indices), so it probably won't work for Different Departments OR
Semesters(Though , can be made to work by changing the harvest indices).

And in Future , if Bahria decides to change their generated pdf's format, then , It will require 
an update for all the harvest indices. 

A Better way might be to parse the pdf and use regex to match patterns and harvest data, might redo the get_parsed_data() if i revisit this repo
"""

def clear_screen() -> int:
    status: int = 1
    cmd: str = 'cls' if os.name == 'nt' else 'clear'
    forked_process_status = subprocess.run([cmd], shell=True)
    
    if not forked_process_status.returncode:
        status = 0
    
    return status
