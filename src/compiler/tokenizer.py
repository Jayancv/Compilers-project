import re
from dataclasses import dataclass
from typing import Literal

TokenType = Literal["int_literal", "operators", "identifier", "parenthesis", "comment", "end"]


@dataclass(frozen=True)
class SourceLocation:
    line: int
    column: int


@dataclass(frozen=True)
class Token:
    type: TokenType
    text: str
    source_location: SourceLocation


def tokenize(source_code: str) -> list[Token]:
    whitespace_rex = re.compile(r'\s+')
    integer_rex = re.compile(r'[0-9]+')
    identifier_rex = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    # operator_rex = re.compile(r'[<>*/+-]'
    operator_rex = re.compile(r'==|!=|<=|>=|[+\-*/=<>]')
    parenthesis_rex = re.compile(r'[(){}]')
    single_line_comment_rex = re.compile(r'//.*?(?:\n|$)')
    multi_line_comment_rex = re.compile(r'/\*.*?\*/', re.DOTALL)

    position = 0
    line_num = 1
    column_num = 1
    result: list[Token] = []
    in_multi_line_comment = False

    while position < len(source_code):

        match = whitespace_rex.match(source_code, position)
        if match is not None:
            if '\n' in match.group():
                lines = match.group().split('\n')
                line_num += len(lines) - 1
                column_num = len(lines[-1]) + 1
            else:
                column_num += len(match.group())
            position = match.end()
            continue

        if not in_multi_line_comment:
            # Match single-line comments
            match = single_line_comment_rex.match(source_code, position)
            if match is not None:
                # result.append(Token(type='comment', text=match.group(), line=line_num, column=column_num))
                if '\n' in match.group():
                    lines = match.group().split('\n')
                    line_num += len(lines) - 1
                    column_num = len(lines[-1]) + 1
                else:
                    column_num += len(match.group())
                position = match.end()
                continue

        # Match multi-line comments
        match = multi_line_comment_rex.match(source_code, position)
        if match is not None:
            if not in_multi_line_comment:
                in_multi_line_comment = True
            if '\n' in match.group():  # get all lines
                lines = match.group().split('\n')
                for line in lines[:-1]:
                    line_num += 1
                    column_num = 1
                if lines[-1]:  # last line
                    column_num = len(lines[-1]) - 2
            else:  # single line
                column_num += len(match.group())
            position = match.end() - 2
            continue

        # Check if multi-line comment ends
        if in_multi_line_comment:
            end_match = re.search(r'\*/', source_code[position:])
            if end_match:
                end_index = position + end_match.start() + 2  # Move to the end of '*/'
                line_num += source_code[position:end_index].count('\n')
                if '\n' in source_code[position:end_index]:
                    column_num = len(source_code[position:end_index].split('\n')[-1]) + 1
                else:
                    column_num += end_match.start()
                position = end_index
                in_multi_line_comment = False
                continue
            else:
                position = len(source_code)
                continue

        match = identifier_rex.match(source_code, position)
        if match is not None:
            result.append(Token(type='identifier', text=source_code[position:match.end()],
                                source_location=SourceLocation(line=line_num, column=column_num)))
            column_num += len(match.group())
            position = match.end()
            continue

        match = integer_rex.match(source_code, position)
        if match is not None:
            result.append(Token(type='int_literal', text=source_code[position:match.end()],
                                source_location=SourceLocation(line=line_num, column=column_num)))
            column_num += len(match.group())
            position = match.end()
            continue

        match = operator_rex.match(source_code, position)
        if match is not None:
            result.append(Token(type='operators', text=source_code[position:match.end()],
                                source_location=SourceLocation(line=line_num, column=column_num)))
            column_num += len(match.group())
            position = match.end()
            continue

        match = parenthesis_rex.match(source_code, position)
        if match is not None:
            result.append(Token(type='parenthesis', text=source_code[position:match.end()],
                                source_location=SourceLocation(line=line_num, column=column_num)))
            column_num += len(match.group())
            position = match.end()
            continue

        raise Exception(
            f'Tokenization failed at line {line_num}, column {column_num}: near {source_code[position:(position + 10)]}')

    return result
