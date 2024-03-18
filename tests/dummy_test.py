# This test file only exists so you can check that the test runner works.
# You can delete it after writing your first real test.
import os
import subprocess

from src.compiler.assembler import assemble
from src.compiler.assembly_generator import generate_assembly
from src.compiler.ir_generator import generate_ir
from src.compiler.parser import parser
from src.compiler.symTab import root_types, SymTab
from src.compiler.tokenizer import tokenize
from src.compiler.type_checker import typecheck


def test_dummy() -> None:
    path = '../resource'
    files = [os.path.join(path, file) for file in os.listdir(path) if os.path.isfile(os.path.join(path, file))]

    for f in files:
        if(os.path.isdir(f)):
            continue
        with open(f'{path}/{f}') as file:
            first_line = file.readline().strip()  # Strip to remove leading/trailing whitespaces

            # Read the rest of the content
            remaining_content = file.read()

            # lines = file.readlines()
            # i = 0
            # count = 0
            # while i < len(lines):
            #     inpt = lines[i].strip().split('#')[1]
            #     expected = lines[i + 1].strip().split('#')[1]
            #     count += 1
            #     i = i + 3
            #     run_test_case(count, f, (inpt, expected))
            execute_code(remaining_content, f, first_line)


def execute_code(source_code, test_namespace, expected):
    tokens = tokenize(source_code)
    ast_nodes = parser(tokens)
    typecheck(ast_nodes, SymTab(locals={}, parent=None))
    irs = generate_ir(root_types, ast_nodes)
    for func, irs in irs.items():
        print(f"function : {func}:")
        print("\n".join([str(ins) for ins in irs]))
    asm_code = generate_assembly(irs)
    assemble(asm_code, 'compile_program')

    proc = subprocess.run([f'{os.getcwd()}/compile_program'], capture_output=True, text=True)
    output = proc.stdout
    if output:
        assert output.strip() == expected
    else:
        raise Exception(f'Test failed')
