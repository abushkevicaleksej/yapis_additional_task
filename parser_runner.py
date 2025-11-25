import sys
from antlr4 import *
from bones.grammarNumLangLexer import grammarNumLangLexer
from bones.grammarNumLangParser import grammarNumLangParser
from src.ast_builder import ASTBuilder
from src.wat_emitter import WATEmitter
from src.ast_nodes import Program, Func

def main(src_path):
    input_stream = FileStream(src_path, encoding='utf-8')
    lexer = grammarNumLangLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = grammarNumLangParser(tokens)
    tree = parser.prog() 
    builder = ASTBuilder()
    root = builder.visit(tree)

    if isinstance(root, Program):
        prog = root
    elif isinstance(root, list):
        prog = Program(funcs=root)
    else:
        funcs = []
        for child in tree.children:
            try:
                node = builder.visit(child)
                if isinstance(node, Func):
                    funcs.append(node)
            except Exception:
                pass
        prog = Program(funcs=funcs)

    emitter = WATEmitter()
    wat = emitter.emit(prog)
    with open("module.wat", "w", encoding="utf-8") as f:
        f.write(wat)
    print("WAT written to module.wat")
    print("You can assemble to wasm with: wat2wasm module.wat -o module.wasm")
    print("Run example (Node): node runtime.js module.wasm Main")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parser_runner.py <source_file>")
        sys.exit(1)
    main(sys.argv[1])
    # main("tests/test1.expr")
