from compiler.tokenizer import tokenize, Token


def test_tokenizer() -> None:
    assert tokenize("Hello") == [
        Token(type='identifier', text='Hello', line=1, column=1)
    ]
    assert tokenize("  \n Hello         \n    \n") == [
        Token(type='identifier', text='Hello', line=2, column=2)
    ]

    assert tokenize("  \n Hello    I am Jayan 123     \n    \n") == [
        Token(type='identifier', text='Hello', line=2, column=2),
        Token(type='identifier', text="I", line=2, column=11),
        Token(type='identifier', text="am", line=2, column=13),
        Token(type='identifier', text='Jayan', line=2, column=16),
        Token(type='int_literal', text='123', line=2, column=22)
    ]

    assert tokenize(" 3+ -6+2-(1)") == [
        Token(type='int_literal', text='3', line=1, column=2),
        Token(type='operators', text='+', line=1, column=3),
        Token(type='operators', text='-', line=1, column=5),
        Token(type='int_literal', text='6', line=1, column=6),
        Token(type='operators', text='+', line=1, column=7),
        Token(type='int_literal', text='2', line=1, column=8),
        Token(type='operators', text='-', line=1, column=9),
        Token(type='parenthesis', text='(', line=1, column=10),
        Token(type='int_literal', text='1', line=1, column=11),
        Token(type='parenthesis', text=')', line=1, column=12),
    ]

    assert tokenize("if  3\nwhile") == [
        Token(type='identifier', text='if', line=1, column=1),
        Token(type='int_literal', text='3', line=1, column=5),
        Token(type='identifier', text='while', line=2, column=1)
    ]

    assert tokenize("  \n Hello         \n  // Comment  \n jayan") == [
        Token(type='identifier', text='Hello', line=2, column=2),
        Token(type='identifier', text='jayan', line=4, column=2)
    ]

    assert tokenize("  \n Hello     /* multi \n line \n comment */\n  Jayan  \n    \n") == [
        Token(type='identifier', text='Hello', line=2, column=2),
        Token(type='identifier', text='Jayan', line=5, column=3)
    ]

    assert tokenize("  \n Hello     /* multi  line single comment */  Jayan  \n    \n") == [
        Token(type='identifier', text='Hello', line=2, column=2),
        Token(type='identifier', text='Jayan', line=2, column=46)
    ]
