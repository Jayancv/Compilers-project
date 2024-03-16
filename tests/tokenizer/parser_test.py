from src.compiler import ast
from src.compiler.parser import parser
from src.compiler.tokenizer import tokenize, SourceLocation, DummyLocation

loc = DummyLocation(
    line=0,
    column=0
)


def test_parser() -> None:
    assert parser(tokenize('1')) == ast.Literal(location=SourceLocation(line=1, column=1), value=1)

    assert parser(tokenize('1 + 2')) == ast.TreeOperator(
        location=SourceLocation(line=1, column=3),
        left=ast.Literal(SourceLocation(line=1, column=1), 1),
        operator="+",
        right=ast.Literal(SourceLocation(line=1, column=5), 2)
    )

    assert parser(tokenize('1* 2 + 3')) == ast.TreeOperator(
        location=SourceLocation(line=1, column=6),
        left=ast.TreeOperator(
            location=SourceLocation(line=1, column=2),
            left=ast.Literal(SourceLocation(line=1, column=1), 1),
            operator='*',
            right=ast.Literal(SourceLocation(line=1, column=4), 2)
        ),
        operator="+",
        right=ast.Literal(SourceLocation(line=1, column=8), 3)
    )

    assert parser(tokenize('1 *3 + 2 * 3')) == ast.TreeOperator(
        location=SourceLocation(line=1, column=6),
        left=ast.TreeOperator(
            location=SourceLocation(line=1, column=3),
            left=ast.Literal(SourceLocation(line=1, column=1), 1),
            operator='*',
            right=ast.Literal(SourceLocation(line=1, column=4), 3)
        ),
        operator="+",
        right=ast.TreeOperator(
            location=SourceLocation(line=1, column=10),
            left=ast.Literal(SourceLocation(line=1, column=8), 2),
            operator='*',
            right=ast.Literal(SourceLocation(line=1, column=12), 3)
        )
    )

    assert parser(tokenize('1 * ( 3 + 2 )')) == ast.TreeOperator(
        location=loc,
        left=ast.Literal(loc, 1),
        operator="*",
        right=ast.TreeOperator(
            location=loc,
            left=ast.Literal(loc, 3),
            operator='+',
            right=ast.Literal(loc, 2)
        )
    )

    assert parser(tokenize('(1 + 3) + 2 ')) == ast.TreeOperator(
        location=loc,
        left=ast.TreeOperator(
            location=loc,
            left=ast.Literal(loc, 1),
            operator='+',
            right=ast.Literal(loc, 3)
        ),
        operator="+",
        right=ast.Literal(loc, 2)

    )

    assert parser(tokenize('1 * ( 2 - 3 ) / 5')) == ast.TreeOperator(
        location=loc,
        left=ast.TreeOperator(
            location=loc,
            left=ast.Literal(loc, 1),
            operator='*',
            right=ast.TreeOperator(
                location=loc,
                left=ast.Literal(loc, 2),
                operator='-',
                right=ast.Literal(loc, 3)
            )
        ),
        operator="/",
        right=ast.Literal(loc, 5)

    )

    assert parser(tokenize('( 1 + 5 ) - ( 2 * 3 ) / 5')) == ast.TreeOperator(
        location=loc,
        left=ast.TreeOperator(
            location=loc,
            left=ast.Literal(loc, 1),
            operator='+',
            right=ast.Literal(loc, 5)
        ),
        operator="-",
        right=ast.TreeOperator(
            location=loc,
            left=ast.TreeOperator(
                location=loc,
                left=ast.Literal(loc, 2),
                operator='*',
                right=ast.Literal(loc, 3)
            ),
            operator='/',
            right=ast.Literal(loc, 5)
        )
    )

    assert parser(tokenize('(1 + 3) > 2 ')) == ast.TreeOperator(
        location=loc,
        left=ast.TreeOperator(
            location=loc,
            left=ast.Literal(loc, 1),
            operator='+',
            right=ast.Literal(loc, 3)
        ),
        operator=">",
        right=ast.Literal(loc, 2)

    )

    assert parser(tokenize('if 1 then 2 ')) == ast.IfExpression(
        location=loc,
        condition=ast.Literal(loc, 1),
        then_clause=ast.Literal(loc, 2),
        else_clause=None
    )

    assert parser(tokenize('if 1 then 2 else 5')) == ast.IfExpression(
        location=loc,
        condition=ast.Literal(loc, 1),
        then_clause=ast.Literal(loc, 2),
        else_clause=ast.Literal(loc, 5)
    )

    assert parser(tokenize('if 1-4 then 2*3 else 5/6')) == ast.IfExpression(
        location=loc,
        condition=ast.TreeOperator(loc, left=ast.Literal(loc, 1), operator='-', right=ast.Literal(loc, 4)),
        then_clause=ast.TreeOperator(loc, left=ast.Literal(loc, 2), operator='*', right=ast.Literal(loc, 3)),
        else_clause=ast.TreeOperator(loc, left=ast.Literal(loc, 5), operator='/', right=ast.Literal(loc, 6))
    )
