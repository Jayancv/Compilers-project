from src.compiler import ir, ast
from src.compiler.ir import IRVar, Instruction, Label
import numpy as np


def generate_ir(root_node: ast.Expression) -> list[Instruction]:
    next_var_num = 1
    next_lbl_num = 1
    instructions = []

    def new_var() -> IRVar:
        nonlocal next_var_num
        var = IRVar(f'x{next_var_num}')
        next_var_num += 1
        return var

    def new_lbl() -> Label:
        nonlocal next_lbl_num
        label = Label(f'L{next_lbl_num}')
        next_lbl_num += 1
        return label

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
            case ast.IfExpression():
                if node.else_clause is None:
                    raise Exception("Not yet handled")  # TODO handle this
                else:
                    lbl_then = new_lbl()
                    lbl_else = new_lbl()
                    lbl_end = new_lbl()

                    var_cond = visit(node.condition)
                    instructions.append(ir.CondJump(var_cond, lbl_then, lbl_else))
                    instructions.append(lbl_then)
                    var_result = visit(node.then_clause)
                    instructions.append(ir.Jump(lbl_end))

                    instructions.append(lbl_else)
                    var_else_result = visit(node.else_clause)
                    instructions.append(ir.Copy(var_else_result, var_result))
                    instructions.append(lbl_end)
                    return var_result
            case _:
                raise Exception(f"Unsupported AST Node: {node}")

    res = visit(root_node)

    # handle boolean and unit result
    instructions.append(ir.Call(IRVar("print_int"), [res], new_var()))
    return instructions
