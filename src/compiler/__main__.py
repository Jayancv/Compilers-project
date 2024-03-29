import sys

from src.compiler.assembler import assemble
from src.compiler.assembly_generator import generate_assembly
from src.compiler.interpreter import interpret
from src.compiler.ir_generator import generate_ir
from src.compiler.parser import parser
from src.compiler.symTab import SymTab, root_types
from src.compiler.tokenizer import tokenize
from src.compiler.type_checker import typecheck

# TODO(student): add more commands as needed
usage = f"""
Usage: {sys.argv[0]} <command> [source_code_file]

Command 'interpret':
    Runs the interpreter on source code.

Common arguments:
    source_code_file        Optional. Defaults to standard input if missing.
 """.strip() + "\n"


def main() -> int:
    command: str | None = None
    input_file: str | None = None
    for arg in sys.argv[1:]:
        if arg in ['-h', '--help']:
            print(usage)
            return 0
        elif arg.startswith('-'):
            raise Exception(f"Unknown argument: {arg}")
        elif command is None:
            command = arg
        elif input_file is None:
            input_file = arg
        else:
            raise Exception("Multiple input files not supported")

    def read_source_code() -> str:
        if input_file is not None:
            with open(input_file) as f:
                return f.read()
        else:
            return sys.stdin.read()

    if command is None:
        print(f"Error: command argument missing\n\n{usage}", file=sys.stderr)
        return 1

    if command == 'interpret':
        source_code = read_source_code()
        result = interpret(parser(tokenize(source_code)))
        print(result)
    elif command == 'ir':
        source_code = read_source_code()
        tokens = tokenize(source_code)
        ast_nodes = parser(tokens)
        typecheck(ast_nodes, SymTab(locals={}, parent=None))
        irs = generate_ir(root_types, ast_nodes)
        for func, irs in irs.items():
            print(f"function : {func}:")
            print("\n".join([str(ins) for ins in irs]))
    elif command == 'asm':
        source_code = read_source_code()
        tokens = tokenize(source_code)
        ast_nodes = parser(tokens)
        typecheck(ast_nodes, SymTab(locals={}, parent=None))
        irs = generate_ir(root_types, ast_nodes)
        asm_code = generate_assembly(irs)
        print(asm_code)
    elif command == 'compile':
        source_code = read_source_code()
        tokens = tokenize(source_code)
        ast_nodes = parser(tokens)
        typecheck(ast_nodes, SymTab(locals={}, parent=None))
        irs = generate_ir(root_types, ast_nodes)
        asm_code = generate_assembly(irs)
        assemble(asm_code, 'compile_program')
    else:
        print(f"Error: unknown command: {command}\n\n{usage}", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
