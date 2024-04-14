import os
import logging
import subprocess
from glob import glob
from time import sleep
from threading import Thread, Lock
from rich.logging import RichHandler
from prompt_toolkit.styles import Style
from .parse_exam_pdf import ExamPdfParser
from .diff_exams import DiffExams, visualize_diff
from prompt_toolkit.completion import WordCompleter
from .misc import clear_screen, UTIL_HELP, UTIL_VERSION
from .exceptions import AlreadyActiveEventLoop, ReplNotInitialized
from prompt_toolkit import PromptSession, HTML, print_formatted_text as print


thread_mutex: Lock = Lock()

logging.basicConfig(
    format=logging.BASIC_FORMAT, level=logging.INFO, handlers=[RichHandler()]
)
repl_logger: "Logger" = logging.getLogger()


class Repl:
    event_loop_active: bool = False

    def __init__(self) -> None:
        self.prompt_session: PromptSession = PromptSession()
        self.prompt_style: Style = Style.from_dict({"": "#ff0066", "prompt": "#00aa00"})
        self.prompt_string: list[tuple[str]] = [("class:prompt", "\n>>")]
        self.__pdf_loc: str = os.path.join(os.getenv("LOCALAPPDATA"), "desp_pdfs")
        self.pdfs: list = []
        self.already_loaded_pdfs: list[str] = []
        self.candidate_names: list[str] = []
        self.word_completer: list[str] = []

        self.__repl_is_initialized: bool = False

    @property
    def pdf_loc(self) -> str:
        return self.__pdf_loc

    @pdf_loc.getter
    def pdf_loc(self) -> str:
        if not os.path.exists(self.__pdf_loc):
            os.mkdir(self.__pdf_loc)

        return self.__pdf_loc

    def __hotreload_pdf(self):
        is_hotreload = False
        while Repl.event_loop_active:
            with thread_mutex:
                for pdf in glob(os.path.join(self.pdf_loc, "*")):
                    if os.path.basename(pdf) in self.already_loaded_pdfs:
                        continue
                    is_hotreload = True
                    pdf_obj = ExamPdfParser(pdf)
                    repl_logger.info(
                        "New candidate slip detected! : {}".format(
                            os.path.basename(pdf)
                        )
                    )
                    print("", end="")
                    self.already_loaded_pdfs.append(os.path.basename(pdf))
                    cand_parsed_pdf: dict = pdf_obj.get_parsed_data()
                    self.candidate_names.append(cand_parsed_pdf["name"])
                    self.pdfs.append(cand_parsed_pdf)
                if is_hotreload:
                    self.word_completer = WordCompleter(self.candidate_names)
                    is_hotreload = False
            sleep(2)

    def init_repl(self):

        if Repl.event_loop_active:
            raise AlreadyActiveEventLoop
        else:
            Repl.event_loop_active = True
        print(HTML("<green>loading candidate slips...</green>"))
        Thread(name="repl-event-loop", target=self.__hotreload_pdf).start()
        sleep(1.2)
        clear_screen()
        self.__repl_is_initialized = True

    def start_repl(self):
        if not self.__repl_is_initialized:
            raise ReplNotInitialized
        while Repl.event_loop_active:
            print(
                HTML(
                    "<green><b>type candidate name to get the diff OR 'help' for help. Use TAB for autocompletion</b></green>"
                )
            )
            cmd: str = self.prompt_session.prompt(
                self.prompt_string,
                style=self.prompt_style,
                completer=self.word_completer,
            )

            if cmd in self.candidate_names:
                pass
            elif cmd == "opdf":
                cmd_completion = subprocess.run(
                    ["explorer", self.pdf_loc],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                if not cmd_completion.returncode:
                    repl_logger.error("explorer.exe subprocess returned returncode 0")
                continue
            elif cmd == "help":
                print(HTML(UTIL_HELP))
                continue
            elif cmd in ["exit", "quit"]:
                Repl.event_loop_active = False
                continue
            elif cmd == "lpdf":
                for pdf in self.already_loaded_pdfs:
                    print(pdf)
                continue
            elif cmd == "clear":
                clear_screen()
                continue
            elif cmd == "ver":
                print("ver: ", UTIL_VERSION)
                continue
            elif not cmd.strip():
                continue
            else:
                repl_logger.error("Unknown phrase!")
                continue

            diff_obj = DiffExams(*self.pdfs)
            generated_diffs = diff_obj.generate_diffs()
            
            try:
                cand_diff = generated_diffs[cmd]
            except KeyError:
                repl_logger.error("Moye Moye!, ye tou bnda hi nhi mila")
                continue

            clear_screen()
            visualize_diff(cand_diff)

        print(HTML("<cyan>Quitting!\nGood luck cheating ig?</cyan>"))
