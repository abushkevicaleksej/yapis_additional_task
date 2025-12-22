# parse_runner.py
import sys
import traceback
from antlr4 import *
from compiler.bones.grammarNumLangLexer import grammarNumLangLexer
from compiler.bones.grammarNumLangParser import grammarNumLangParser
from compiler.src.ast_builder import ASTBuilder
from compiler.src.wat_emitter import WATEmitter
from compiler.src.semantic_analyzer import SemanticAnalyzer
from compiler.src.errors import ErrorCollector

def run_stage(name, func):
    print(f"--- Stage: {name} ---")
    try:
        result = func()
        print(f"✅ {name} completed.")
        return result
    except Exception as e:
        print(f"❌ Error during {name}:")
        print(traceback.format_exc())
        sys.exit(1)

def main(src_path):
    print(f"🚀 Starting compilation of: {src_path}")
    with open(src_path, 'r', encoding='utf-8') as f:
        source_code = f.read()

    error_collector = ErrorCollector(source_code)

    # 1. Parsing
    input_stream = InputStream(source_code)
    lexer = grammarNumLangLexer(input_stream)
    tokens = CommonTokenStream(lexer)
    parser = grammarNumLangParser(tokens)
    tree = run_stage("Parsing", lambda: parser.prog())

    # 2. AST
    builder = ASTBuilder()
    prog = run_stage("AST Building", lambda: builder.visit(tree))

    # 3. Semantic
    def semantic_check():
        analyzer = SemanticAnalyzer(error_collector)
        analyzer.analyze(prog)
        if error_collector.has_errors():
            print("\n❌ Semantic errors found:")
            error_collector.print_all()
            sys.exit(1)
    
    run_stage("Semantic Analysis", semantic_check)

    # 4. WAT Generation
    emitter = WATEmitter()
    wat = run_stage("Code Generation (WAT)", lambda: emitter.emit(prog))

    with open("module.wat", "w") as f:
        f.write(wat)
    print(f"\n✨ Success! Output saved to module.wat")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parse_runner.py <file>")
    else:
        main(sys.argv[1])