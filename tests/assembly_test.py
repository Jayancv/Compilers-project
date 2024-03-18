import os
import subprocess

from src.compiler.assembler import assemble
from src.compiler.assembly_generator import generate_assembly
from src.compiler.ir_generator import generate_ir
from src.compiler.parser import parser
from src.compiler.symTab import SymTab, root_types
from src.compiler.tokenizer import tokenize
from src.compiler.type_checker import typecheck


def test_generate_ir_var() -> None:
    nodes = parser(tokenize('{ var x = true; if x then 1 else 2; print_int(x) }'))
    if nodes is None:
        raise Exception('Failed to parse input')
    typecheck(nodes, SymTab(locals={}, parent=None))
    expected = ['LoadBoolConst(True, x1)',
                'Copy(x1, x2)',
                'CondJump(x2, Label(L1), Label(L2))',
                'Label(L1)',
                'LoadIntConst(1, x3)',
                'Jump(Label(L3))',
                'Label(L2)',
                'LoadIntConst(2, x4)',
                'Copy(x4, x3)',
                'Label(L3)',
                'Call(print_int, [x2], x5)']

    ir_instructions = generate_ir(root_types, nodes)
    output = [str(ins) for ins in ir_instructions['main']]
    assert output == expected

    asm_code = generate_assembly(ir_instructions)
    print(asm_code)
    assemble(asm_code, 'compile_program')
    proc = subprocess.run([f'{os.getcwd()}/compile_program'], capture_output=True, text=True)
    output = proc.stdout
    if output:
        assert output.strip() == '1'
    else:
        raise Exception(f'Test failed')
