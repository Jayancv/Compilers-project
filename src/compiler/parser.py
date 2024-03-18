from typing import List

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

    def parse_module() -> ast.Module:
        expressions: List[ast.Expression] = []
        functions: List[ast.FunctionDef] = []

        while pos < len(tokens):
            if peek().text == 'fun':
                fun = parse_fun_definition()
                functions.append(fun)
            else:
                expression = parse_expression()
                expressions.append(expression)

        return ast.Module(functions=functions, expr=ast.Block(SourceLocation(line=1, column=1), expressions))

    def parse_fun_definition() -> ast.FunctionDef:
        token = peek()
        consume('fun')
        name = parse_identifier()
        consume('(')
        params: list[ast.Identifier] = []
        param_types: list[ast.BasicType] = []

        while peek().text != ')':
            if len(params) > 0:
                consume(',')
            param = parse_identifier()
            consume(':')
            param_type = ast.BasicType(consume().text)

            params.append(param)
            param_types.append(param_type)

        consume(')')
        consume(':')
        return_type = ast.BasicType(consume().text)
        body = parse_blocks()
        return ast.FunctionDef(token.source_location, name, param_types, body, return_type)

    def parse_return() -> ast.Return:
        token = peek()
        consume('return')
        if peek().text == '}':
            value = None
        else:
            value = parse_expression()
        if peek().text != '}':
            raise Exception(f'Return statement must be the last statement in a block')
        return ast.Return(token.source_location, value)

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

    def parse_break_and_continue() -> ast.Expression:
        token = peek()
        if token.text == 'break':
            consume('break')
            name = 'break'
        else:
            consume('continue')
            name = 'continue'
        return ast.BreakContinue(token.source_location, name)

    def parse_bool_literal() -> ast.Literal:
        token = peek()
        if token.type != 'bool_literal':
            raise Exception(f'{token.source_location}: expected a boolean value')

        consume()
        if token.text.lower() == 'true':
            value = True
        elif token.text.lower() == 'false':
            value = False
        else:
            raise Exception(f'{token.source_location}: expected boolean true/True or false/False')

        return ast.Literal(value=value, location=token.source_location)

    def parse_unary() -> ast.Expression:
        token = peek()
        if peek().text in ['-', 'not']:
            operator_token = consume()
            operator = operator_token.text
            expr = parse_factors()
            return ast.UnaryOp(token.source_location, operator, expr)

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
            elif peek().text in ['break', 'continue']:
                return parse_break_and_continue()
        elif peek().type == 'identifier':
            identifier = parse_identifier()
            if peek().text == '(':  # function calls
                function_call = parse_function_call(identifier)
                function_call.name = identifier
                return function_call
            return identifier
        elif peek().type == 'int_literal':
            return parse_literal()
        elif peek().type == 'bool_literal':
            return parse_bool_literal()
        if peek().text in ['-', 'not']:
            return parse_unary()
        else:
            raise Exception(f'Unexpected "{peek().text}" ')

    def parse_parenthesize_expression() -> ast.Expression:
        consume('(')
        expr = parse_expression()
        consume(')')
        return expr

    # def parse_terms() -> ast.Expression:
    #     left: ast.Expression = parse_factors()
    #     while peek().text in ['*', '/', '%']:
    #         token = peek()
    #         op = consume()
    #         right = parse_factors()
    #         left = ast.TreeOperator(token.source_location, left, op.text, right)
    #     return left
    #
    # def parse_polynomial() -> ast.Expression:
    #     left: ast.Expression = parse_terms()
    #     while peek().text in ['+', '-']:
    #         token = peek()
    #         op = consume()
    #         right = parse_terms()
    #         left = ast.TreeOperator(token.source_location, left, op.text, right)
    #
    #     return left
    #
    # def parse_comparison() -> ast.Expression:
    #     left: ast.Expression = parse_polynomial()
    #     while peek().text in ['<', '>', '<=', '>=']:
    #         token = peek()
    #         op = consume()
    #         right = parse_polynomial()
    #         left = ast.TreeOperator(token.source_location, left, op.text, right)
    #
    #     return left
    #
    # def parse_equality() -> ast.Expression:
    #     left: ast.Expression = parse_comparison()
    #     if peek().text in ['==', '!=']:
    #         token = peek()
    #         op = consume()
    #         right = parse_comparison()
    #         left = ast.TreeOperator(token.source_location, left, op.text, right)
    #
    #     return left
    #
    # def parse_and() -> ast.Expression:
    #     left: ast.Expression = parse_equality()
    #     while peek().text in ['and']:
    #         token = peek()
    #         op = consume()
    #         right = parse_equality()
    #         left = ast.TreeOperator(token.source_location, left, op.text, right)
    #
    #     return left
    #
    # def parse_or() -> ast.Expression:
    #     left: ast.Expression = parse_and()
    #     while peek().text in ['or']:
    #         token = peek()
    #         op = consume()
    #         right = parse_and()
    #         left = ast.TreeOperator(token.source_location, left, op.text, right)
    #
    #     return left

    def parse_binary_expression(operators: list[str], next_level_parser) -> ast.Expression:
        left: ast.Expression = next_level_parser()

        while peek().text in operators:
            token = peek()
            op = consume()
            right = next_level_parser()
            left = ast.TreeOperator(token.source_location, left, op.text, right)

        return left

    def parse_terms() -> ast.Expression:
        return parse_binary_expression(['*', '/', '%'], parse_factors)

    def parse_polynomial() -> ast.Expression:
        return parse_binary_expression(['+', '-'], parse_terms)

    def parse_comparison() -> ast.Expression:
        return parse_binary_expression(['<', '>', '<=', '>='], parse_polynomial)

    def parse_equality() -> ast.Expression:
        return parse_binary_expression(['==', '!='], parse_comparison)

    def parse_and() -> ast.Expression:
        return parse_binary_expression(['and'], parse_equality)

    def parse_or() -> ast.Expression:
        return parse_binary_expression(['or'], parse_and)

    def parse_expression() -> ast.Expression:
        left: ast.Expression = parse_or()
        while peek().text in ['=']:
            token = peek()
            op = consume()
            right = parse_expression_right()
            left = ast.TreeOperator(token.source_location, left, op.text, right)

        return left

    def parse_expression_right() -> ast.Expression:
        left: ast.Expression = parse_equality()
        if peek().text in ['=']:
            token = peek()
            op = consume()
            right = parse_expression_right()
            return ast.TreeOperator(token.source_location, left, op.text, right)

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

        return ast.VarDeclaration(token.source_location, name, var_type, value)

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
        location = peek().source_location
        consume('{')
        block = ast.Block(location, statements=[])

        while peek().text != '}':
            if peek().type == 'end':
                raise Exception(f'{peek().source_location}: expected a "}}"')
            if peek().text == 'return':
                block.statements.append(parse_return())
                semicolon = False
            else :
                statement = parse_expression()
                block.statements.append(statement)

            # block.statements.append(parse_expression())
            if peek().text == ';':
                consume(';')
                if peek().text == '}':
                    location = peek().source_location
                    block.statements.append(ast.Literal(location, value=None))
            elif tokens[pos - 1].text == '}':
                continue
            elif peek().text not in ['{', '}']:
                raise Exception(f'{peek().source_location}: expected ";" or "}}"')

        consume('}')

        return block

    def parse_function_call(identifier) -> ast.FunctionCall:
        consume('(')
        func = ast.FunctionCall(
            location=identifier.location,
            call=identifier,
            args=[]
        )

        while peek().text != ')':
            if peek().text == ',':
                consume(',')

            func.args.append(parse_expression())

        consume(')')
        return func

    return parse_expression()

