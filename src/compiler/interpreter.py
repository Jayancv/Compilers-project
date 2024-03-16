from typing import Any

from src.compiler import ast

Value = int | bool | None


def interpret(node: ast.Expression) -> Value:
    operators = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x // y,
        '<': lambda x, y: x < y,
        # Add more operators as needed
    }
    match node:
        case ast.Literal():
            return node.value

        case ast.TreeOperator():
            a : Any = interpret(node.left)
            b : Any = interpret(node.right)
            # if node.operator in operators:
            #     return operators[node.operator](a, b)
            if node.operator == '+':
                return a + b
            elif node.operator == '-':
                return a - b
            elif node.operator == '*':
                return a * b
            elif node.operator == '/':
                return a // b
            elif node.operator == '<':
                return a < b
            elif node.operator == '>':
                return a > b


            else:
                # Handle the case when the operator is not recognized
                raise ValueError(f"Unsupported operator: {node.operator}")
        case ast.IfExpression():
            if node.else_clause is not None:
                if interpret(node.condition):
                    return interpret(node.then_clause)
                else:
                    return interpret(node.else_clause)
            else:
                if interpret(node.condition):
                    return interpret(node.then_clause)
                else:
                    return None

        case _:
            raise Exception(f'Unsupported AST node {node}')
