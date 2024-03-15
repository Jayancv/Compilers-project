import dataclasses

from compiler import ir
from compiler.intrinsics import all_intrinsics, IntrinsicArgs


def generate_assembly(instructions: list[ir.Instruction]) -> str:
    code_lines = []

    def emit(line: str) -> None:
        code_lines.append(line)

    locals = Locals(get_all_ir_variables(instructions))

    emit('.global main')
    emit('.type main @function')
    emit('.extern print_int')

    emit('.section .text')
    emit('main:')
    emit('pushq %rbp')
    emit('movq %rsp, %rbp')
    emit(f'subq ${locals.stack_used()}, %rsp')

    for ins in instructions:

        emit('#' + str(ins))
        match ins:
            case ir.Label():
                emit(f'.L{ins.name}:')
            case ir.LoadIntConst():
                emit(f'movq ${ins.value}, {locals.get_ref(ins.dest)}')
                # TODO  ^ dosent workt if ins.value is too large
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
                    assert ins.func.name == 'print_int', "TODO: Other Functionalities"
                    assert len(ins.args) == 1, "TODO :  support more args"
                    emit(f'movq {locals.get_ref(ins.args[0])}, %rdi')
                    emit('call print_int')
            case ir.Jump():
                emit(f'jmp .L{ins.label.name}')
            case ir.CondJump():
                emit(f'cmpq $0, {locals.get_ref(ins.cond)}')
                emit(f'jne .L{ins.then_label.name}')
                emit(f'jmp .L{ins.else_label.name}')

            case _:
                print (ins)
                raise Exception(f'Unknown Instruction : {type(ins)}')

    emit('movq $0, %rax')
    emit('movq %rbp, %rsp')
    emit('popq %rbp')
    emit('ret')
    emit('')

    return "\n".join(code_lines)


def get_all_ir_variables(instructions: list[ir.Instruction]) -> list[ir.IRVar]:
    result_list: list[ir.IRVar] = []
    result_set: set[ir.IRVar] = set()

    def add(v: ir.IRVar) -> None:
        if v not in result_set:
            result_list.append(v)
            result_set.add(v)

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