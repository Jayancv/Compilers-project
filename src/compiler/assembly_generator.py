import dataclasses

from src.compiler import ir
from src.compiler.intrinsics import all_intrinsics, IntrinsicArgs


def generate_assembly(instructions: dict[str, list[ir.Instruction]]) -> str:
    code_lines = []

    def emit(line: str) -> None:
        code_lines.append(line)

    locals = Locals(get_all_ir_variables(instructions))
    param_registers = ['%rdi', '%rsi', '%rdx', '%rcx', '%r8', '%r9']

    emit('.global main')
    emit('.type main @function')
    emit('.extern print_int')
    emit('.extern print_bool')
    emit('.extern read_int')

    # emit('.section .text')
    # emit('main:')
    # emit('pushq %rbp')
    # emit('movq %rsp, %rbp')
    # emit(f'subq ${locals.stack_used()}, %rsp')

    for fun_name, instructions_set in instructions.items():
        param_count = 0

        emit(f'{fun_name}:')
        emit('pushq %rbp')
        emit('movq %rsp, %rbp')
        emit(f'subq ${locals.stack_used()}, %rsp')

        for ins in instructions_set:
            emit('#' + str(ins))
            match ins:
                case ir.Label():
                    emit(f'.L{ins.name}:')
                case ir.LoadIntConst():
                    emit(f'movq ${ins.value}, {locals.get_ref(ins.dest)}')
                    # TODO  ^ dosent workt if ins.value is too large
                case ir.LoadBoolConst():
                    emit(f'movq ${int(ins.value)}, {locals.get_ref(ins.dest)}')
                case ir.Copy():
                    emit(f'movq  {locals.get_ref(ins.source)}, %rax')
                    emit(f'movq %rax, {locals.get_ref(ins.dest)}')
                case ir.Call():
                    if (intrinsic := all_intrinsics.get(ins.func.name)) is not None:
                        args = IntrinsicArgs(
                            arg_refs=[locals.get_ref(a) for a in ins.args],
                            result_register='%rax',
                            emit=emit
                        )
                        intrinsic(args)
                        emit(f'movq %rax, {locals.get_ref(ins.dest)}')

                    else:
                        for i, arg in enumerate(ins.args):
                            emit(f'movq {locals.get_ref(arg)}, {param_registers[i]}')
                        emit(f'call {ins.func.name}')
                        emit(f'movq %rax, {locals.get_ref(ins.dest)}')

                case ir.Jump():
                    emit(f'jmp .L{ins.label.name}')
                case ir.CondJump():
                    emit(f'cmpq $0, {locals.get_ref(ins.cond)}')
                    emit(f'jne .L{ins.then_label.name}')
                    emit(f'jmp .L{ins.else_label.name}')

                case ir.Return():
                    emit(f'movq {locals.get_ref(ins.value)}, %rax')
                case _:
                    print(ins)
                    raise Exception(f'Unknown Instruction : {type(ins)}')
        if fun_name == 'main':
            emit('movq $0, %rax')
        # emit('movq $0, %rax')
        emit('movq %rbp, %rsp')
        emit('popq %rbp')
        emit('ret')
        emit('')

    return "\n".join(code_lines)


def get_all_ir_variables(instruction_set: dict[str, list[ir.Instruction]]) -> list[ir.IRVar]:
    result_list: list[ir.IRVar] = []
    result_set: set[ir.IRVar] = set()

    def add(v: ir.IRVar) -> None:
        if v not in result_set:
            result_list.append(v)
            result_set.add(v)

    for instructions in instruction_set.values():
        for insn in instructions:
            for field in dataclasses.fields(insn):
                value = getattr(insn, field.name)
                if isinstance(value, ir.IRVar):
                    add(value)
                elif isinstance(value, list):
                    for v in value:
                        if isinstance(v, ir.IRVar):
                            add(v)
    return result_list


class Locals:
    """Knows the memory location of every local variable."""
    _var_to_location: dict[ir.IRVar, str]
    _stack_used: int

    def __init__(self, variables: list[ir.IRVar]) -> None:
        self._var_to_location = {}
        self._stack_used = 8
        for v in variables:
            if v not in self._var_to_location:
                self._var_to_location[v] = f'-{self._stack_used}(%rbp)'
                self._stack_used += 8

    def get_ref(self, v: ir.IRVar) -> str:
        """Returns an Assembly reference like `-24(%rbp)`
        for the memory location that stores the given variable"""
        return self._var_to_location[v]

    def stack_used(self) -> int:
        """Returns the number of bytes of stack space needed for the local variables."""
        return self._stack_used
