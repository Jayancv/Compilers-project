from src.compiler import ast
from src.compiler.ast import Identifier

from src.compiler.tokenizer import Token, SourceLocation
from src.compiler.types import Type


def parser(tokens: list[Token]) -> ast.Expression:
    pos = 0

    def peek() -> Token:
        if pos < len(tokens):
            return tokens[pos]
        else:
            return Token(type='end', text='', source_location=tokens[-1].source_location)

    def consume(expected: str | list[str] | None = None) -> Token:
        token = peek()
        if expected is not None and token.text != expected:
            raise Exception(f'{token.source_location} Expected "{expected}", got "{token.text}" ')
        if isinstance(expected, list) and token.text not in expected:
            comma_separated = ", ".join([f'"{e}"' for e in expected])
            raise Exception(f'{token.source_location}: expected one of: {comma_separated}')
        nonlocal pos
        pos += 1
        return token

    def parse_literal() -> ast.Literal:
        token = peek()
        if token.type == 'int_literal':
            consume()
            return ast.Literal(value=int(token.text), location=token.source_location)
        else:
            raise Exception(f'Expected literal, Found "{token.text}"')

    def parse_identifier() -> ast.Identifier:
        token = peek()
        if token.type == 'identifier':
            consume()
            return ast.Identifier(name=token.text, location=token.source_location)
        else:
            raise Exception(f'Expected identifier, Found "{token.text}"')

    def parse_bool_literal() -> ast.Literal:
        token = peek()
        if token.type != 'bool_literal':
            raise Exception(f'{token.location}: expected a boolean value')

        consume()
        if token.text.lower() == 'true':
            value = True
        elif token.text.lower() == 'false':
            value = False
        else:
            raise Exception(f'{token.location}: expected boolean true/True or false/False')

        return ast.Literal(value=value, location=token.location)

    def parse_factors() -> ast.Expression:
        if peek().text == '(':
            return parse_parenthesize_expression()
        elif peek().text == '{':
            return parse_blocks()
        elif peek().type == 'keyword':
            if peek().text == 'var':
                return parse_var_declaration()
            elif peek().text == 'if':
                return parse_if_expression()
            elif peek().text == 'while':
                return parse_while_loop()
        elif peek().type == 'identifier':
            identifier = parse_identifier()
            return identifier
        elif peek().type == 'int_literal':
            return parse_literal()
        elif peek().type == 'bool_literal':
            return parse_bool_literal()
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
            token = peek()
            op = consume()
            right = parse_factors()
            left = ast.TreeOperator(token.source_location, left, op.text, right)
        return left

    def parse_polynomial() -> ast.Expression:
        left: ast.Expression = parse_terms()
        while peek().text in ['+', '-']:
            token = peek()
            op = consume()
            right = parse_terms()
            left = ast.TreeOperator(token.source_location, left, op.text, right)

        return left

    def parse_expression() -> ast.Expression:
        left: ast.Expression = parse_polynomial()
        while peek().text in ['<', '>']:
            token = peek()
            op = consume()
            right = parse_polynomial()
            left = ast.TreeOperator(token.source_location, left, op.text, right)

        return left

    def parse_if_expression() -> ast.Expression:
        token = peek()
        consume('if')
        condition = parse_expression()
        consume('then')
        then_clause = parse_expression()
        if peek().text == 'else':
            consume('else')
            else_clause = parse_expression()
        else:
            else_clause = None

        return ast.IfExpression(token.source_location, condition, then_clause, else_clause)

    def parse_var_declaration() -> ast.VarDeclaration:
        token = peek()
        consume('var')
        name = parse_identifier()
        var_type = parse_var_type()
        consume('=')
        value = parse_expression()

        return ast.VarDeclaration(token.source_location, name, var_type, value
                                  )

    def parse_var_type() -> Type | None:
        if peek().text == ':':
            consume(':')
            if peek().text == 'Int':
                consume('Int')
                return ast.TypeInt('Int')

            elif peek().text == 'Bool':
                consume('Bool')
                return ast.TypeBool('Bool')

            elif peek().text == '=':
                raise Exception(
                    f'{peek().location}: missing type declaration')
            else:
                raise Exception(
                    f'{peek().location}: invalid type declaration "{peek().text}"')
        else:
            return None

    def parse_while_loop() -> ast.WhileLoop:
        token = peek()
        consume('while')
        condition = parse_expression()
        consume('do')
        do_action = parse_expression()
        return ast.WhileLoop(token.source_location, condition, do_action)

    def parse_blocks() -> ast.Block:
        location = peek().location
        consume('{')
        block = ast.Block(
            location,
            statements=[]
        )

        while peek().text != '}':
            if peek().type == 'end':
                raise Exception(f'{peek().location}: expected a "}}"')

            block.statements.append(parse_expression())
            if peek().text == ';':
                consume(';')
                if peek().text == '}':
                    location = peek().location
                    block.statements.append(ast.Literal(location, value=None))
            elif peek_backwards().text == '}':
                continue
            elif peek().text not in ['{', '}']:
                raise Exception(f'{peek().location}: expected ";" or "}}"')

        consume('}')

        return block

    return parse_expression()

# TODO right associativity
