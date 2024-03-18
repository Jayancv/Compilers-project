from src.compiler import ast
from src.compiler.symTab import SymTab, find_context
from src.compiler.types import Type, Int, Bool, Unit, FunctionType


def typecheck(node: ast.Expression | None, symtab: SymTab) -> Type:
    def set_node_type(node: ast.Expression, type: Type) -> Type:
        node.type = type
        return type

    match node:
        case ast.Literal():
            if isinstance(node.value, bool):
                return set_node_type(node, Bool)
            elif isinstance(node.value, int):
                return set_node_type(node, Int)
            elif node.value is None:
                return set_node_type(node, Unit)
            else:
                raise Exception(f"Can not determine the type of literal {node.value} at {node.location.__str__()}")

        case ast.TreeOperator():
            l = typecheck(node.left, symtab)
            r = typecheck(node.right, symtab)

            if node.operator in ['+', '-', '*', '/']:
                if l is not Int or r is not Int:
                    raise Exception(
                        f"Operator {node.operator} expected two Ints, got {l} and {r} at {node.location.__str__()}")
                else:
                    return set_node_type(node, Int)

            elif node.operator in ['<', '>', '<=', '>=']:
                if l is not Int or r is not Int:
                    raise Exception(
                        f"Operator {node.operator} expected two Ints, got {l} and {r} at {node.location.__str__()}")
                else:
                    return set_node_type(node, Bool)

            elif node.operator in ['or', 'and']:
                if l is not Bool or r is not Bool:
                    raise Exception(
                        f"Operator {node.operator} expected two Bool, got {l} and {r} at {node.location.__str__()}")
                else:
                    return set_node_type(node, Bool)

            elif node.operator in ['==', '!=']:
                if l not in [Int, Bool] or r not in [Int, Bool]:
                    raise Exception(
                        f'Types must be either Int or Bool at {node.location.__str__()}')
                if l != r:
                    raise Exception(
                        f'Types {l} and {r} do not match at {node.location.__str__()}')
                else:
                    return set_node_type(node, Bool)

            elif node.operator == '=':
                if l != r:
                    raise Exception(
                        f'Types {l} and {r} do not match at {node.location.__str__()}')
                else:
                    return set_node_type(node, l)

            else:
                raise Exception(f"Unknown operator {node.operator} at {node.location.__str__()}")

        case ast.IfExpression():
            con = typecheck(node.condition, symtab)
            if con is not Bool:
                raise Exception(f"'If' statement condition was {con} at {node.location.__str__()} ")
            then_cl = typecheck(node.then_clause, symtab)
            if node.else_clause is None:
                return set_node_type(node, Unit)
            else_cl = typecheck(node.else_clause, symtab)
            if then_cl != else_cl:
                raise Exception(
                    f"'then' and 'else' having different types: {then_cl} and {else_cl} at {node.location.__str__()}")
            return set_node_type(node, then_cl)

        # TODO need to update this
        case ast.Identifier():
            context = find_context(symtab, node.name)
            if context is not None:
                return context.locals[node.name]
            else:
                raise Exception(f'Unknown identifier {node.name}')

        case ast.VarDeclaration():
            if node.name.name in symtab.locals:
                raise Exception(
                    f'Variable {node.name.name} has already been declared')

            value_type = typecheck(node.value, symtab)

            if node.var_type is None:
                symtab.locals[node.name.name] = value_type
                return set_node_type(node, Unit)

            elif isinstance(node.var_type, ast.TypeInt):
                if value_type != Int:
                    raise Exception(
                        f'{node.location}: type error, expected Int')
                symtab.locals[node.name.name] = Int
                return set_node_type(node, Int)

            elif isinstance(node.var_type, ast.TypeBool):
                if value_type != Bool:
                    raise Exception(
                        f'{node.location}: type error, expected Bool')
                symtab.locals[node.name.name] = Bool
                return set_node_type(node, Bool)

            else:
                raise Exception(f'{node.location}: unknown type {node.type}')

        case ast.UnaryOp():
            value_type = typecheck(node.expr, symtab)

            if node.operator == 'not' and value_type is not Bool:
                raise Exception(
                    f'Expected type Bool, got {value_type} at {node.location.__str__()}')
            elif node.operator == '-' and value_type is not Int:
                raise Exception(
                    f'Expected type Int, got {value_type} at {node.location.__str__()}')
            return set_node_type(node, value_type)

        case ast.Block():
            context = symtab
            if symtab.parent is not None:
                context = SymTab(locals={}, parent=symtab)

            for statement in node.statements:
                typecheck(statement, context)

            return set_node_type(node, Unit)

        case ast.FunctionCall():
            args = []
            return_type = Unit

            for arg in node.args:
                arg_type = typecheck(arg, symtab)
                args.append(arg_type)

            if node.name is not None:
                fun_type = FunctionType(args, return_type)
                symtab.locals[node.name.name] = fun_type
                return set_node_type(node, fun_type)
            else:
                raise Exception(f'Function call has no name at {node.location.__str__()}')

        case ast.WhileLoop():
            condition = typecheck(node.condition, symtab)
            if condition is not Bool:
                raise Exception(
                    f'{node.location}: while loop condition must be type Bool, got {condition} at {node.location.__str__()}')

            typecheck(node.do_action, symtab)

            return set_node_type(node, Unit)

        case _:
            raise Exception(f"Unsupported TAS Node {node} at {node.location.__str__()}")

# TODO Add type error exceptions separately
# Add type to AST node
