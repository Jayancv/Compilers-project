from src.compiler import ast, types
from src.compiler.parser import parser
from src.compiler.tokenizer import tokenize, DummyLocation, SourceLocation

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

    assert parser(tokenize('var x = 123')) == ast.VarDeclaration(
        location=loc,
        name=ast.Identifier(location=SourceLocation(line=1, column=5), name="x"),
        var_type=None,
        value=ast.Literal(loc, value=123)
    )

    assert parser(tokenize('var a: Int = 1+2')) == ast.VarDeclaration(
        location=loc,
        name=ast.Identifier(location=SourceLocation(line=1, column=5), name="a"),
        var_type=ast.TypeInt('Int'),
        value=ast.TreeOperator(loc, ast.Literal(loc, value=1), '+', ast.Literal(loc, value=2))
    )

    assert parser(tokenize('var b: Bool = False')) == ast.VarDeclaration(
        loc, name=ast.Identifier(loc, name='b'),
        var_type=ast.TypeBool(type='Bool'), value=ast.Identifier(loc, name='False'))

    assert parser(tokenize('{var a: Int = 2; print_int(a);}')) == ast.Block(
        loc,
        statements=[
            ast.VarDeclaration(loc,
                               name=ast.Identifier(loc, name='a'),
                               var_type=ast.TypeInt(type='Int'),
                               value=ast.Literal(loc, 2)),
            ast.FunctionCall(loc, ast.Identifier(loc, 'print_int'), args=[ast.Identifier(loc, name='a')]),
            ast.Literal(loc, None)
        ]
    )


def test_parse_vars1() -> None:
    assert parser(tokenize('{var a: Int = 2; print_int(a);}')) == ast.Block(
        loc,
        statements=[
            ast.VarDeclaration(loc,
                               name=ast.Identifier(loc, name='a'),
                               var_type=ast.TypeInt(type='Int'),
                               value=ast.Literal(loc, 2)),
            ast.FunctionCall(loc, ast.Identifier(loc, 'print_int'), args=[ast.Identifier(loc, name='a')])
        ]
    )
