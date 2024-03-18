from src.compiler import ast, types
from src.compiler.parser import parser
from src.compiler.tokenizer import tokenize, DummyLocation, SourceLocation
from src.compiler.types import Type, Int

loc = DummyLocation(
    line=0,
    column=0
)


def test_parse_while_loop() -> None:
    assert parser(tokenize('func(1,2)')) == ast.FunctionCall(
        location=SourceLocation(line=1, column=1),
        call=ast.Identifier(loc, name="func"),
        args=[ast.Literal(location=SourceLocation(line=1, column=6),value=1),
             ast.Literal(location=SourceLocation(line=1, column=8), value=2)])


def test_parse_print() -> None:
    assert parser(tokenize('print_int(2);')) == ast.FunctionCall(loc,
             type=types.BasicType(name='Unit'),  call=ast.Identifier(loc,    type=types.BasicType(name='Unit'), name='print_int'),
             args=[ast.Literal(loc,   type=types.BasicType(name='Unit'),  value=2)])

def test_parse_f() -> None:
    assert (parser(tokenize('f(x, y + z)')) ==
            ast.FunctionCall(
                loc, call=ast.Identifier(loc, name='f'),
                args=[ast.Identifier(loc, name='x'),
                      ast.TreeOperator(loc, left=ast.Identifier(loc, name='y'), operator='+',
                                       right=ast.Identifier(loc, name='z'))]))
