import os
import re
from typing import Union
from enum import Enum, auto
from dataclasses import dataclass
from pypdf import PdfReader, PageObject
from .exceptions import UnidentifiedToken


@dataclass
class HarvestIndices:
    nameNclass: int = 4
    enrollment: int = 3
    table_start: int = 6


class Harvest:
    def __init__(self) -> None:
        self.course_names: list[str] = []
        self.exam_rooms: list[str] = []
        self.exam_dates: list[str] = []
        self.exam_timings: list[str] = []
        self.exam_dimensions: list[tuple[str, str]] = []
        self.name: str = ""
        self.std_class: str = ""
        self.enrollment: str = ""


class TokenType(Enum):
    COURSE_NAME = auto()
    EXAM_DATE = auto()
    EXAM_TIMING = auto()
    EXAM_ROOM = auto()
    EXAM_ROW = auto()
    EXAM_COL = auto()
    SKIP = auto()
    SKIP_FOUR = auto()
    SKIP_THREE = auto()
    NOP = auto()


hi = HarvestIndices


class ExamPdfParser:
    def __init__(self, std_slip_pth: str) -> None:
        self.std_slip_pth = std_slip_pth

    def get_parsed_data(self) -> dict:
        harvest_obj: Harvest = Harvest()

        def extract_stdnameNclass(harvest_row: list[str]) -> str:
            stdname: str = ""
            stdclass: str = ""
            harvest_row = harvest_row[1:]  # skip the first token named 'Name:'
            idx: int = 0
            for idx, name_token in enumerate(harvest_row):
                if name_token == "Class:":
                    break
                stdname += " " + name_token

            after_classtoken_idx = idx + 1
            for class_token in harvest_row[after_classtoken_idx:]:
                stdclass += " " + class_token

            return stdname, stdclass

        def table_extraction_driver(table_start_idx: int) -> None:
            table_terminator_str: str = "Please"

            def process_token(token: str, ctx: dict) -> TokenType:
                token_idx: int = ctx["idx"]
                token_row: list[str] = ctx["row"]
                course_name_complete: bool = ctx["course-name-complete"] 

                if re.match(r"(^(?!BS)\w+[-&]*\w*)|^&", token) and not course_name_complete:
                    return TokenType.COURSE_NAME

                elif token.strip() == "BS" and re.match(
                    r"\(\w\w\)-\d", token_row[token_idx + 1]
                ):
                    return TokenType.SKIP_FOUR
                
                elif re.match(r"\(\w\w\)-\d", token_row[token_idx]):
                    # this happens when the token `BS`
                    # is not encountered due to some reason
                    # probably because its concatenated with
                    # previous token

                    return TokenType.SKIP_THREE
                
                elif re.match(r"\d{2}/\d{2}/\d{4}", token):
                    return TokenType.EXAM_DATE

                elif re.match(r"\d{2}:\d{2}", token):
                    return TokenType.EXAM_TIMING

                elif re.match(r"\w{2}-\d\d?", token):
                    return TokenType.EXAM_ROOM

                elif re.match(r"\d", token) and token_idx == len(token_row) - 2:
                    return TokenType.EXAM_ROW

                elif re.match(r"\d", token) and token_idx == len(token_row) - 1:
                    return TokenType.EXAM_COL

                elif token == "N/A" or token == "–":
                    return TokenType.NOP

                elif token == "&":
                    """
                    We need to check if the character is '&'
                    and next character is `BS`,meaning end of word, then
                    next row must be skipped, otherwise append
                    that to course name
                    """
                    if token_row[token_idx + 1] == "BS":
                        return TokenType.SKIP
                    else:
                        return TokenType.COURSE_NAME
                else:
                    return None

            course_name: str = ""
            exam_date: str = ""
            exam_timing: str = ""
            exam_room: str = ""
            exam_dimension: list[str, str] = ["", ""]

            skip_next_row: bool = False
            for row, single_exam_row in enumerate(
                extracted_text_dimensionfull[table_start_idx:]
            ):
                if single_exam_row[0] == table_terminator_str:
                    # If the first token is 'Please', then that
                    # means , we are outta table. very intelligent ik
                    break

                if skip_next_row:
                    try:
                        course_names_len = len(harvest_obj.exam_timings)
                        harvest_obj.course_names[course_names_len - 1] = (
                            harvest_obj.course_names[course_names_len - 1]
                            + " "
                            + " ".join(single_exam_row)
                        )
                    except IndexError:
                        # probably previous row was not a theory exam
                        # and this row contained a fragment of coursename
                        pass
                    skip_next_row = False
                    continue

                course_name_complete: bool = False
                skip_next4_cols: bool = False
                skip_next4_ctr = 0

                # same but for 3 iteration skip
                skip_next3_ctr = 0
                skip_next3_cols = False
                for col, token in enumerate(single_exam_row):
                    if skip_next4_cols:
                        # The idea here is that, when a course name is completed
                        # The next 4 tokens are the classname which we don't need so
                        # we want to skip those tokens. first skip is done in the conditional below
                        # next 3 skips are done here
                        if skip_next4_ctr < 3:
                            skip_next4_ctr += 1
                            continue
                        else:
                            skip_next4_ctr = 0
                            skip_next4_cols = False
                        
                    if skip_next3_cols:
                        if skip_next3_ctr < 2:
                            # same idea as above , just with three skips
                            skip_next3_ctr += 1
                            continue
                        else:
                            skip_next3_ctr = 0
                            skip_next3_cols = False

                    ctx: dict = {
                        "idx": col,
                        "row": single_exam_row,
                        "course-name-complete": course_name_complete,
                    }

                    if process_token(token, ctx) == TokenType.SKIP:
                        skip_next_row = True
                    elif process_token(token, ctx) == TokenType.SKIP_FOUR:
                        course_name_complete = True
                        skip_next4_cols = True
                        continue
                    elif process_token(token, ctx) == TokenType.SKIP_THREE:
                        course_name = course_name[:-2]
                        course_name_complete = True
                        skip_next3_cols = True
                        continue
                    elif process_token(token, ctx) == TokenType.COURSE_NAME:
                        course_name += " " + token
                    elif process_token(token, ctx) == TokenType.EXAM_DATE:
                        exam_date = token
                    elif process_token(token, ctx) == TokenType.EXAM_TIMING:
                        exam_timing = token
                    elif process_token(token, ctx) == TokenType.EXAM_ROOM:
                        exam_room = token
                    elif process_token(token, ctx) == TokenType.EXAM_ROW:
                        exam_dimension[0] = token
                    elif process_token(token, ctx) == TokenType.EXAM_COL:
                        exam_dimension[1] = token
                    elif process_token(token, ctx) == TokenType.NOP:
                        pass
                    else:
                        raise UnidentifiedToken(token)
                        

                if not exam_timing:
                    # if the exam doesn't have exam_timing
                    # that means, that its a LAB exam and we skip those.
                    course_name = ""
                    exam_date = ""
                    exam_room = ""
                    exam_timing = ""
                    exam_dimension = ["", ""]
                    continue

                harvest_obj.course_names.append(course_name)
                harvest_obj.exam_dates.append(exam_date)
                harvest_obj.exam_rooms.append(exam_room)
                harvest_obj.exam_timings.append(exam_timing)
                harvest_obj.exam_dimensions.append(exam_dimension)

                course_name = ""
                exam_date = ""
                exam_room = ""
                exam_timing = ""
                exam_dimension = ["", ""]

        read_slip: PageObject = PdfReader(self.std_slip_pth).pages[0]
        extracted_text: list[str] = read_slip.extract_text(
            extraction_mode="layout"
        ).splitlines()

        extracted_text_dimensionfull: list[list[str]] = [
            row.split() for row in extracted_text
        ]

        harvest_obj.enrollment: str = extracted_text_dimensionfull[hi.enrollment][1]
        harvest_obj.name, harvest_obj.std_class = extract_stdnameNclass(
            extracted_text_dimensionfull[hi.nameNclass]
        )

        table_extraction_driver(hi.table_start)

        harvest: dict = {}

        harvest = {
            "name": harvest_obj.name,
            "enrollment": harvest_obj.enrollment,
            "courses": harvest_obj.course_names,
            "exam_timings": harvest_obj.exam_timings,
            "exam_room": harvest_obj.exam_rooms,
            "exam_dates": harvest_obj.exam_dates,
            "sitting_dimensions": harvest_obj.exam_dimensions,
        }

        return harvest
