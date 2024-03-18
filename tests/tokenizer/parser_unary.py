import src.compiler.ast as ast
from src.compiler.parser import parser
from src.compiler.tokenizer import tokenize, DummyLocation

loc = DummyLocation(
    line=0,
    column=0
)


def test_parse_unary_op() -> None:
    assert parser(tokenize('not a')) == ast.UnaryOp(
        loc,
        operator='not',
        expr=ast.Identifier(loc, name='a')
    )

    assert parser(tokenize('- a')) == ast.UnaryOp(
        loc,
        operator='-',
        expr=ast.Identifier(loc, name='a')
    )

def test_also_parse_second_unary_op() -> None:
    input = tokenize('test', '- a')
    expected = ast.UnaryOp(
        location,
        op='-',
        expr=ast.Identifier(location, name='a')
    )

    assert parse(input) == expected


def test_recognize_unary_op_after_operator() -> None:
    input = tokenize('test', 'a - - b')
    expected = ast.BinaryOp(
        location,
        left=ast.Identifier(location, name='a'),
        op='-',
        right=ast.UnaryOp(
            location,
            op='-',
            expr=ast.Identifier(location, name='b')
        )
    )

    assert parse(input) == expected


def test_expression_in_unary_op() -> None:
    input = tokenize('test', 'a + - (b or c)')
    expected = ast.BinaryOp(
        location,
        left=ast.Identifier(location, name='a'),
        op='+',
        right=ast.UnaryOp(
            location,
            op='-',
            expr=ast.BinaryOp(
                location,
                left=ast.Identifier(location, name='b'),
                op='or',
                right=ast.Identifier(location, name='c')
            )
        )
    )

    assert parse(input) == expected
