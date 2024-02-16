from compiler import ast
from compiler.parser import parser
from compiler.tokenizer import tokenize


def test_parser() -> None:
    assert parser(tokenize('1 + 2')) == ast.TreeOperator(
        left=ast.Literal(1),
        operator="+",
        right=ast.Literal(2)
    )
