class CodeFormatter:
    def __init__(self, indent_size=4):
        self.indent_size = indent_size
        self.current_indent = 0
    
    def format_program(self, program: Program) -> str:
        lines = []
        for func in program.funcs:
            lines.append(self._format_function(func))
            lines.append("")
        return "\n".join(lines)
    
    def _format_function(self, func: Func) -> str:
        result = []
        
        # Сигнатура функции
        ret_type = func.ret_type if func.ret_type else "void"
        params = ", ".join(f"{t} {n}" for t, n in zip(func.param_types, func.params))
        
        if func.is_template:
            template_params = ", ".join(f"type {p}" for p in func.template_params)
            result.append(f"template <{template_params}>")
        
        result.append(f"{ret_type} function {func.name}({params}) {{")
        
        # Тело функции
        self.current_indent += self.indent_size
        for stmt in func.body:
            result.append(self._format_statement(stmt))
        self.current_indent -= self.indent_size
        
        result.append("}")
        return "\n".join(result)
    
    def _format_statement(self, stmt: Stmt) -> str:
        indent = " " * self.current_indent
        # TODO: реализовать форматирование каждого типа statement
        return indent + str(stmt)