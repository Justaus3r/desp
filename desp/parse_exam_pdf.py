from typing import Union
from dataclasses import dataclass
from py_pdf_parser.components import ElementList
from py_pdf_parser.loaders import load_file, PDFDocument


@dataclass
class HarvestIndices:
    NAME_N_ENROLL: int = 3
    EXAM_DATE_FRAG: int = 15
    EXAM_ROOM_FRAG: int = 17
    EXAM_ROW_FRAG: int = 18
    EXAM_COL_FRAG: int = 19
    EXAM_DATE: int = 20
    EXAM_TIMING: int = 21
    EXAM_ROOM: int = 22
    EXAM_ROW: int = 23
    EXAM_COL: int = 24
    COURSES: int = 25
    THEORY_EXAM_START: int = 5


hi: HarvestIndices = HarvestIndices


class ExamPdfParser:
    def __init__(self, fl_path: str) -> None:
        self.fl_path: str = fl_path

    def get_parsed_data(self) -> dict[str, Union[str, list]]:
        # we will use hard coded list indices
        # to extract different info provided by py_pdf_parser
        # since all pdf docs are identical
        CWAP_STR1: str = "BS (CS)-1 (B) Morning"
        CWAP_STR2: str = "BS (CS)-0 (S) Evening"
        BEGGAR_STR: str = "Please"
        exam_pdf: PDFDocument = load_file(self.fl_path)
        pdf_elements: ElementList = exam_pdf.elements
        harvest: dict[str, Union[str, list]] = {}
        name: str
        enrollment: str
        course_names: list[str] = []
        enrollment, name = pdf_elements[hi.NAME_N_ENROLL].text().split("\n")
        exam_timings: list[str] = pdf_elements[hi.EXAM_TIMING].text().split("\n")
        exam_room: list[str] = [
            pdf_elements[hi.EXAM_ROOM_FRAG].text().split("\n")[1]
        ] + pdf_elements[hi.EXAM_ROOM].text().split("\n")
        
        exam_dates: list[str] = [pdf_elements[hi.EXAM_DATE_FRAG].text()] + pdf_elements[
            hi.EXAM_DATE
        ].text().split("\n")
        
        __exam_rows: list[str] = [pdf_elements[hi.EXAM_ROW_FRAG].text()] + pdf_elements[
            hi.EXAM_ROW
        ].text().split("\n")
       
        __exam_colss: list[str] = [
            pdf_elements[hi.EXAM_COL_FRAG].text()
        ] + pdf_elements[hi.EXAM_COL].text().split("\n")

        exam_dimensions: list[tuple[str, str]] = [
            (__exam_rows[_], __exam_colss[_]) for _ in range(len(__exam_rows))
        ]

        _skip_next: bool = False
        courses: list[str] = (
            pdf_elements[hi.COURSES].text().split("\n")[hi.THEORY_EXAM_START :]
        )  # ignore lab exams
        for idx, course_name in enumerate(courses):
            if _skip_next:
                _skip_next = False
                continue
            if course_name.strip().endswith("&"):
                course_name_final: str = course_name + courses[idx + 1]
                _skip_next = True
                course_names.append(course_name_final)
                continue
            elif course_name.strip() == CWAP_STR1 or course_name.strip() == CWAP_STR2:
                continue
            elif course_name.strip().startswith(BEGGAR_STR):
                break

            course_names.append(course_name)

        harvest["name"] = name
        harvest["enrollment"] = enrollment
        harvest["courses"] = course_names
        harvest["exam_timings"] = exam_timings
        harvest["exam_room"] = exam_room
        harvest["exam_dates"] = exam_dates
        harvest["sitting_dimensions"] = exam_dimensions

        return harvest

