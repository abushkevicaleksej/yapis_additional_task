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
        self._collect_all_strings(program)

        self.lines.append('(module')
        self.lines.append(f'{self.indent}(import "env" "out_i32" (func $out_i32 (param i32)))')
        self.lines.append(f'{self.indent}(import "env" "out_f32" (func $out_f32 (param f32)))')
        self.lines.append(f'{self.indent}(import "env" "out_str" (func $out_str (param i32 i32)))')
        # Обратите внимание: in_i32 теперь принимает параметры строки-подсказки
        self.lines.append(f'{self.indent}(import "env" "in_i32" (func $in_i32 (param i32 i32) (result i32)))')
        self.lines.append(f'{self.indent}(memory (export "memory") 1)')

        for text, offset in self.strings.items():
            safe = text.replace("\n", "\\n")
            self.lines.append(f'{self.indent}(data (i32.const {offset}) "{safe}")')

        for f in program.funcs:
            if not f.is_template: self.emit_func(f)

        self.lines.append(')')
        return '\n'.join(self.lines)

    def _get_expr_type(self, e):
        if isinstance(e, IntConst): return 'int'
        if isinstance(e, FloatConst): return 'float'
        if isinstance(e, StringConst): return 'string'
        if isinstance(e, VarRef): return self.var_types.get(e.name, 'int')
        if isinstance(e, CastExpr): return e.target_type
        if isinstance(e, BinaryOp):
            if e.op in ['==', '!=', '<', '>', '<=', '>=', '&&', '||']: return 'int'
            tl, tr = self._get_expr_type(e.left), self._get_expr_type(e.right)
            return 'float' if tl == 'float' or tr == 'float' else 'int'
        if isinstance(e, FuncCall):
            if e.name == 'out': return 'void'
            f = self.func_index.get(e.name)
            return f.ret_type if f else 'int'
        return 'int'

    def emit_func(self, func: Func):
        self.var_types = {name: t for name, t in zip(func.params, func.param_types)}
        params = " ".join([f"(param ${n} {'f32' if t=='float' else 'i32'})" for n, t in self.var_types.items()])
        res = f"(result {'f32' if func.ret_type=='float' else 'i32'})" if func.ret_type and func.ret_type != 'void' else ""
        
        self.lines.append(f'{self.indent}(func ${func.name} {params} {res}')
        
        locs = self._collect_locals(func)
        for n, t in locs.items():
            if n not in func.params:
                self.lines.append(f'{self.indent*2}(local ${n} {"f32" if t=="float" else "i32"})')
                self.var_types[n] = t

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
        elif isinstance(e, BinaryOp):
            if e.op == '=':
                self.emit_expr(e.right)
                self.lines.append(f'{indent}local.set ${e.left.name}')
                # Чтобы '=' можно было использовать как выражение (int a = b = 5)
                self.lines.append(f'{indent}local.get ${e.left.name}') 
                return

            t_l = self._get_expr_type(e.left)
            t_r = self._get_expr_type(e.right)
            is_f = (t_l == 'float' or t_r == 'float')

            # Кладём левую часть
            self.emit_expr(e.left)
            if is_f and t_l == 'int': 
                self.lines.append(f'{indent}f32.convert_i32_s')
            
            # Кладём правую часть
            self.emit_expr(e.right)
            if is_f and t_r == 'int': 
                self.lines.append(f'{indent}f32.convert_i32_s')

            # Генерируем операцию
            if is_f:
                ops = {'+':'f32.add','-':'f32.sub','*':'f32.mul','/':'f32.div',
                       '==':'f32.eq','!=':'f32.ne','>':'f32.gt','<':'f32.lt'}
                self.lines.append(f'{indent}{ops.get(e.op, "f32.add")}')
            else:
                ops = {'+':'i32.add','-':'i32.sub','*':'i32.mul','/':'i32.div_s',
                       '==':'i32.eq','!=':'i32.ne','>':'i32.gt_s','<':'i32.lt_s','<=':'i32.le_s'}
                self.lines.append(f'{indent}{ops.get(e.op, "i32.add")}')
        elif isinstance(e, FuncCall):
            if e.name == 'in':
                # Вызов in с параметрами строки-подсказки
                prompt = e.args[0]
                self.lines.append(f'{indent}i32.const {self.strings[prompt.value]}')
                self.lines.append(f'{indent}i32.const {len(prompt.value.encode("utf-8"))}')
                self.lines.append(f'{indent}call $in_i32')
            elif e.name == 'out':
                arg = e.args[0]
                self.emit_expr(arg)
                t = self._get_expr_type(arg)
                if t == 'string':
                    self.lines.append(f'{indent}i32.const {len(arg.value.encode("utf-8"))}')
                    self.lines.append(f'{indent}call $out_str')
                else:
                    self.lines.append(f"{indent}call $out_{'f32' if t=='float' else 'i32'}")
                self.lines.append(f'{indent}i32.const 0') # Возвращаем 0 для стека
            else:
                # РЕКУРСИЯ И ОБЫЧНЫЕ ВЫЗОВЫ
                for arg in e.args:
                    self.emit_expr(arg)
                self.lines.append(f'{indent}call ${e.name}')

    def _collect_locals(self, func: Func):
        locs = {'tmp_sq': 'float'}
        def walk(stmts):
            if not stmts: return
            for s in stmts:
                if isinstance(s, VarDecl): locs[s.name] = s.type or 'int'
                elif isinstance(s, IfStmt):
                    walk(s.then_body)
                    walk(s.else_body)
        walk(func.body)
        return locs

    def _collect_all_strings(self, program: Program):
        self.strings = {}
        off = 0
        def walk(node):
            nonlocal off
            if isinstance(node, StringConst):
                if node.value not in self.strings:
                    self.strings[node.value] = off
                    off += len(node.value.encode('utf-8')) + 1
            elif hasattr(node, '__dict__'):
                for v in node.__dict__.values():
                    if isinstance(v, list): [walk(i) for i in v]
                    else: walk(v)
        walk(program)