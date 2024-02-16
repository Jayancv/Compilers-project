from compiler.tokenizer import tokenize, Token


def test_tokenizer() -> None:
    assert tokenize("Hello") == [
        Token(type='identifier', text='Hello')
    ]
    assert tokenize("  \n Hello         \n    \n") == [
        Token(type='identifier', text='Hello')
    ]

    assert tokenize("  \n Hello    I am Jayan 123     \n    \n") == [
        Token(type='identifier', text='Hello'),
        Token(type='identifier', text="I"),
        Token(type='identifier', text="am"),
        Token(type='identifier', text='Jayan'),
        Token(type='int_literal', text='123')
    ]

    assert tokenize(" 3+ -6+2-(1)") == [
        Token(type='int_literal', text='3'),
        Token(type='operators', text='+'),
        Token(type='operators', text='-'),
        Token(type='int_literal', text='6'),
        Token(type='operators', text='+'),
        Token(type='int_literal', text='2'),
        Token(type='operators', text='-'),
        Token(type='parenthesis', text='('),
        Token(type='int_literal', text='1'),
        Token(type='parenthesis', text=')'),
    ]

    assert tokenize("if  3\nwhile") == [
        Token(type='identifier', text='if'),
        Token(type='int_literal', text='3'),
        Token(type='identifier', text='while')
    ]
