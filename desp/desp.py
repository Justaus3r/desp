from .repl import Repl
from rich.console import Console

con = Console()


def main():
    try:
        repl: Repl = Repl()
        repl.init_repl()
        repl.start_repl()
    except Exception:
        print(
            "An Unhandled Exception has Occured, report this issue on github bug tracker"
        )
        con.print_exception(show_locals=True)
