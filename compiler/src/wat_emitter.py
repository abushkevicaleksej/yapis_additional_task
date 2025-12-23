import copy
from compiler.src.ast_nodes import *
from typing import List, Dict, Set, Tuple

class WATEmitter:
    def __init__(self):
        self.lines = []
        self.indent = "  "
        self.func_index = {}
        self.var_types = {}
        self.strings = {}
        self.specializations: Dict[str, Set[Tuple[str, ...]]] = {}
        self.type_mapping: Dict[str, str] = {}

    def emit(self, program: Program) -> str:
        self.lines = []
        self.func_index = {f.name: f for f in program.funcs}
        self._collect_all_strings(program)
        
        self.specializations = {}
        self._find_specializations(program)

        self.lines.append('(module')
        self.lines.append(f'{self.indent}(import "env" "out_i32" (func $out_i32 (param i32)))')
        self.lines.append(f'{self.indent}(import "env" "out_f32" (func $out_f32 (param f32)))')
        self.lines.append(f'{self.indent}(import "env" "out_str" (func $out_str (param i32)))')
        self.lines.append(f'{self.indent}(import "env" "in_i32" (func $in_i32 (param i32) (result i32)))')
        self.lines.append(f'{self.indent}(import "env" "pow_f32" (func $pow_f32 (param f32 f32) (result f32)))')
        self.lines.append(f'{self.indent}(memory (export "memory") 1)')

        for text, offset in self.strings.items():
            self.lines.append(f'{self.indent}(data (i32.const {offset}) "{text.replace("\\n", "\\\\n")}\\00")')

        for f in program.funcs:
            if not f.is_template:
                self.type_mapping = {}
                self.emit_func(f)
            else:
                specs = self.specializations.get(f.name, [])
                for spec_args in specs:
                    self.type_mapping = { name: val for name, val in zip(f.template_params, spec_args) }
                    spec_name = f"{f.name}_" + "_".join(spec_args)
                    self.emit_func(f, override_name=spec_name)

        self.lines.append(')')
        return '\n'.join(self.lines)

    def _find_specializations(self, node):
        if isinstance(node, FuncCall) and node.template_args:
            if node.name not in self.specializations:
                self.specializations[node.name] = set()
            self.specializations[node.name].add(tuple(node.template_args))
        
        if hasattr(node, '__dict__'):
            for v in node.__dict__.values():
                if isinstance(v, list):
                    for i in v: self._find_specializations(i)
                elif isinstance(v, ASTNode):
                    self._find_specializations(v)

    def _map_type(self, t: str) -> str:
        return self.type_mapping.get(t, t)

    def _get_expr_type(self, e):
        if isinstance(e, IntConst): return 'int'
        if isinstance(e, FloatConst): return 'float'
        if isinstance(e, StringConst): return 'string'
        if isinstance(e, VarRef):
            return self._map_type(self.var_types.get(e.name, 'int'))
        if isinstance(e, CastExpr): return self._map_type(e.target_type)
        if isinstance(e, (IntegralExpr, DerivativeExpr, ArrayAccess)): return 'float'
        if isinstance(e, SolveLUExpr): return 'int'
        
        if isinstance(e, BinaryOp):
            if e.op in ['==', '!=', '<', '>', '<=', '>=']: return 'int'
            if e.op == '^': return 'float'
            tl, tr = self._get_expr_type(e.left), self._get_expr_type(e.right)
            if tl == 'float' or tr == 'float': return 'float'
            return 'int'
            
        if isinstance(e, FuncCall):
            if e.name in ['out', 'in']: return 'int'
            f = self.func_index.get(e.name)
            if not f: return 'int'
            ret = f.ret_type
            if f.is_template and ret in f.template_params:
                if self.type_mapping and ret in self.type_mapping:
                    return self.type_mapping[ret]
                if e.template_args:
                    idx = f.template_params.index(ret)
                    return e.template_args[idx]
            return self._map_type(ret)
        return 'int'

    def _collect_locals(self, func: Func):
        locs = {
            'tmp_sq': 'float', 
            'int_i': 'int', 
            'int_h': 'float', 
            'int_sum': 'float'
        }
        
        def walk(node):
            if node is None: return
            
            if isinstance(node, VarDecl):
                locs[node.name] = self._map_type(node.type or 'int')
            
            if isinstance(node, IntegralExpr):
                locs[node.var] = 'float'
            
            if isinstance(node, DerivativeExpr):
                locs[node.var] = 'float'
                
            if hasattr(node, '__dict__'):
                for v in node.__dict__.values():
                    if isinstance(v, list):
                        for i in v:
                            if isinstance(i, (ASTNode, list)): walk(i)
                    elif isinstance(v, ASTNode):
                        walk(v)

        if func.body:
            for stmt in func.body:
                walk(stmt)
                
        return locs

    def emit_func(self, func: Func, override_name=None):
        name = override_name or func.name
        self.var_types = {n: self._map_type(t) for n, t in zip(func.params, func.param_types)}
        params = " ".join([f"(param ${n} {'f32' if t=='float' else 'i32'})" for n, t in self.var_types.items()])
        ret_t = self._map_type(func.ret_type)
        res = f"(result {'f32' if ret_t=='float' else 'i32'})" if ret_t and ret_t != 'void' else ""
        
        self.lines.append(f'{self.indent}(func ${name} {params} {res}')
        locs = self._collect_locals(func)
        for n, t in locs.items():
            if n not in func.params:
                self.lines.append(f'{self.indent*2}(local ${n} {"f32" if t=="float" else "i32"})')
                self.var_types[n] = t

        for s in func.body: self.emit_stmt(s)
        if ret_t and ret_t != 'void': self.lines.append(f"{self.indent*2}{'f32.const 0.0' if ret_t=='float' else 'i32.const 0'}")
        self.lines.append(f'{self.indent})')
        self.lines.append(f'{self.indent}(export "{name}" (func ${name}))')

    def emit_stmt(self, s):
        indent = self.indent * 2
        if isinstance(s, VarDecl):
            if s.init:
                self.emit_expr(s.init)
                actual_t, target_t = self._get_expr_type(s.init), self.var_types.get(s.name, 'int')
                if target_t == 'float' and actual_t == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
                elif target_t == 'int' and actual_t == 'float': self.lines.append(f'{indent}i32.trunc_f32_s')
                self.lines.append(f'{indent}local.set ${s.name}')
        elif isinstance(s, ExprStmt):
            t = self._get_expr_type(s.expr)
            self.emit_expr(s.expr)
            if t != 'void': self.lines.append(f'{indent}drop')
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
        elif isinstance(s, WhileStmt):
            self.lines.append(f'{indent}block\n{indent}  loop')
            self.emit_expr(s.cond)
            self.lines.append(f'{indent}    i32.eqz\n{indent}    br_if 1')
            for bs in s.body: self.emit_stmt(bs)
            self.lines.append(f'{indent}    br 0\n{indent}  end\n{indent}end')
        elif isinstance(s, ForStmt):
            if s.init: self.emit_stmt(s.init)
            self.lines.append(f'{indent}block\n{indent}  loop')
            if s.cond:
                self.emit_expr(s.cond)
                self.lines.append(f'{indent}    i32.eqz\n{indent}    br_if 1')
            for bs in s.body: self.emit_stmt(bs)
            if s.step: self.emit_expr(s.step); self.lines.append(f'{indent}drop')
            self.lines.append(f'{indent}    br 0\n{indent}  end\n{indent}end')

    def emit_expr(self, e):
        indent = self.indent * 2
        if isinstance(e, IntConst): self.lines.append(f'{indent}i32.const {e.value}')
        elif isinstance(e, FloatConst): self.lines.append(f'{indent}f32.const {e.value}')
        elif isinstance(e, VarRef): self.lines.append(f'{indent}local.get ${e.name}')
        elif isinstance(e, StringConst): self.lines.append(f'{indent}i32.const {self.strings[e.value]}')
        elif isinstance(e, CastExpr):
            self.emit_expr(e.expr)
            src, dst = self._get_expr_type(e.expr), self._map_type(e.target_type)
            if dst == 'float' and src == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
            elif dst == 'int' and src == 'float': self.lines.append(f'{indent}i32.trunc_f32_s')
        elif isinstance(e, BinaryOp):
            if e.op == '=':
                self.emit_expr(e.right)
                target_t, actual_t = self.var_types.get(e.left.name, 'int'), self._get_expr_type(e.right)
                if target_t == 'float' and actual_t == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
                elif target_t == 'int' and actual_t == 'float': self.lines.append(f'{indent}i32.trunc_f32_s')
                self.lines.append(f'{indent}local.tee ${e.left.name}')
            elif e.op == '^':
                self.emit_expr(e.left)
                if self._get_expr_type(e.left) == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
                self.emit_expr(e.right)
                if self._get_expr_type(e.right) == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
                self.lines.append(f'{indent}call $pow_f32')
            else:
                tl, tr = self._get_expr_type(e.left), self._get_expr_type(e.right)
                is_f = (tl == 'float' or tr == 'float')
                self.emit_expr(e.left)
                if is_f and tl == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
                self.emit_expr(e.right)
                if is_f and tr == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
                if is_f:
                    op = {'+':'f32.add','-':'f32.sub','*':'f32.mul','/':'f32.div','==':'f32.eq','!=':'f32.ne','>':'f32.gt','<':'f32.lt','<=':'f32.le','>=':'f32.ge'}
                    self.lines.append(f'{indent}{op.get(e.op, "f32.add")}')
                else:
                    op = {'+':'i32.add','-':'i32.sub','*':'i32.mul','/':'i32.div_s','==':'i32.eq','!=':'i32.ne','>':'i32.gt_s','<':'i32.lt_s','<=':'i32.le_s','>=':'i32.ge_s'}
                    self.lines.append(f'{indent}{op.get(e.op, "i32.add")}')
        elif isinstance(e, FuncCall):
            if e.name == 'out':
                arg = e.args[0]; t = self._get_expr_type(arg)
                self.emit_expr(arg)
                call_target = {"string": "$out_str", "float": "$out_f32"}.get(t, "$out_i32")
                self.lines.append(f'{indent}call {call_target}\n{indent}i32.const 0')
            elif e.name == 'in':
                prompt = e.args[0]
                self.lines.append(f'{indent}i32.const {self.strings[prompt.value]}\n{indent}call $in_i32')
            else:
                f = self.func_index.get(e.name)
                call_name = e.name
                if f and f.is_template and e.template_args:
                    call_name = f"{e.name}_" + "_".join(e.template_args)
                for i, arg in enumerate(e.args):
                    self.emit_expr(arg)
                    if f:
                        formal_t = self._map_type(f.param_types[i]) if f.is_template else f.param_types[i]
                        actual_t = self._get_expr_type(arg)
                        if formal_t == 'float' and actual_t == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
                        elif formal_t == 'int' and actual_t == 'float': self.lines.append(f'{indent}i32.trunc_f32_s')
                self.lines.append(f'{indent}call ${call_name}')
        elif isinstance(e, IntegralExpr):
            self.emit_expr(e.start)
            if self._get_expr_type(e.start) == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
            self.emit_expr(e.end)
            if self._get_expr_type(e.end) == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
            self.lines.append(f'{indent}f32.sub')
            self.lines.append(f'{indent}f32.const 1000.0')
            self.lines.append(f'{indent}f32.div')
            self.lines.append(f'{indent}local.set $int_h')
            
            self.lines.append(f'{indent}f32.const 0.0')
            self.lines.append(f'{indent}local.set $int_sum')
            self.lines.append(f'{indent}i32.const 0')
            self.lines.append(f'{indent}local.set $int_i')
            
            self.lines.append(f'{indent}block\n{indent}  loop')
            self.lines.append(f'{indent}    local.get $int_i\n{indent}    i32.const 1000\n{indent}    i32.ge_s\n{indent}    br_if 1')
            
            self.emit_expr(e.start)
            if self._get_expr_type(e.start) == 'int': self.lines.append(f'{indent}f32.convert_i32_s')
            self.lines.append(f'{indent}local.get $int_i\n{indent}f32.convert_i32_s\n{indent}f32.const 0.5\n{indent}f32.add')
            self.lines.append(f'{indent}local.get $int_h\n{indent}f32.mul\n{indent}f32.add')
            self.lines.append(f'{indent}local.set ${e.var}')
            
            self.lines.append(f'{indent}local.get $int_sum')
            self.emit_expr(e.body)
            if self._get_expr_type(e.body) == 'int':
                self.lines.append(f'{indent}f32.convert_i32_s')
            
            self.lines.append(f'{indent}local.get $int_h')
            self.lines.append(f'{indent}f32.mul')
            self.lines.append(f'{indent}f32.add')
            self.lines.append(f'{indent}local.set $int_sum')
            
            self.lines.append(f'{indent}local.get $int_i\n{indent}i32.const 1\n{indent}i32.add\n{indent}local.set $int_i')
            self.lines.append(f'{indent}br 0\n{indent}  end\n{indent}end')
            self.lines.append(f'{indent}local.get $int_sum')
        elif isinstance(e, DerivativeExpr):
            dx = 0.0001; self.lines.append(f'{indent}local.get ${e.var}\n{indent}local.set $tmp_sq\n{indent}local.get $tmp_sq\n{indent}f32.const {dx}\n{indent}f32.add\n{indent}local.set ${e.var}')
            self.emit_expr(e.body)
            self.lines.append(f'{indent}local.get $tmp_sq\n{indent}f32.const {dx}\n{indent}f32.sub\n{indent}local.set ${e.var}')
            self.emit_expr(e.body)
            self.lines.append(f'{indent}f32.sub\n{indent}f32.const {2*dx}\n{indent}f32.div\n{indent}local.get $tmp_sq\n{indent}local.set ${e.var}')
        elif isinstance(e, SolveLUExpr):
            self.emit_expr(e.matrix); self.lines.append(f'{indent}drop')
            self.emit_expr(e.vector); self.lines.append(f'{indent}drop\n{indent}i32.const 0')
        elif isinstance(e, ArrayAccess):
            self.lines.append(f'{indent}local.get ${e.name}')
            self.emit_expr(e.expr); self.lines.append(f'{indent}i32.const 4\n{indent}i32.mul\n{indent}i32.add\n{indent}f32.load')

    def _collect_all_strings(self, program):
        self.strings = {}; off = 0
        def walk(n):
            nonlocal off
            if isinstance(n, StringConst) and n.value not in self.strings:
                self.strings[n.value] = off
                off += len(n.value.encode('utf-8')) + 1
            if hasattr(n, '__dict__'):
                for v in n.__dict__.values():
                    if isinstance(v, list): [walk(i) for i in v if isinstance(i, ASTNode)]
                    elif isinstance(v, ASTNode): walk(v)
        walk(program)