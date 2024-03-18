from src.compiler import ast
from src.compiler.parser import parser
from src.compiler.tokenizer import tokenize, DummyLocation, SourceLocation
from src.compiler.types import Type, Int

loc = DummyLocation(
    line=0,
    column=0
)


def test_parse_blocks() -> None:
    assert parser(tokenize('{ a+b ; var a = 2  x=1 ;}')) == ast.Block(
        loc,
        statements=[
            ast.TreeOperator(loc, left=ast.Identifier(loc, name='a'), operator='+',
                             right=ast.Identifier(loc, name='b')),
            ast.VarDeclaration(loc, name=ast.Identifier(loc, name='a'), var_type=None, value=ast.Literal(loc, value=2)),
            ast.TreeOperator(loc, left=ast.Identifier(loc, name='x'), operator='=', right=ast.Literal(loc, value=1))
            ,ast.Literal(loc, None)
        ]
    )

def test_parse_semicolons_missing_exception() -> None:
    try:
        parser(tokenize('{ a+b ; var a = 2  x=1 ;}'))
        assert False
    except Exception as e:
        assert 'expected ";"' in str(e)

def test_parse_brackets() -> None:
    assert parser(tokenize('{ { a } { b } }')) == ast.Block(
        loc,
        statements=[ast.Block(loc, statements=[ast.Identifier(loc,  name='a')]),
                    ast.Block(loc,   statements=[ast.Identifier(loc,  name='b')])
                    ]
    )
    assert parser(tokenize('{if true then { a }  b  }')) == ast.Block(
        loc,
        statements=[ast.IfExpression(
            loc,
            condition=ast.Literal(loc, value=True),
            then_clause=ast.Block(loc, statements=[ast.Identifier(loc, name='a')]),
            else_clause=None),
                    ast.Identifier(loc, name='b')])

    assert parser(tokenize('{if true then { a } ; b  }')) == ast.Block(
        loc,
        statements=[ast.IfExpression(
            loc,
            condition=ast.Literal(loc, value=True),
            then_clause=ast.Block(loc, statements=[ast.Identifier(loc, name='a')]),
            else_clause=None),
            ast.Identifier(loc, name='b')])

    assert parser(tokenize('{if true then { a }  b ; c }')) == ast.Block(
        loc,
        statements=[ast.IfExpression(
            loc,
            condition=ast.Literal(loc, value=True),
            then_clause=ast.Block(loc, statements=[ast.Identifier(loc, name='a')]),
            else_clause=None),
            ast.Identifier(loc, name='b'),
            ast.Identifier(loc, name='c')])

    assert parser(tokenize('{if true then { a } else { b } 3 }')) == ast.Block(
        loc,
        statements=[ast.IfExpression(
            loc,
            condition=ast.Literal(loc, value=True),
            then_clause=ast.Block(loc, statements=[ast.Identifier(loc, name='a')]),
            else_clause=ast.Block(loc, statements=[ast.Identifier(loc, name='b')])),
            ast.Literal(loc, value=3)])

    assert parser(tokenize('x = { { f(a) } { b } }')) == ast.TreeOperator(
        loc,
        left=ast.Identifier(loc, name='x'),
        operator='=',
        right=ast.Block(loc, statements=[
            ast.Block(loc, statements=[
                ast.FunctionCall(loc, call=ast.Identifier(loc, name='f'), args=[ast.Identifier(loc, name='a')])]),
            ast.Block(loc, statements=[ast.Identifier(loc, name='b')])])
    )

    try:
        parser(tokenize('{  a b }'))
        assert False
    except Exception as e:
        assert 'expected ";"' in str(e)
        assert ' "}"' in str(e)

    try:
        parser(tokenize('{ if true then { a } b c }'))
        assert False
    except Exception as e:
        assert 'expected ";"' in str(e)
        assert ' "}"' in str(e)