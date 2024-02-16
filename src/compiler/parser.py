from compiler import ast
from compiler.tokenizer import Token


def parser(tokens: list[Token]) -> ast.Expression:
    pos = 0

    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(type='end', text='')

    def consume() -> Token:
        token = peek()
        nonlocal pos
        pos += 1
        return token

    def parse_literal() -> ast.Literal:
        token = peek()
        if token.type == 'int_literal':
            consume()
            return ast.Literal(value=int(token.text))
        else:
            raise Exception(f'Expected literal, Found "{token.text}"')

    def parse_expression() -> ast.Expression:
        left= parse_literal()
        op = consume()
        if op.text not in ['+', '-', '*', '/']:
            raise Exception(f'Expected literal, Found "{op.text}"')
        right = parse_literal()
        return ast.TreeOperator(left, op.text, right)

    return parse_expression()
