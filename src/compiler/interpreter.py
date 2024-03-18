from typing import Any

from src.compiler import ast
from src.compiler.symTab import find_top_level_context, SymTab, find_context

Value = int | bool | None


def interpret(st: SymTab, node: ast.Expression) -> Value:
    operators = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y,
        '/': lambda x, y: x // y,
        '<': lambda x, y: x < y,
        # Add more operators as needed
    }

    top_context = find_top_level_context(st)

    match node:
        case ast.Literal():
            return node.value

        case ast.Identifier():
            context = find_context(st, node.name)
            if context is not None:
                return context.locals[node.name]
            else:
                raise Exception(f'Undefined variable name {node.name} at : {node.location.__str__()}')

        case ast.TreeOperator():
            if node.operator == '=':
                value = interpret(st, node.right)
                if isinstance(node.left, ast.Identifier):
                    context = find_context(st, node.left.name)
                    if context is not None:
                        context.locals[node.left.name] = value
                        return value
                    else:
                        raise Exception(f'Undefined variable name {node.left.name}')

                else:
                    raise Exception(f'Only identifiers allowed as variable names.')

            elif node.operator in top_context.locals:

                a: Any = interpret(st, node.left)
                # if node.operator in operators:
                #     return operators[node.operator](a, b)
                # if node.operator == '+':
                #     return a + b
                # elif node.operator == '-':
                #     return a - b
                # elif node.operator == '*':
                #     return a * b
                # elif node.operator == '/':
                #     return a // b
                # elif node.operator == '<':
                #     return a < b
                # elif node.operator == '>':
                #     return a > b
                op = top_context.locals[node.operator]

                if not callable(op):
                    raise Exception(f'{node.operator} is not a inbuilt function')
                elif node.op == 'and':  # optimizing 'and & 'or' operation with one arg evaluating
                    if a is False:
                        return False
                elif node.op == 'or':
                    if a is True:
                        return True
                b: Any = interpret(st, node.right)

                return op(a, b)

        case ast.IfExpression():
            if node.else_clause is not None:
                if interpret(st, node.condition):
                    return interpret(st, node.then_clause)
                else:
                    return interpret(st, node.else_clause)
            else:
                if interpret(st, node.condition):
                    return interpret(st, node.then_clause)
                else:
                    return None

        case ast.VarDeclaration():
            if not isinstance(node.name, ast.Identifier):
                raise Exception('Only identifiers allowed as variable names')
            elif node.name.name in st.locals:
                raise Exception(f'Variable {node.name.name} already exists.')
            else:
                st.locals[node.name.name] = interpret(st, node.value)
                return None

        case ast.Block():
            result = None
            context = SymTab(locals={}, parent=st)
            for statement in node.statements:
                result = interpret(context, statement)

            return result

        case ast.WhileLoop():
            cond = interpret(st, node.condition)
            if cond is True:
                interpret(st, node.do_action)
                return interpret(st, node)
            elif cond is False:
                return None
            else:
                raise Exception(
                    f'Failed to evaluate condition')

        case ast.FunctionCall():
            if isinstance(node.call, ast.Identifier):
                name = node.call.name
                if name in top_context.locals:  # only built in functions supported for now
                    fun = top_context.locals[name]
                    if not callable(fun):
                        raise Exception(
                            f'{node.location}: {fun} is not a function')
                    args = []
                    for arg in node.args:
                        args.append(interpret(st, arg))
                    result = fun(*args)
                    return result
                else:
                    raise Exception(
                        f'Unknown function call {name}')
            else:
                raise Exception(
                    f'Function name has to be an Identifier')

        case _:
            raise Exception(f'Unsupported AST node {node}')
