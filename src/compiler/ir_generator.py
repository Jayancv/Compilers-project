from compiler import ir, ast
from compiler.ir import IRVar, Instruction
import numpy as np


def generate_ir(root_node: ast.Expression) -> list[Instruction]:
    next_var_num = 1
    instructions = []

    def new_var() -> IRVar:
        nonlocal next_var_num
        var = IRVar(f'x{next_var_num}')
        next_var_num += 1
        return var

    def visit(node: ast.Expression) -> IRVar:
        match node:
            case ast.Literal():
                var = new_var()
                instructions.append(ir.LoadIntConst(node.value, var))
                return var

            case ast.TreeOperator():
                var_left = visit(node.left)
                var_right = visit(node.right)
                var_result = new_var()
                instructions.append(ir.Call(
                    func=IRVar(node.operator),
                    args=[var_left, var_right],
                    dest=var_result
                ))
                return var_result
            case _:
                raise Exception(f"Unsupported AST Node: {node}")

    visit(root_node)
    return instructions
