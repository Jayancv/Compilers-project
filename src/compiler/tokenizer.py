import re
from dataclasses import dataclass
from typing import Literal

TokenType = Literal["int_literal", "operators", "identifier", "parenthesis", "end"]


@dataclass(frozen=True)
class Token:
    type: TokenType
    text: str


def tokenize(source_code: str) -> list[Token]:
    whitespace_rex = re.compile(r'\s+')
    integer_rex = re.compile(r'[0-9]+')
    identifier_rex = re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')
    operator_rex = re.compile(r'[<>*/+-]')
    parenthesis_rex = re.compile(r'[(){}]')

    position = 0
    result: list[Token] = []

    while position < len(source_code):
        match = whitespace_rex.match(source_code, position)
        if match is not None:
            position = match.end()
            continue

        match = identifier_rex.match(source_code, position)
        if match is not None:
            result.append(Token(type='identifier', text=source_code[position:match.end()]))
            position = match.end()
            continue

        match = integer_rex.match(source_code, position)
        if match is not None:
            result.append(Token(type='int_literal', text=source_code[position:match.end()]))
            position = match.end()
            continue

        match = operator_rex.match(source_code, position)
        if match is not None:
            result.append(Token(type='operators', text=source_code[position:match.end()]))
            position = match.end()
            continue

        match = parenthesis_rex.match(source_code, position)
        if match is not None:
            result.append(Token(type='parenthesis', text=source_code[position:match.end()]))
            position = match.end()
            continue

        raise Exception(
            f'Tokenization failed near {source_code[position:(position + 10)]}')  # TODO make this more meaingful line col

    return result
