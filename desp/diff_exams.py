from rich import box
from typing import Union
from rich.tree import Tree
from rich.table import Table
from rich.console import Console
from dataclasses import dataclass
from .parse_exam_pdf import ExamPdfParser


console_obj: Console = Console()

"""
single candidate diff structure:
diff = 
        {
                Candidate Name : str,
                Candidate Seating: str,
                Exam Room: list,
                Cheating Partners: list
                Cheating Partners Seating: list
                Seating Diff Visual: str
                }
"""


@dataclass
class AuxInfo:
    exam_count: int
    exam_seating_diff_str: str = """[1-1]  [1-2] [1-3] [1-4]  [1-5]
[2-1]  [2-2] [2-3] [2-4]  [2-5]
[3-1]  [3-2] [3-3] [3-4]  [3-5]
[4-1]  [4-2] [4-3] [4-4]  [4-5]
[5-1]  [5-2] [5-3] [5-4]  [5-5]
[6-1]  [6-2] [6-3] [6-4]  [6-5]"""


class DiffExams:
    def __init__(self, *exams) -> None:
        self.candidates_info: list[dict[str, Union[str, list]]] = exams
        # we check exams of every candidate and pick out the
        # lowest common denominator
        self.__cand_exams_len = [len(exam["courses"]) for exam in exams]
        AuxInfo.exam_count = min(self.__cand_exams_len)
        self.disputed_exams_cand_idx_len: list = []
        for idx, elen in enumerate(self.__cand_exams_len):
            if elen != AuxInfo.exam_count:
                self.disputed_exams_cand_idx_len.append(idx)

        # we will just remove the diff of candidates
        # with base_case, to avoid dealing with
        # additional handling of shit

        # base_case is the candidate with
        # "courses" length equilent to AuxInfo.exam_count
        base_case: list = []
        for _cand in self.candidates_info:
            if len(_cand["courses"]) == AuxInfo.exam_count:
                base_case = _cand["courses"]
                break

        for _cand_idx in self.disputed_exams_cand_idx_len:
            for _idx in range(AuxInfo.exam_count):
                disputed_exam_cand_courses = self.candidates_info[_cand_idx]["courses"]

                _idx_course_base_case = base_case[_idx]
                _idx_course_disputed = disputed_exam_cand_courses[_idx]

                if _idx_course_base_case != _idx_course_disputed:
                    self.candidates_info[_cand_idx]["courses"].pop(_idx)
                    self.candidates_info[_cand_idx]["exam_room"].pop(_idx)
                    break

    def __generate_single_diff(self, _candidate: dict) -> dict:
        single_candidate_diff: dict = {}

        single_candidate_diff["cheating-partners"] = [
            [] for _ in range(AuxInfo.exam_count)
        ]
        single_candidate_diff["cheating-partners-seating-coords"] = [
            [] for i in range(AuxInfo.exam_count)
        ]
        single_candidate_diff["name"] = _candidate["name"]
        single_candidate_diff["seating-coords"] = _candidate["sitting_dimensions"]
        single_candidate_diff["courses"] = _candidate["courses"]
        single_candidate_diff["exam_dates"] = _candidate["exam_dates"]
        single_candidate_diff["lucky_days"] = []
        single_candidate_diff["exam_room"] = _candidate["exam_room"]
        for _cand in self.candidates_info:
            if _cand == _candidate:
                continue

            for _ctr in range(AuxInfo.exam_count):
                if _cand["exam_room"][_ctr] == _candidate["exam_room"][_ctr]:
                    single_candidate_diff["cheating-partners"][_ctr].append(
                        _cand["name"]
                    )
                    single_candidate_diff["cheating-partners-seating-coords"][
                        _ctr
                    ].append(_cand["sitting_dimensions"][_ctr])

                    single_candidate_diff["lucky_days"].append(_cand["exam_room"])

        return single_candidate_diff

    def generate_diffs(self) -> list[dict]:
        diffs: dict = {}
        for single_candidate in self.candidates_info:
            single_candidate_diff = self.__generate_single_diff(single_candidate)
            single_cand_final_diff = self.__create_seating_diff_visual(
                single_candidate_diff
            )
            diffs.update({single_cand_final_diff["name"]: single_cand_final_diff})
        return diffs

    def __create_seating_diff_visual(self, diff: dict) -> dict:
        diff["seating-diff-visuals"] = [[] for _ in range(AuxInfo.exam_count)]
        for _ctr in range(AuxInfo.exam_count):
            visual_diff_str: str = AuxInfo.exam_seating_diff_str
            row, col = diff["seating-coords"][_ctr]
            replacent_str_cand = "[green][!*!][/green]"
            visual_diff_str = visual_diff_str.replace(
                "[{}-{}]".format(row, col), replacent_str_cand
            )
            single_exam_seating: list = diff["cheating-partners-seating-coords"][_ctr]
            single_exam_partners: list = diff["cheating-partners"][_ctr]

            for idx, partner_coords in enumerate(single_exam_seating):
                row, col = partner_coords
                cheat_partner_fname, cheat_partner_mname, *_ = single_exam_partners[
                    idx
                ].split()
                replacent_str_cheat_partner = "[cyan][{}.{}][/cyan]".format(
                    cheat_partner_fname[0], cheat_partner_mname[0]
                )
                visual_diff_str = visual_diff_str.replace(
                    "[{}-{}]".format(row, col), replacent_str_cheat_partner
                )
            diff["seating-diff-visuals"][_ctr] = visual_diff_str

        return diff


def visualize_diff(diff: dict) -> None:
    cand_name: str = diff["name"]
    candidate_exam: Tree = Tree("{}'s Theory Exams".format(cand_name))
    for exam, exam_date in zip(diff["courses"], diff["exam_dates"]):
        candidate_exam.add(exam_date + " - " + exam)

    lucky_days: Table = Table(show_lines=True, show_header=False, box=box.ROUNDED)
    candidate_name_abbreviations: Tree = Tree("Cheat Buddies")

    _already_added: list = []
    for partners in diff["cheating-partners"]:
        for partner in partners:
            if partner in _already_added:
                continue
            first_name, middle_name, *_ = partner.split()
            candidate_name_abbreviations.add(
                "{}.{}".format(first_name[0], middle_name[0]) + " - " + partner
            )
            _already_added.append(partner)

    visual_diffs = Table(show_lines=True, show_header=False, box=box.ROUNDED)

    visual_diff_strs = diff["seating-diff-visuals"]
    visual_diffs_individual = []
    for idx, diff_str in enumerate(visual_diff_strs):
        individual_tbl = Table(
            title=diff["exam_dates"][idx] + " | " + diff["exam_room"][idx],
            show_header=False,
            box=box.ROUNDED,
        )
        individual_tbl.add_row(diff_str)

        visual_diffs_individual.append(individual_tbl)

    for idx in range(0, len(visual_diff_strs), 2):
        try:
            visual_diffs.add_row(*visual_diffs_individual[idx : idx + 2])
        except IndexError:
            pass

    lucky_days.add_row(candidate_name_abbreviations, visual_diffs)

    tbl: Table = Table(
        title="{}'s Seating".format(cand_name),
        show_lines=True,
        show_header=False,
        box=box.ROUNDED,
    )
    tbl.add_row("Courses", candidate_exam)
    tbl.add_row("Lucky Days", lucky_days)
    console_obj.print(tbl)
