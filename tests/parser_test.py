from compiler import ast
from compiler.parser import parser
from compiler.tokenizer import tokenize


def test_parser() -> None:
    assert parser(tokenize('1')) == ast.Literal(1)

    assert parser(tokenize('1 + 2')) == ast.TreeOperator(
        left=ast.Literal(1),
        operator="+",
        right=ast.Literal(2)
    )

    assert parser(tokenize('1* 2 + 3')) == ast.TreeOperator(
        left=ast.TreeOperator(
            left=ast.Literal(1),
            operator='*',
            right=ast.Literal(2)
        ),
        operator="+",
        right=ast.Literal(3)
    )

    assert parser(tokenize('1 *3 + 2 * 3')) == ast.TreeOperator(
        left=ast.TreeOperator(
            left=ast.Literal(1),
            operator='*',
            right=ast.Literal(3)
        ),
        operator="+",
        right=ast.TreeOperator(
            left=ast.Literal(2),
            operator='*',
            right=ast.Literal(3)
        )
    )

    assert parser(tokenize('1 * ( 3 + 2 )')) == ast.TreeOperator(
        left=ast.Literal(1),
        operator="*",
        right=ast.TreeOperator(
            left=ast.Literal(3),
            operator='+',
            right=ast.Literal(2)
        )
    )

    assert parser(tokenize('(1 + 3) + 2 ')) == ast.TreeOperator(
        left=ast.TreeOperator(
            left=ast.Literal(1),
            operator='+',
            right=ast.Literal(3)
        ),
        operator="+",
        right=ast.Literal(2)

    )

    assert parser(tokenize('1 * ( 2 - 3 ) / 5')) == ast.TreeOperator(
        left=ast.TreeOperator(
            left=ast.Literal(1),
            operator='*',
            right=ast.TreeOperator(
                left=ast.Literal(2),
                operator='-',
                right=ast.Literal(3)
            )
        ),
        operator="/",
        right=ast.Literal(5)

    )

    assert parser(tokenize('( 1 + 5 ) - ( 2 * 3 ) / 5')) == ast.TreeOperator(
        left=ast.TreeOperator(
            left=ast.Literal(1),
            operator='+',
            right=ast.Literal(5)
        ),
        operator="-",
        right=ast.TreeOperator(
            left=ast.TreeOperator(
                left=ast.Literal(2),
                operator='*',
                right=ast.Literal(3)
            ),
            operator='/',
            right=ast.Literal(5)
        )
    )

    assert parser(tokenize('(1 + 3) > 2 ')) == ast.TreeOperator(
        left=ast.TreeOperator(
            left=ast.Literal(1),
            operator='+',
            right=ast.Literal(3)
        ),
        operator=">",
        right=ast.Literal(2)

    )

    assert parser(tokenize('if 1 then 2 ')) == ast.IfExpression(
        condition=ast.Literal(1),
        then_clause=ast.Literal(2),
        else_clause=None
    )

    assert parser(tokenize('if 1 then 2 else 5')) == ast.IfExpression(
        condition=ast.Literal(1),
        then_clause=ast.Literal(2),
        else_clause=ast.Literal(5)
    )

    assert parser(tokenize('if 1-4 then 2*3 else 5/6')) == ast.IfExpression(
        condition=ast.TreeOperator(ast.Literal(1), operator='-', right=ast.Literal(4)),
        then_clause=ast.TreeOperator(ast.Literal(2), operator='*', right=ast.Literal(3)),
        else_clause=ast.TreeOperator(ast.Literal(5), operator='/', right=ast.Literal(6))
    )
