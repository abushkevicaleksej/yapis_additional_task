import copy
from compiler.src.ast_nodes import *
from typing import List, Dict

class WATEmitter:
    def __init__(self):
        self.lines = []
        self.indent = "  "
        self.funcs_emitted = set()
        self.extra_imports = [
            '(import "env" "out_i32" (func $out_i32 (param i32)))',
            '(import "env" "out_f32" (func $out_f32 (param f32)))',
            '(import "env" "in_i32" (func $in_i32 (result i32)))'
        ]
        self.func_index = {}
        self.loop_stack = []
        self.var_types = {}

    def emit(self, program: Program) -> str:
        self.func_index = {}
        self.funcs_emitted = set()
        self.lines = []
        
        # Индексируем исходные функции
        for f in program.funcs:
            self.func_index[f.name] = f

        self.lines.append('(module')
        for imp in self.extra_imports:
            self.lines.append(f'{self.indent}{imp}')

        # Генерируем новые функции из шаблонов
        self._instantiate_templates_from_calls(program)
        
        # Обновляем индекс с учетом сгенерированных
        for f in program.funcs:
            self.func_index[f.name] = f

        # Эмитим ВСЕ функции (включая сгенерированные), кроме шаблонов
        for f in program.funcs:
            if not f.is_template:
                self.emit_func(f)

        self.lines.append(')')
        return '\n'.join(self.lines)

    def _instantiate_templates_from_calls(self, program: Program):
        new_funcs = []
        processed_signatures = set()

        calls_to_process = []
        for f in program.funcs:
            if not f.is_template:
                calls_to_process.extend(self._collect_calls(f.body))
        
        i = 0
        while i < len(calls_to_process):
            call = calls_to_process[i]
            i += 1
            
            if call.template_args:
                base_name = call.name
                mangled_name = self._mangle(base_name, call.template_args)
                
                if mangled_name in self.func_index: continue
                if mangled_name in processed_signatures: continue

                base_func = self.func_index.get(base_name)
                if base_func and base_func.is_template:
                    new_func = copy.deepcopy(base_func)
                    new_func.name = mangled_name
                    new_func.is_template = False
                    new_func.template_params = None
                    
                    type_map = {}
                    if base_func.template_params and len(base_func.template_params) == len(call.template_args):
                        for j, t_param in enumerate(base_func.template_params):
                            type_map[t_param] = call.template_args[j]
                    
                    self._replace_types_in_func(new_func, type_map)
                    
                    new_funcs.append(new_func)
                    processed_signatures.add(mangled_name)
                    self.func_index[mangled_name] = new_func 
                    
                    calls_to_process.extend(self._collect_calls(new_func.body))

        program.funcs.extend(new_funcs)

    def _replace_types_in_func(self, func: Func, type_map: Dict[str, str]):
        if func.ret_type in type_map:
            func.ret_type = type_map[func.ret_type]
        
        if func.param_types:
            new_pt = []
            for pt in func.param_types:
                new_pt.append(type_map.get(pt, pt))
            func.param_types = new_pt
            
        self._replace_types_in_stmts(func.body, type_map)

    def _replace_types_in_stmts(self, stmts: List[Stmt], type_map: Dict[str, str]):
        if not stmts: return
        for s in stmts:
            if isinstance(s, VarDecl):
                if s.type in type_map: s.type = type_map[s.type]
                if s.init: self._replace_types_in_expr(s.init, type_map)
            elif isinstance(s, Return):
                if s.expr: self._replace_types_in_expr(s.expr, type_map)
            elif isinstance(s, ExprStmt):
                self._replace_types_in_expr(s.expr, type_map)
            elif isinstance(s, IfStmt):
                self._replace_types_in_expr(s.cond, type_map)
                self._replace_types_in_stmts(s.then_body, type_map)
                if s.else_body: self._replace_types_in_stmts(s.else_body, type_map)
            elif isinstance(s, WhileStmt):
                self._replace_types_in_expr(s.cond, type_map)
                self._replace_types_in_stmts(s.body, type_map)
            elif isinstance(s, ForStmt):
                if isinstance(s.init, Stmt): self._replace_types_in_stmts([s.init], type_map)
                if s.cond: self._replace_types_in_expr(s.cond, type_map)
                if s.step: self._replace_types_in_expr(s.step, type_map)
                self._replace_types_in_stmts(s.body, type_map)

    def _replace_types_in_expr(self, e: Expr, type_map: Dict[str, str]):
        if isinstance(e, CastExpr):
            if e.target_type in type_map: e.target_type = type_map[e.target_type]
            self._replace_types_in_expr(e.expr, type_map)
        elif isinstance(e, BinaryOp):
            self._replace_types_in_expr(e.left, type_map)
            self._replace_types_in_expr(e.right, type_map)
        elif isinstance(e, UnaryOp):
            self._replace_types_in_expr(e.expr, type_map)
        elif isinstance(e, FuncCall):
            for a in e.args: self._replace_types_in_expr(a, type_map)
            if e.template_args:
                new_ta = [type_map.get(ta, ta) for ta in e.template_args]
                e.template_args = new_ta

    def _collect_calls(self, stmts):
        res = []
        if not stmts: return res
        for s in stmts:
            if isinstance(s, ExprStmt): res.extend(self._collect_calls_in_expr(s.expr))
            elif isinstance(s, VarDecl) and s.init: res.extend(self._collect_calls_in_expr(s.init))
            elif isinstance(s, Return) and s.expr: res.extend(self._collect_calls_in_expr(s.expr))
            elif isinstance(s, IfStmt):
                if s.cond: res.extend(self._collect_calls_in_expr(s.cond))
                res.extend(self._collect_calls(s.then_body))
                if s.else_body: res.extend(self._collect_calls(s.else_body))
            elif isinstance(s, WhileStmt):
                res.extend(self._collect_calls_in_expr(s.cond))
                res.extend(self._collect_calls(s.body))
            elif isinstance(s, ForStmt):
                if s.init and isinstance(s.init, VarDecl) and s.init.init:
                    res.extend(self._collect_calls_in_expr(s.init.init))
                if s.cond: res.extend(self._collect_calls_in_expr(s.cond))
                if s.step: res.extend(self._collect_calls_in_expr(s.step))
                res.extend(self._collect_calls(s.body))
        return res

    def _collect_calls_in_expr(self, e):
        res = []
        if isinstance(e, FuncCall):
            res.append(e)
            for a in e.args: res.extend(self._collect_calls_in_expr(a))
        elif isinstance(e, BinaryOp):
            res.extend(self._collect_calls_in_expr(e.left))
            res.extend(self._collect_calls_in_expr(e.right))
        elif isinstance(e, UnaryOp):
            res.extend(self._collect_calls_in_expr(e.expr))
        elif isinstance(e, CastExpr):
            res.extend(self._collect_calls_in_expr(e.expr))
        return res

    def _mangle(self, name, templ_args):
        safe = [t.replace(' ', '').replace('<','').replace('>','') for t in templ_args]
        return name + "__" + "_".join(safe)

    def _map_type(self, t):
        if t == 'float': return 'f32'
        return 'i32'

    def _get_expr_type(self, e):
        if isinstance(e, IntConst): return 'int'
        if isinstance(e, FloatConst): return 'float'
        if isinstance(e, StringConst): return 'int'
        if isinstance(e, CharConst): return 'char'
        
        if isinstance(e, VarRef):
            return self.var_types.get(e.name, 'int')
        if isinstance(e, CastExpr):
            return e.target_type
        if isinstance(e, BinaryOp):
            if e.op == '=': return self._get_expr_type(e.left)
            if e.op in ['==', '!=', '<', '<=', '>', '>=', '&&', '||']: return 'int'
            t_left = self._get_expr_type(e.left)
            t_right = self._get_expr_type(e.right)
            if t_left == 'float' or t_right == 'float': return 'float'
            return 'int'
        if isinstance(e, FuncCall):
            if e.name == 'in': return 'int'
        
            if e.name == 'out': return 'int' 
            
            f = self.func_index.get(e.name)
            if f:
                return f.ret_type # может вернуть 'void'
            return 'int'
        if isinstance(e, UnaryOp):
            return self._get_expr_type(e.expr)
        return 'int'

    def emit_func(self, func: Func):
        if func.name in self.funcs_emitted: return
        self.funcs_emitted.add(func.name)
        self.var_types = {}

        wasm_params_parts = []
        for i, pname in enumerate(func.params):
            ptype = 'int'
            if func.param_types and i < len(func.param_types):
                ptype = func.param_types[i]
            self.var_types[pname] = ptype
            wtype = self._map_type(ptype)
            wasm_params_parts.append(f'(param ${pname} {wtype})')
        
        wasm_params = ' '.join(wasm_params_parts)
        wasm_ret = ''
        if func.ret_type and func.ret_type != 'void':
            wasm_ret = f'(result {self._map_type(func.ret_type)})'
            
        self.lines.append(f'{self.indent}(func ${func.name} {wasm_params} {wasm_ret}')
        
        locals_ = self._collect_locals_with_types(func)
        for name, type_ in locals_.items():
            self.var_types[name] = type_
            if name not in func.params:
                self.lines.append(f'{self.indent*2}(local ${name} {self._map_type(type_)})')
        
        for s in func.body:
            self.emit_stmt(s)
            
        if func.ret_type and func.ret_type != 'void':
            wtype = self._map_type(func.ret_type)
            zero = '0.0' if wtype == 'f32' else '0'
            const_instr = 'f32.const' if wtype == 'f32' else 'i32.const'
            self.lines.append(f'{self.indent*2}{const_instr} {zero}')

        self.lines.append(f'{self.indent})')
        self.lines.append(f'{self.indent}(export "{func.name}" (func ${func.name}))')

    def _collect_locals_with_types(self, func):
        locs = {}
        def walk(stmts):
            if not stmts: return
            for s in stmts:
                if isinstance(s, VarDecl):
                    locs[s.name] = s.type if s.type else 'int'
                elif isinstance(s, IfStmt):
                    walk(s.then_body)
                    if s.else_body: walk(s.else_body)
                elif isinstance(s, WhileStmt):
                    walk(s.body)
                elif isinstance(s, ForStmt):
                    if s.init and isinstance(s.init, VarDecl):
                         locs[s.init.name] = s.init.type
                    walk(s.body)
        walk(func.body)
        return locs

    def emit_stmt(self, s):
        indent = self.indent * 2
        
        if isinstance(s, VarDecl):
            if s.init:
                target_type = s.type if s.type else 'int'
                expr_type = self._get_expr_type(s.init)
                self.emit_expr(s.init)
                
                if target_type == 'float' and (expr_type == 'int' or expr_type == 'char'):
                    self.lines.append(f'{indent}f32.convert_i32_s')
                elif (target_type == 'int' or target_type == 'char') and expr_type == 'float':
                    self.lines.append(f'{indent}i32.trunc_f32_s')
                    
                self.lines.append(f'{indent}local.set ${s.name}')
        
        elif isinstance(s, ExprStmt):
            self.emit_expr(s.expr)
            # FIX: Делаем drop только если выражение что-то вернуло (не void)
            if self._get_expr_type(s.expr) != 'void':
                self.lines.append(f'{indent}drop')
        
        elif isinstance(s, Return):
            if s.expr:
                self.emit_expr(s.expr)
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
        
        elif isinstance(s, WhileStmt):
            lb, lc = f"break_{len(self.lines)}", f"cont_{len(self.lines)}"
            self.lines.append(f'{indent}block ${lb}')
            self.lines.append(f'{indent}loop ${lc}')
            self.emit_expr(s.cond)
            self.lines.append(f'{indent}i32.eqz')
            self.lines.append(f'{indent}br_if ${lb}')
            self.loop_stack.append((lb, lc))
            for bs in s.body: self.emit_stmt(bs)
            self.loop_stack.pop()
            self.lines.append(f'{indent}br ${lc}')
            self.lines.append(f'{indent}end')
            self.lines.append(f'{indent}end')
        
        elif isinstance(s, ForStmt):
            if s.init: self.emit_stmt(s.init)
            lb, lc = f"break_{len(self.lines)}", f"cont_{len(self.lines)}"
            self.lines.append(f'{indent}block ${lb}')
            self.lines.append(f'{indent}loop ${lc}')
            if s.cond:
                self.emit_expr(s.cond)
                self.lines.append(f'{indent}i32.eqz')
                self.lines.append(f'{indent}br_if ${lb}')
            self.loop_stack.append((lb, lc))
            for bs in s.body: self.emit_stmt(bs)
            self.loop_stack.pop()
            if s.step:
                self.emit_expr(s.step)
                self.lines.append(f'{indent}drop')
            self.lines.append(f'{indent}br ${lc}')
            self.lines.append(f'{indent}end')
            self.lines.append(f'{indent}end')

    def emit_expr(self, e):
        indent = self.indent * 2
        
        if isinstance(e, IntConst):
            self.lines.append(f'{indent}i32.const {e.value}')
        elif isinstance(e, FloatConst):
            self.lines.append(f'{indent}f32.const {e.value}')
        elif isinstance(e, StringConst):
            self.lines.append(f'{indent}i32.const 0')
        elif isinstance(e, CharConst):
            self.lines.append(f'{indent}i32.const {ord(e.value)}')
        elif isinstance(e, VarRef):
            self.lines.append(f'{indent}local.get ${e.name}')

        elif isinstance(e, CastExpr):
            self.emit_expr(e.expr)
            src = self._get_expr_type(e.expr)
            dst = e.target_type
            
            if src == dst: pass
            elif (src == 'int' or src == 'char') and dst == 'float':
                self.lines.append(f'{indent}f32.convert_i32_s')
            elif src == 'float' and (dst == 'int' or dst == 'char'):
                self.lines.append(f'{indent}i32.trunc_f32_s')

        elif isinstance(e, BinaryOp):
            if e.op == '=':
                if not isinstance(e.left, VarRef): raise NotImplementedError("Assign to rvalue")
                var_type = self._get_expr_type(e.left)
                val_type = self._get_expr_type(e.right)
                self.emit_expr(e.right)
                
                if var_type == 'float' and (val_type == 'int' or val_type == 'char'):
                    self.lines.append(f'{indent}f32.convert_i32_s')
                elif (var_type == 'int' or var_type == 'char') and val_type == 'float':
                    self.lines.append(f'{indent}i32.trunc_f32_s')
                
                self.lines.append(f'{indent}local.tee ${e.left.name}')
                return

            t_left = self._get_expr_type(e.left)
            t_right = self._get_expr_type(e.right)
            is_float_op = (t_left == 'float' or t_right == 'float')

            if e.op == '^':
                if isinstance(e.right, IntConst) and e.right.value == 2 and isinstance(e.left, VarRef):
                     self.emit_expr(e.left)
                     if t_left != 'float': self.lines.append(f'{indent}f32.convert_i32_s')
                     self.emit_expr(e.left)
                     if t_left != 'float': self.lines.append(f'{indent}f32.convert_i32_s')
                     self.lines.append(f'{indent}f32.mul')
                     return
                self.emit_expr(e.left)
                if t_left != 'float': self.lines.append(f'{indent}f32.convert_i32_s')
                self.emit_expr(e.right)
                self.lines.append(f'{indent}drop')
                self.lines.append(f'{indent}f32.sqrt')
                return

            self.emit_expr(e.left)
            if is_float_op and t_left != 'float': self.lines.append(f'{indent}f32.convert_i32_s')
            
            self.emit_expr(e.right)
            if is_float_op and t_right != 'float': self.lines.append(f'{indent}f32.convert_i32_s')

            if is_float_op:
                op_map = {
                    '+': 'f32.add', '-': 'f32.sub', '*': 'f32.mul', '/': 'f32.div',
                    '==': 'f32.eq', '!=': 'f32.ne', '<': 'f32.lt', '<=': 'f32.le', '>': 'f32.gt', '>=': 'f32.ge'
                }
                self.lines.append(f'{indent}{op_map.get(e.op, "f32.add")}')
            else:
                op_map = {
                    '+': 'i32.add', '-': 'i32.sub', '*': 'i32.mul', '/': 'i32.div_s',
                    '==': 'i32.eq', '!=': 'i32.ne', '<': 'i32.lt_s', '<=': 'i32.le_s', '>': 'i32.gt_s', '>=': 'i32.ge_s',
                    '&&': 'i32.and', '||': 'i32.or'
                }
                self.lines.append(f'{indent}{op_map.get(e.op, "i32.add")}')

        elif isinstance(e, UnaryOp):
            self.emit_expr(e.expr)
            t = self._get_expr_type(e.expr)
            if e.op == '-':
                if t == 'float': self.lines.append(f'{indent}f32.neg')
                else:
                    self.lines.append(f'{indent}i32.const -1')
                    self.lines.append(f'{indent}i32.mul')
            elif e.op == '!':
                self.lines.append(f'{indent}i32.eqz')

        elif isinstance(e, FuncCall):
            if e.name == 'in':
                self.lines.append(f'{indent}call $in_i32')
            elif e.name == 'out':
                arg = e.args[0]
                self.emit_expr(arg)
                t = self._get_expr_type(arg)
                if t == 'float':
                    self.lines.append(f'{indent}call $out_f32')
                else:
                    self.lines.append(f'{indent}call $out_i32')
                self.lines.append(f'{indent}i32.const 0') # out возвращает 0
            else:
                target = self.func_index.get(e.name)
                for i, arg in enumerate(e.args):
                    self.emit_expr(arg)
                    actual_t = self._get_expr_type(arg)
                    # Проверяем тип параметра функции
                    if target and i < len(target.param_types):
                        expected_t = target.param_types[i]
                        if expected_t == 'float' and actual_t != 'float':
                            self.lines.append(f'{indent}f32.convert_i32_s')
                        elif expected_t != 'float' and actual_t == 'float':
                            self.lines.append(f'{indent}i32.trunc_f32_s')
                
                self.lines.append(f'{indent}call ${e.name}')
        else:
            raise NotImplementedError(f'Unknown expr {type(e)}')