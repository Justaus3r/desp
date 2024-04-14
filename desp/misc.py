import os
import subprocess

UTIL_VERSION: str = "0.2.1"


UTIL_AUTHOR: str = "Justuas3r"

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

Starting from 0.2.0, it should work with most, if not all student slips as now it doesn't depend on
embedded const indices and tries to be smart and extract data based on patterns.
"""


def clear_screen() -> int:
    status: int = 1
    cmd: str = "cls" if os.name == "nt" else "clear"
    forked_process_status = subprocess.run([cmd], shell=True)

    if not forked_process_status.returncode:
        status = 0

    return status
