from src.compiler import ast
from src.compiler.parser import parser
from src.compiler.tokenizer import tokenize, DummyLocation, SourceLocation
from src.compiler.types import Type, Int

loc = DummyLocation(
    line=0,
    column=0
)


def test_parse_while_loop() -> None:
    assert parser(tokenize('while 1<2 do 1 + 2')) == ast.WhileLoop(
        location=SourceLocation(line=1, column=1),
        condition=ast.TreeOperator(
            location=SourceLocation(line=1, column=8),
            left=ast.Literal(location=SourceLocation(line=1, column=7), value=1),
            operator='<',
            right=ast.Literal(location=SourceLocation(line=1, column=9), value=2)),
        do_action=ast.TreeOperator(
            location=SourceLocation(line=1, column=16),
            left=ast.Literal(location=SourceLocation(line=1, column=14), value=1),
            operator='+',
            right=ast.Literal(location=SourceLocation(line=1, column=18), value=2)))


def test_parser_break_loops() -> None:
    assert parser(tokenize("while true do break")) == ast.WhileLoop(
        loc,
        condition=ast.Literal(loc, True),
        do_action=ast.BreakContinue(loc, 'break')
    )

    assert parser(tokenize("{if true then continue}")) == ast.Block(
        loc,
        statements=[ast.IfExpression(
            loc,
            condition=ast.Literal(loc, True),
            then_clause=ast.BreakContinue(loc, 'continue'),
            else_clause=None
        )]
    )
