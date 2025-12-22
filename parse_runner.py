import sys
from antlr4 import *
from compiler.bones.grammarNumLangLexer import grammarNumLangLexer
from compiler.bones.grammarNumLangParser import grammarNumLangParser
from compiler.src.ast_builder import ASTBuilder
from compiler.src.wat_emitter import WATEmitter
from compiler.src.semantic_analyzer import SemanticAnalyzer
from compiler.src.errors import ErrorCollector
from compiler.src.ast_nodes import Program, Func

def main(src_path):
    # 1. Лексический и синтаксический анализ
    input_stream = FileStream(src_path, encoding='utf-8')
    lexer = grammarNumLangLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = grammarNumLangParser(tokens)
    
    # Настройка обработки ошибок
    error_collector = ErrorCollector()
    
    tree = parser.prog()
    
    # 2. Построение AST
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
    
    # 3. Семантический анализ
    analyzer = SemanticAnalyzer(error_collector)
    analyzer.analyze(prog)
    
    if error_collector.has_errors():
        print("Compilation failed with errors:")
        error_collector.print_all()
        sys.exit(1)
    
    # 4. Генерация WAT
    emitter = WATEmitter()
    wat = emitter.emit(prog)
    
    with open("module.wat", "w", encoding="utf-8") as f:
        f.write(wat)
    
    print("✅ Compilation successful!")
    print("WAT written to module.wat")
    print("You can assemble to wasm with: wat2wasm module.wat -o module.wasm")
    print("Run example (Node): node runtime.js module.wasm Main")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parser_runner.py <source_file>")
        sys.exit(1)
    main(sys.argv[1])