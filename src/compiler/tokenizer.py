import re
from dataclasses import dataclass
from typing import Literal

TokenType = Literal[
    "int_literal", "bool_literal", "bool_operators", "operators", "identifier", "parenthesis", "comment", "keyword",
    "null_literal", "unary_operator", "punctuation", "end"]


@dataclass
class SourceLocation:
    line: int
    column: int

    def __str__(self) -> str:
        return f'line: {self.line}, column : {self.column}'


@dataclass
class DummyLocation(SourceLocation):  # for skip location validation in test
    def __eq__(self, other: object) -> bool:
        return isinstance(other, SourceLocation)


@dataclass(frozen=True)
class Token:
    type: TokenType
    text: str
    source_location: SourceLocation


def add_token(result: list[Token], token_type: TokenType, text: str, line_num: int, column_num: int) -> int:
    result.append(Token(type=token_type, text=text, source_location=SourceLocation(line=line_num, column=column_num)))
    return len(text)


def tokenize(source_code: str) -> list[Token]:
    whitespace_rex = re.compile(r'\s+')
    integer_rex = re.compile(r'[0-9]+')
    bool_rex = re.compile(r'true|false')
    bool_operator_rex = re.compile(r'and|or')
    unary_rex = re.compile(r'not')
    identifier_rex = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    operator_rex = re.compile(r'==|!=|<=|>=|[+\-*/=<>]')
    parenthesis_rex = re.compile(r'[(){}]')
    punctuation_rex = re.compile(r'[,:;]')
    single_line_comment_rex = re.compile(r'//.*?(?:\n|$)')
    multi_line_comment_rex = re.compile(r'/\*.*?\*/', re.DOTALL)
    keywords_rex = re.compile(r'if|then|else|while|do|var|return|break|continue|fun')
    null_rex = re.compile(r'null')

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

        # Match tokens and add to result using the add_token function
        for token_rex, token_type in [(keywords_rex, 'keyword'), (bool_rex, 'bool_literal'),
                                      (bool_operator_rex, 'bool_operator'), (unary_rex, 'unary_operator'),
                                      (null_rex, 'null_literal'), (identifier_rex, 'identifier'),
                                      (integer_rex, 'int_literal'), (operator_rex, 'operators'),
                                      (parenthesis_rex, 'parenthesis'), (punctuation_rex, 'punctuation')]:
            match = token_rex.match(source_code, position)
            if match is not None:
                column_num += add_token(result, token_type, match.group(), line_num, column_num)
                position = match.end()
                break
        else:
            raise Exception(
                f'Tokenization failed at line {line_num}, column {column_num}: near {source_code[position:(position + 10)]}')

    return result
