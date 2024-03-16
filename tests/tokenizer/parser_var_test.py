from src.compiler import ast
from src.compiler.parser import parser
from src.compiler.tokenizer import tokenize, DummyLocation, SourceLocation
from src.compiler.types import Type, Int

loc = DummyLocation(
    line=0,
    column=0
)


def test_parse_vars() -> None:
    assert parser(tokenize('var a: Int = 1')) == ast.VarDeclaration(
        location=loc,
        name=ast.Identifier(location=SourceLocation(line=1, column=5), name="a"),
        var_type=ast.TypeInt('Int'),
        value=ast.Literal(loc, value=1)
    )

    assert parser(tokenize('var a = 1')) == ast.VarDeclaration(
        location=loc,
        name=ast.Identifier(location=SourceLocation(line=1, column=5), name="a"),
        var_type=None,
        value=ast.Literal(loc, value=1)
    )

    assert parser(tokenize('var a: Int = 1+2')) == ast.VarDeclaration(
        location=loc,
        name=ast.Identifier(location=SourceLocation(line=1, column=5), name="a"),
        var_type=ast.TypeInt('Int'),
        value=ast.TreeOperator(loc, ast.Literal(loc, value=1), '+', ast.Literal(loc, value=2))
    )
