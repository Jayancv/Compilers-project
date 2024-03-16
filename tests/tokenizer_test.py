from src.compiler.tokenizer import tokenize, Token, SourceLocation


def test_tokenizer() -> None:
    assert tokenize("Hello") == [
        Token(type='identifier', text='Hello', source_location=SourceLocation(line=1, column=1))
    ]
    assert tokenize("  \n Hello         \n    \n") == [
        Token(type='identifier', text='Hello', source_location=SourceLocation(line=2, column=2))
    ]

    assert tokenize("  \n Hello    I am Jayan 123     \n    \n") == [
        Token(type='identifier', text='Hello', source_location=SourceLocation(line=2, column=2)),
        Token(type='identifier', text="I", source_location=SourceLocation(line=2, column=11)),
        Token(type='identifier', text="am", source_location=SourceLocation(line=2, column=13)),
        Token(type='identifier', text='Jayan', source_location=SourceLocation(line=2, column=16)),
        Token(type='int_literal', text='123', source_location=SourceLocation(line=2, column=22))
    ]

    assert tokenize(" 3+ -6+2-(1)") == [
        Token(type='int_literal', text='3', source_location=SourceLocation(line=1, column=2)),
        Token(type='operators', text='+', source_location=SourceLocation(line=1, column=3)),
        Token(type='operators', text='-', source_location=SourceLocation(line=1, column=5)),
        Token(type='int_literal', text='6', source_location=SourceLocation(line=1, column=6)),
        Token(type='operators', text='+', source_location=SourceLocation(line=1, column=7)),
        Token(type='int_literal', text='2', source_location=SourceLocation(line=1, column=8)),
        Token(type='operators', text='-', source_location=SourceLocation(line=1, column=9)),
        Token(type='parenthesis', text='(', source_location=SourceLocation(line=1, column=10)),
        Token(type='int_literal', text='1', source_location=SourceLocation(line=1, column=11)),
        Token(type='parenthesis', text=')', source_location=SourceLocation(line=1, column=12)),
    ]

    assert tokenize(" 3!=6<2>=(1)") == [
        Token(type='int_literal', text='3', source_location=SourceLocation(line=1, column=2)),
        Token(type='operators', text='!=', source_location=SourceLocation(line=1, column=3)),
        Token(type='int_literal', text='6', source_location=SourceLocation(line=1, column=5)),
        Token(type='operators', text='<', source_location=SourceLocation(line=1, column=6)),
        Token(type='int_literal', text='2', source_location=SourceLocation(line=1, column=7)),
        Token(type='operators', text='>=', source_location=SourceLocation(line=1, column=8)),
        Token(type='parenthesis', text='(', source_location=SourceLocation(line=1, column=10)),
        Token(type='int_literal', text='1', source_location=SourceLocation(line=1, column=11)),
        Token(type='parenthesis', text=')', source_location=SourceLocation(line=1, column=12)),
    ]

    assert tokenize("if  3\nwhile") == [
        Token(type='keyword', text='if', source_location=SourceLocation(line=1, column=1)),
        Token(type='int_literal', text='3', source_location=SourceLocation(line=1, column=5)),
        Token(type='keyword', text='while', source_location=SourceLocation(line=2, column=1))
    ]

    assert tokenize("  \n Hello         \n  // Comment  \n jayan") == [
        Token(type='identifier', text='Hello', source_location=SourceLocation(line=2, column=2)),
        Token(type='identifier', text='jayan', source_location=SourceLocation(line=4, column=2))
    ]

    assert tokenize("  \n Hello     /* multi \n line \n comment */\n  Jayan  \n    \n") == [
        Token(type='identifier', text='Hello', source_location=SourceLocation(line=2, column=2)),
        Token(type='identifier', text='Jayan', source_location=SourceLocation(line=5, column=3))
    ]

    assert tokenize("  \n Hello     /* multi  line single comment */  Jayan  \n    \n") == [
        Token(type='identifier', text='Hello', source_location=SourceLocation(line=2, column=2)),
        Token(type='identifier', text='Jayan', source_location=SourceLocation(line=2, column=46))
    ]
