import copy
from compiler.src.ast_nodes import *
from typing import List, Dict

class WATEmitter:
    def __init__(self):
        self.lines = []
        self.indent = "  "
        self.func_index = {}
        self.var_types = {}
        self.strings = {}

    def emit(self, program: Program) -> str:
        self.lines = []
        self.func_index = {f.name: f for f in program.funcs}
        
        # 1. Собираем все строки для секции данных
        self._collect_all_strings(program)

        self.lines.append('(module')
        
        # Импорты стандартных функций
        self.lines.append(f'{self.indent}(import "env" "out_i32" (func $out_i32 (param i32)))')
        self.lines.append(f'{self.indent}(import "env" "out_f32" (func $out_f32 (param f32)))')
        self.lines.append(f'{self.indent}(import "env" "out_str" (func $out_str (param i32 i32)))')
        self.lines.append(f'{self.indent}(import "env" "in_i32" (func $in_i32 (result i32)))')
        
        # Экспорт памяти для работы со строками
        self.lines.append(f'{self.indent}(memory (export "memory") 1)')

        # Секция данных (текстовые сообщения)
        for string_text, offset in self.strings.items():
            safe_text = string_text.replace("\n", "\\n")
            self.lines.append(f'{self.indent}(data (i32.const {offset}) "{safe_text}")')

        # Генерация кода функций
        for f in program.funcs:
            if not f.is_template:
                self.emit_func(f)

        self.lines.append(')')
        return '\n'.join(self.lines)

    def _collect_all_strings(self, program: Program):
        """Рекурсивно собирает все текстовые константы из всей программы"""
        self.strings = {}
        offset = 0

        def walk_expr(e):
            nonlocal offset
            if e is None: return
            
            if isinstance(e, StringConst):
                if e.value not in self.strings:
                    self.strings[e.value] = offset
                    # Кодируем в utf-8 для корректного подсчета байтов
                    offset += len(e.value.encode('utf-8')) + 1
            elif isinstance(e, BinaryOp):
                walk_expr(e.left)
                walk_expr(e.right)
            elif isinstance(e, UnaryOp):
                walk_expr(e.expr)
            elif isinstance(e, FuncCall):
                for arg in e.args: walk_expr(arg)
            elif isinstance(e, CastExpr):
                walk_expr(e.expr)

        def walk_stmt(s):
            if s is None: return
            
            if isinstance(s, VarDecl):
                if s.init: walk_expr(s.init)
            elif isinstance(s, ExprStmt):
                walk_expr(s.expr)
            elif isinstance(s, Return):
                if s.expr: walk_expr(s.expr)
            elif isinstance(s, IfStmt):
                walk_expr(s.cond)
                for ts in s.then_body: walk_stmt(ts)
                if s.else_body:
                    for es in s.else_body: walk_stmt(es)
            elif isinstance(s, WhileStmt):
                walk_expr(s.cond)
                for bs in s.body: walk_stmt(bs)
            elif isinstance(s, ForStmt):
                if s.init: walk_stmt(s.init)
                if s.cond: walk_expr(s.cond)
                if s.step: walk_expr(s.step)
                for bs in s.body: walk_stmt(bs)

        for f in program.funcs:
            for s in f.body:
                walk_stmt(s)

    def _get_expr_type(self, e):
        if isinstance(e, IntConst): return 'int'
        if isinstance(e, FloatConst): return 'float'
        if isinstance(e, StringConst): return 'string'
        if isinstance(e, VarRef): return self.var_types.get(e.name, 'int')
        if isinstance(e, UnaryOp): return self._get_expr_type(e.expr)
        if isinstance(e, CastExpr): return e.target_type
        if isinstance(e, BinaryOp):
            if e.op in ['==', '!=', '<', '>', '<=', '>=']: return 'int'
            if e.op == '^': return 'float'
            tl, tr = self._get_expr_type(e.left), self._get_expr_type(e.right)
            return 'float' if tl == 'float' or tr == 'float' else 'int'
        if isinstance(e, FuncCall):
            if e.name == 'out': return 'void'
            f = self.func_index.get(e.name)
            return f.ret_type if f else 'int'
        return 'int'

    def _collect_locals(self, func: Func) -> Dict[str, str]:
        locs = {'tmp_sq': 'float'} # ОБЯЗАТЕЛЬНО добавляем tmp_sq сюда
        def walk(stmts):
            for s in stmts:
                if isinstance(s, VarDecl): locs[s.name] = s.type or 'int'
                elif isinstance(s, IfStmt):
                    walk(s.then_body)
                    if s.else_body: walk(s.else_body)
        walk(func.body)
        return locs

    def emit_func(self, func: Func):
        self.var_types = {name: t for name, t in zip(func.params, func.param_types)}
        params = " ".join([f"(param ${n} {'f32' if t=='float' else 'i32'})" for n, t in self.var_types.items()])
        result = f"(result {'f32' if func.ret_type=='float' else 'i32'})" if func.ret_type and func.ret_type != 'void' else ""
        
        self.lines.append(f'{self.indent}(func ${func.name} {params} {result}')
        
        # Декларация локальных переменных (включая служебную tmp_sq)
        all_locals = self._collect_locals(func)
        for name, ptype in all_locals.items():
            if name not in func.params:
                wtype = 'f32' if ptype == 'float' else 'i32'
                self.lines.append(f'{self.indent*2}(local ${name} {wtype})')
                self.var_types[name] = ptype

        for s in func.body: self.emit_stmt(s)
        
        if func.ret_type and func.ret_type != 'void':
            self.lines.append(f"{self.indent*2}{'f32.const 0.0' if func.ret_type=='float' else 'i32.const 0'}")
        self.lines.append(f'{self.indent})')
        self.lines.append(f'{self.indent}(export "{func.name}" (func ${func.name}))')

    def emit_stmt(self, s):
        indent = self.indent * 2
        if isinstance(s, VarDecl):
            if s.init:
                self.emit_expr(s.init)
                if s.type == 'float' and self._get_expr_type(s.init) == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
                self.lines.append(f'{indent}local.set ${s.name}')
        elif isinstance(s, ExprStmt):
            self.emit_expr(s.expr)
            if self._get_expr_type(s.expr) != 'void': self.lines.append(f'{indent}drop')
        elif isinstance(s, Return):
            if s.expr: self.emit_expr(s.expr)
            self.lines.append(f'{indent}return')
        elif isinstance(s, IfStmt):
            self.emit_expr(s.cond)
            if self._get_expr_type(s.cond) == 'float':
                self.lines.append(f'{indent}f32.const 0.0')
                self.lines.append(f'{indent}f32.ne')
            self.lines.append(f'{indent}if')
            for ts in s.then_body: self.emit_stmt(ts)
            if s.else_body:
                self.lines.append(f'{indent}else')
                for es in s.else_body: self.emit_stmt(es)
            self.lines.append(f'{indent}end')

    def emit_expr(self, e):
        indent = self.indent * 2
        if isinstance(e, IntConst): self.lines.append(f'{indent}i32.const {e.value}')
        elif isinstance(e, FloatConst): self.lines.append(f'{indent}f32.const {e.value}')
        elif isinstance(e, VarRef): self.lines.append(f'{indent}local.get ${e.name}')
        elif isinstance(e, StringConst): self.lines.append(f'{indent}i32.const {self.strings[e.value]}')
        elif isinstance(e, CastExpr):
            self.emit_expr(e.expr)
            if e.target_type == 'float' and self._get_expr_type(e.expr) == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
        elif isinstance(e, UnaryOp):
            self.emit_expr(e.expr)
            if e.op == '-':
                if self._get_expr_type(e.expr) == 'float': self.lines.append(f'{indent}f32.neg')
                else: self.lines.append(f'{indent}i32.const -1'), self.lines.append(f'{indent}i32.mul')
        elif isinstance(e, BinaryOp):
            if e.op == '=':
                self.emit_expr(e.right)
                if self.var_types[e.left.name] == 'float' and self._get_expr_type(e.right) == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
                self.lines.append(f'{indent}local.tee ${e.left.name}')
                return
            if e.op == '^':
                self.emit_expr(e.left)
                if self._get_expr_type(e.left) == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
                if isinstance(e.right, (IntConst, FloatConst)) and float(e.right.value) == 2.0:
                    self.lines.append(f'{indent}local.tee $tmp_sq')
                    self.lines.append(f'{indent}local.get $tmp_sq')
                    self.lines.append(f'{indent}f32.mul')
                else: self.lines.append(f'{indent}f32.sqrt')
                return
            t_l, t_r = self._get_expr_type(e.left), self._get_expr_type(e.right)
            is_f = (t_l == 'float' or t_r == 'float')
            self.emit_expr(e.left)
            if is_f and t_l == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
            self.emit_expr(e.right)
            if is_f and t_r == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
            if is_f:
                op = {'+':'f32.add','-':'f32.sub','*':'f32.mul','/':'f32.div','==':'f32.eq','!=':'f32.ne','>':'f32.gt','<':'f32.lt'}
                self.lines.append(f'{indent}{op.get(e.op, "f32.add")}')
            else:
                op = {'+':'i32.add','-':'i32.sub','*':'i32.mul','/':'i32.div_s','==':'i32.eq','!=':'i32.ne','>':'i32.gt_s','<':'i32.lt_s'}
                self.lines.append(f'{indent}{op.get(e.op, "i32.add")}')
        elif isinstance(e, FuncCall):
            if e.name == 'out':
                t = self._get_expr_type(e.args[0])
                self.emit_expr(e.args[0])
                if t == 'string':
                    self.lines.append(f'{indent}i32.const {len(e.args[0].value.encode("utf-8"))}')
                    self.lines.append(f'{indent}call $out_str')
                else: self.lines.append(f"{indent}call $out_{'f32' if t=='float' else 'i32'}")
            elif e.name == 'in': self.lines.append(f'{indent}call $in_i32')
            else:
                f = self.func_index.get(e.name)
                for i, arg in enumerate(e.args):
                    self.emit_expr(arg)
                    if f and i < len(f.param_types) and f.param_types[i] == 'float' and self._get_expr_type(arg) == 'int':
                        self.lines.append(f'{indent}f32.convert_i32_s')
                self.lines.append(f'{indent}call ${e.name}')