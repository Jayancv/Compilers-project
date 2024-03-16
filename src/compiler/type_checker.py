from src.compiler import ast
from src.compiler.types import Type, Int, Bool, Unit


def typecheck(node: ast.Expression) -> Type:
    match node:
        case ast.Literal():
            if isinstance(node.value, int):
                return Int
            else:
                raise Exception(f"Can not determine the type of literal {node.value}")
        case ast.TreeOperator():
            l = typecheck(node.left)
            r = typecheck(node.right)

            if node.operator in ['+', '-', '*', '/']:
                if l is not Int or r is not Int:
                    raise Exception(f"Operator {node.operator} expected two Ints, got {l} and {r}")
                else:
                    return Int

            elif node.operator in ['<', '>']:
                if l is not Int or r is not Int:
                    raise Exception(f"Operator {node.operator} expected two Ints, got {l} and {r}")
                else:
                    return Bool
            else:
                raise Exception(f"Unknown operator {node.operator} ")
        case ast.IfExpression():
            con = typecheck(node.condition)
            if con is not Bool:
                raise Exception(f"'If' statement condition was {con}")
            then_cl = typecheck(node.then_clause)
            if node.else_clause is None:
                return Unit
            else_cl = typecheck(node.else_clause)
            if then_cl != else_cl:
                raise Exception(f"'then' and 'else' having different types: {then_cl} and {else_cl}")
            return then_cl

        case _:
            raise Exception(f"Unsupported TAS Node {node}")

# TODO Add type error exceptions separately
# Add type to AST node
