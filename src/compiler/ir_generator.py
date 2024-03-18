from src.compiler import ir, ast
from src.compiler.ir import IRVar, Instruction, Label

from src.compiler.symTab import SymTab
from src.compiler.tokenizer import SourceLocation
from src.compiler.types import Bool, Int, Type, Unit


def generate_ir(root_types: dict[IRVar, Type], root_node: ast.Expression) -> dict[str, list[Instruction]]:
    var_types: dict[IRVar, Type] = root_types.copy()  # take a local copy
    # 'var_unit' is used when an expression's type is 'Unit'.
    var_unit = IRVar('unit')
    var_types[var_unit] = Unit

    next_var_num = 1
    next_lbl_num = 1
    instructions: dict[str, list[ir.Instruction]] = {'main': []}
    loop_labels: list[tuple[ir.Label, ir.Label]] = []

    def new_var(type: Type) -> IRVar:
        nonlocal next_var_num
        var = IRVar(f'x{next_var_num}')
        var_types[var] = type
        next_var_num += 1
        return var

    def new_lbl(location: SourceLocation) -> Label:
        nonlocal next_lbl_num
        label = Label(location, f'L{next_lbl_num}')
        next_lbl_num += 1
        return label

    def visit(st: SymTab, node: ast.Expression, func_name: str) -> IRVar:
        match node:
            case ast.Literal():
                match node.value:
                    case bool():
                        var = new_var(Bool)
                        instructions[func_name].append(ir.LoadBoolConst(node.location, node.value, var))
                    case int():
                        var = new_var(Int)
                        instructions[func_name].append(ir.LoadIntConst(node.location, node.value, var))
                    case None:
                        var = var_unit
                    case _:
                        raise Exception(f"Unsupported literal: {type(node.value)} at {node.location.__str__()}")
                return var

            case ast.Identifier():
                return st.require(node.name)

            case ast.TreeOperator():
                var_left = visit(st, node.left, func_name)

                var_op = st.require(node.operator)
                loc = node.location
                if node.operator in ('and', 'or'):
                    l_right = new_lbl(loc)
                    l_skip = new_lbl(loc)
                    l_end = new_lbl(loc)
                    if node.operator == 'and':
                        instructions[func_name].append(ir.CondJump(loc, var_left, l_right, l_skip))
                    else:
                        instructions[func_name].append(ir.CondJump(loc, var_left, l_skip, l_right))
                    instructions[func_name].append(l_right)
                    var_right = visit(st, node.right, func_name)
                    result = new_var(Bool)
                    instructions[func_name].append(ir.Copy(loc, var_right, result))
                    instructions[func_name].append(ir.Jump(loc, l_end))

                    instructions[func_name].append(l_skip)
                    if node.operator == 'and':
                        instructions[func_name].append(ir.LoadBoolConst(loc, False, result))
                    else:
                        instructions[func_name].append(ir.LoadBoolConst(loc, True, result))
                    instructions[func_name].append(ir.Jump(loc, l_end))

                    instructions[func_name].append(l_end)

                var_right = visit(st, node.right, func_name)
                if node.operator == '=':
                    if not isinstance(node.left, ast.Identifier):
                        raise Exception(f'Expected an identifier at {node.location.__str__()}')
                    instructions[func_name].append(ir.Copy(node.location, var_right, var_left))
                    return var_right
                else:
                    var_result = new_var(node.type)
                    instructions[func_name].append(ir.Call(
                        node.location,
                        func=IRVar(node.operator),
                        args=[var_left, var_right],
                        dest=var_result
                    ))
                    return var_result
            case ast.IfExpression():
                if node.else_clause is None:
                    l_then = new_lbl(node.location)
                    l_end = new_lbl(node.location)
                    var_cond = visit(st, node.condition, func_name)
                    instructions[func_name].append(ir.CondJump(node.location, var_cond, l_then, l_end))
                    instructions[func_name].append(l_then)
                    visit(st, node.true_branch, func_name)
                    instructions[func_name].append(l_end)
                    return var_unit
                else:
                    lbl_then = new_lbl(node.location)
                    lbl_else = new_lbl(node.location)
                    lbl_end = new_lbl(node.location)

                    var_cond = visit(st, node.condition, func_name)
                    instructions[func_name].append(ir.CondJump(node.location, var_cond, lbl_then, lbl_else))
                    instructions[func_name].append(lbl_then)
                    var_result = visit(st, node.then_clause, func_name)
                    instructions[func_name].append(ir.Jump(node.location, lbl_end))

                    instructions[func_name].append(lbl_else)
                    var_else_result = visit(st, node.else_clause, func_name)
                    instructions[func_name].append(ir.Copy(node.location, var_else_result, var_result))
                    instructions[func_name].append(lbl_end)
                    return var_result
            case ast.UnaryOp():
                var_op = st.require('unary_' + node.operator)
                var_value = visit(st, node.expr, func_name)
                if node.operator == 'not':
                    var_result = new_var(Bool)
                elif node.operator == '-':
                    var_result = new_var(Int)
                else:
                    raise Exception(f'Invalid unary operator {node.operator}')
                instructions[func_name].append(ir.Call(node.location, var_op, [var_value], var_result))
                return var_result

            case ast.VarDeclaration():
                value = visit(st, node.value, func_name)
                var = new_var(node.value.type)
                st.add_local(node.name.name, var)
                instructions[func_name].append(ir.Copy(node.location, value, var))
                return var_unit

            case ast.Block():
                stb = SymTab(locals=root_types, parent=st)
                for statement in node.statements:
                    visit(stb, statement, func_name)
                return var_unit

            case ast.FunctionCall():
                if node.call is None:
                    raise Exception(f'Function has no name')
                f_var = st.require(node.call.name)
                arg_vars = []
                for arg in node.args:
                    arg_var = visit(st, arg, func_name)
                    arg_vars.append(arg_var)
                result_var = new_var(Unit)
                instructions[func_name].append(ir.Call(node.location, f_var, arg_vars, result_var))
                return result_var

            case ast.WhileLoop():
                l_start = new_lbl(node.location)
                l_do_action = new_lbl(node.location)
                l_end = new_lbl(node.location)

                loop_labels.append((l_start, l_end))

                instructions[func_name].append(l_start)
                condition = visit(st, node.condition, func_name)
                instructions[func_name].append(ir.CondJump(node.location, condition, l_do_action, l_end))

                instructions[func_name].append(l_do_action)
                visit(st, node.do_action, func_name)
                instructions[func_name].append(ir.Jump(node.location, l_start))

                instructions[func_name].append(l_end)
                loop_labels.pop()

                return var_unit

            case ast.BreakContinue():
                if not loop_labels:
                    raise Exception(f"While loop not available at {node.location.__str__()}")

                l_start, l_end = loop_labels[-1]
                if node.name == 'break':
                    instructions[func_name].append(ir.Jump(node.location, l_end))
                else:
                    instructions[func_name].append(ir.Jump(node.location, l_start))
                return var_unit

            case _:
                raise Exception(f"Unsupported AST Node: {node} at {node.location.__str__()}")

    root_symtab = SymTab(locals={str: IRVar}, parent=None)
    for v in root_types.keys():
        root_symtab.add_local(v.name, v)
    res = visit(root_symtab, root_node, 'main')

    # handle boolean and unit result
    if var_types[res] == Int:
        instructions['main'].append(ir.Call(root_node.location, IRVar("print_int"), [res], new_var(Int)))
    elif var_types[res] == Bool:
        instructions['main'].append(ir.Call(root_node.location, IRVar("print_bool"), [res], new_var(Bool)))
    # elif var_types[res] == Unit:
    #     instructions['main'].append(ir.Return(root_node.location, None))
    return instructions
