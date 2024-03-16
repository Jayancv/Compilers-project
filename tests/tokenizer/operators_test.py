from src.compiler import ast
from src.compiler.parser import parser
from src.compiler.tokenizer import tokenize, SourceLocation, DummyLocation

loc = DummyLocation(
    line=0,
    column=0
)


def test_operators_parser() -> None:
    assert parser(tokenize('a + 1 - 2')) == ast.TreeOperator(
        location=SourceLocation(line=1, column=7),
        left=ast.TreeOperator(location=loc, left=ast.Identifier(SourceLocation(line=1, column=1), name='a'),
                              operator="+",
                              right=ast.Literal(SourceLocation(line=1, column=5), value=1)
                              ),
        operator="-",
        right=ast.Literal(SourceLocation(line=1, column=9), value=2))
