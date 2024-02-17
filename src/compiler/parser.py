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
        if expected is not None and token.text != expected:
            raise Exception(f'Expected "{expected}", got "{token.text}" ')
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

    def parse_factors() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesize_expression()
        if peek().text == 'if':
            return parse_if_expression()
        elif peek().type == 'int_literal':
            return parse_literal()
        else:
            raise Exception(f'Unexpected "{peek().text}" ')

    def parse_parenthesize_expression() -> ast.Expression:
        consume('(')
        expr = parse_expression()
        consume(')')
        return expr

    def parse_terms() -> ast.Expression:
        left: ast.Expression = parse_factors()
        while peek().text in ['*', '/']:
            op = consume()
            right = parse_factors()
            left = ast.TreeOperator(left, op.text, right)
        return left

    def parse_polynomial() -> ast.Expression:
        left: ast.Expression = parse_terms()
        while peek().text in ['+', '-']:
            op = consume()
            right = parse_terms()
            left = ast.TreeOperator(left, op.text, right)

        return left

    def parse_expression() -> ast.Expression:
        left: ast.Expression = parse_polynomial()
        while peek().text in ['<', '>']:
            op = consume()
            right = parse_polynomial()
            left = ast.TreeOperator(left, op.text, right)

        return left

    def parse_if_expression() -> ast.Expression:
        consume('if')
        condition = parse_expression()
        consume('then')
        then_clause = parse_expression()
        if peek().text == 'else':
            consume('else')
            else_clause = parse_expression()
        else:
            else_clause = None

        return ast.IfExpression(condition, then_clause, else_clause)


    return parse_expression()


# TODO right associativity
