from typing import List, Dict, Optional
from compiler.src.errors import ErrorCollector, Error, ErrorType
from compiler.src.symbol_table import SymbolTable, Symbol, SymbolKind, Scope
from compiler.src.ast_nodes import *
from compiler.src.type_system import Type, TypeKind, TypeChecker

class SemanticAnalyzer:
    def __init__(self, error_collector: ErrorCollector):
        self.errors = error_collector
        self.symbol_table = SymbolTable()
        self.type_checker = TypeChecker()
        self.current_function: Optional[Symbol] = None
        self.loop_depth = 0
        self.in_assignment = False
    
    def analyze(self, program: Program):
        # 0. Регистрируем встроенные функции
        self._register_builtins()
        
        # 1. Первый проход: собираем объявления функций
        self._collect_declarations(program)
        
        # 2. Второй проход: проверяем тела функций
        self._check_functions(program)
        
        # 3. Проверяем наличие main функции
        self._check_main_function()

    def _register_builtins(self):
        # Исправляем out: она не должна требовать 0 аргументов
        out_type = Type(TypeKind.FUNCTION)
        out_type.return_type = Type(TypeKind.VOID) 
        out_type.param_types = [] 
        self.symbol_table.add_symbol(Symbol("out", SymbolKind.FUNCTION, out_type))
        
        in_type = Type(TypeKind.FUNCTION)
        in_type.return_type = Type(TypeKind.INT)
        in_type.param_types = [Type(TypeKind.STRING)] 
        self.symbol_table.add_symbol(Symbol("in", SymbolKind.FUNCTION, in_type))

    def _get_type_with_templates(self, type_name: str, template_params: List[str]) -> Type:
        if template_params and type_name in template_params:
            return Type(TypeKind.GENERIC, name=type_name)
        return self.type_checker.get_type(type_name)
    
    def _collect_template_declaration(self, func: Func):
        template_type = Type(TypeKind.TEMPLATE)
        # Очищаем имена параметров
        template_type.template_params = [p.strip() for p in (func.template_params or [])]
        
        # Регистрируем типы параметров как GENERIC, если они в списке шаблона
        template_type.param_types = [
            self._get_type_with_templates(t, template_type.template_params) 
            for t in func.param_types
        ]
        
        if func.ret_type:
            template_type.return_type = self._get_type_with_templates(func.ret_type, template_type.template_params)
        else:
            template_type.return_type = Type(TypeKind.VOID)

        symbol = Symbol(name=func.name, kind=SymbolKind.TEMPLATE, type=template_type, node=func)
        self.symbol_table.add_symbol(symbol)

    def _check_func_call(self, expr: FuncCall) -> Optional[Type]:
        func_symbol = self.symbol_table.lookup_global(expr.name)
        if not func_symbol:
            self.errors.add_error(Error(ErrorType.NAME, f"Undefined function '{expr.name}'", expr.line, expr.column))
            return None

        # 1. Подготавливаем типы (копируем из объявления)
        expected_param_types = [t for t in func_symbol.type.param_types]
        return_type = func_symbol.type.return_type

        # 2. ПОДСТАНОВКА (Substitution)
        # Если это шаблонный символ и в вызове есть <...>
        if func_symbol.kind == SymbolKind.TEMPLATE and expr.template_args:
            mapping = {}
            # formal_params — это ["T", "Type"]
            formal_params = func_symbol.type.template_params or []
            
            for i, p_name in enumerate(formal_params):
                if i < len(expr.template_args):
                    concrete_type_name = expr.template_args[i]
                    mapping[p_name] = self.type_checker.get_type(concrete_type_name)

            # Заменяем GENERIC типы в параметрах
            for i in range(len(expected_param_types)):
                t = expected_param_types[i]
                if t.kind == TypeKind.GENERIC and t.name in mapping:
                    expected_param_types[i] = mapping[t.name]
            
            # Заменяем тип возврата
            if return_type.kind == TypeKind.GENERIC and return_type.name in mapping:
                return_type = mapping[return_type.name]

        # 3. Проверка количества аргументов
        if len(expr.args) != len(expected_param_types):
            self.errors.add_error(Error(
                type=ErrorType.ARGUMENT, 
                message=f"Function '{expr.name}' expects {len(expected_param_types)} args, got {len(expr.args)}",
                line=expr.line, column=expr.column
            ))
            return return_type

        # 4. Проверка типов (теперь expected_param_types уже содержит 'int' вместо 'T')
        for i, arg in enumerate(expr.args):
            actual_type = self._check_expr(arg)
            if i < len(expected_param_types):
                expected = expected_param_types[i]
                if actual_type and not self.type_checker.can_assign(expected, actual_type):
                    self.errors.add_error(Error(
                        type=ErrorType.TYPE, 
                        message=f"Arg {i+1}: expected {expected}, got {actual_type}",
                        line=arg.line, column=arg.column
                    ))
        
        return return_type

    def _collect_declarations(self, program: Program):
        for func in program.funcs:
            if func.is_template:
                self._collect_template_declaration(func)
            else:
                self._collect_function_declaration(func)
    
    def _collect_function_declaration(self, func: Func):
        func_type = Type(TypeKind.FUNCTION)
        func_type.return_type = self.type_checker.get_type(func.ret_type) if func.ret_type else Type(TypeKind.VOID)
        func_type.param_types = [self.type_checker.get_type(t) for t in func.param_types]
        
        symbol = Symbol(
            name=func.name,
            kind=SymbolKind.FUNCTION,
            type=func_type,
            node=func
        )
        
        try:
            self.symbol_table.add_symbol(symbol)
        except ValueError:
            self.errors.add_error(Error(
                type=ErrorType.SEMANTIC,
                message=f"Function '{func.name}' already defined",
                line=func.line, column=func.column
            ))

    def _check_functions(self, program: Program):
        for func in program.funcs:
            if not func.is_template:
                self._check_function(func)
    
    def _check_function(self, func: Func):
        func_symbol = self.symbol_table.lookup_global(func.name)
        if not func_symbol: return
        
        self.current_function = func_symbol
        self.symbol_table.enter_scope(f"function_{func.name}")
        
        # Регистрация параметров в локальном scope функции
        for param_name, param_type_str in zip(func.params, func.param_types):
            param_type = self.type_checker.get_type(param_type_str)
            symbol = Symbol(name=param_name, kind=SymbolKind.PARAMETER, type=param_type)
            # Добавляем именно в текущий scope
            self.symbol_table.add_symbol(symbol)
        
        for stmt in func.body:
            self._check_statement(stmt)
        
        self.symbol_table.exit_scope()
        self.current_function = None

    def _check_statement(self, stmt: Stmt):
        if isinstance(stmt, VarDecl):
            self._check_var_decl(stmt)
        elif isinstance(stmt, Return):
            self._check_return(stmt)
        elif isinstance(stmt, ExprStmt):
            self._check_expr(stmt.expr)
        elif isinstance(stmt, IfStmt):
            self._check_if_stmt(stmt)
        elif isinstance(stmt, WhileStmt):
            self._check_while_stmt(stmt)
        elif isinstance(stmt, ForStmt):
            self._check_for_stmt(stmt)

    def _check_while_stmt(self, stmt: WhileStmt):
        self._check_expr(stmt.cond)
        self.symbol_table.enter_scope("while_loop")
        for s in stmt.body:
            self._check_statement(s)
        self.symbol_table.exit_scope()

    def _check_for_stmt(self, stmt: ForStmt):
        self.symbol_table.enter_scope("for_loop")
        if stmt.init: self._check_statement(stmt.init)
        if stmt.cond: self._check_expr(stmt.cond)
        if stmt.step: self._check_expr(stmt.step)
        for s in stmt.body:
            self._check_statement(s)
        self.symbol_table.exit_scope()

    def _check_var_decl(self, decl: VarDecl):
        var_type = self.type_checker.get_type(decl.type) if decl.type else Type(TypeKind.INT)
        
        if self.symbol_table.current_scope.lookup(decl.name, current_only=True):
            self.errors.add_error(Error(
                type=ErrorType.SEMANTIC,
                message=f"Variable '{decl.name}' already declared in this scope",
                line=decl.line, column=decl.column
            ))
            return
        
        symbol = Symbol(name=decl.name, kind=SymbolKind.VARIABLE, type=var_type, node=decl)
        self.symbol_table.add_symbol(symbol)
        
        if decl.init:
            init_type = self._check_expr(decl.init)
            if init_type and not self.type_checker.can_assign(var_type, init_type):
                self.errors.add_error(Error(
                    type=ErrorType.TYPE,
                    message=f"Cannot assign {init_type} to {var_type}",
                    line=decl.line, column=decl.column
                ))

    def _check_return(self, stmt: Return):
        if not self.current_function: return
        expected_type = self.current_function.type.return_type
        
        if stmt.expr:
            actual_type = self._check_expr(stmt.expr)
            if actual_type and not self.type_checker.can_assign(expected_type, actual_type):
                self.errors.add_error(Error(
                    type=ErrorType.RETURN,
                    message=f"Function returns {expected_type}, but got {actual_type}",
                    line=stmt.line, column=stmt.column
                ))

    def _check_if_stmt(self, stmt: IfStmt):
        cond_type = self._check_expr(stmt.cond)
        # В NumLang условие может быть int или float (0.0 - ложь)
        if cond_type and not self.type_checker.is_numeric(cond_type):
             self.errors.add_error(Error(
                type=ErrorType.TYPE, message="Condition must be numeric",
                line=stmt.cond.line, column=stmt.cond.column
            ))
        
        self.symbol_table.enter_scope("if_block")
        for s in stmt.then_body: self._check_statement(s)
        self.symbol_table.exit_scope()
        
        if stmt.else_body:
            self.symbol_table.enter_scope("else_block")
            for s in stmt.else_body: self._check_statement(s)
            self.symbol_table.exit_scope()

    def _check_expr(self, expr: Expr) -> Optional[Type]:
        if isinstance(expr, IntConst): return Type(TypeKind.INT)
        if isinstance(expr, FloatConst): return Type(TypeKind.FLOAT)
        if isinstance(expr, StringConst): return Type(TypeKind.STRING)
        if isinstance(expr, VarRef): return self._check_var_ref(expr)
        if isinstance(expr, BinaryOp): return self._check_binary_op(expr)
        if isinstance(expr, FuncCall): return self._check_func_call(expr)
        if isinstance(expr, CastExpr): return self._check_cast_expr(expr)
        if isinstance(expr, IntegralExpr): return self._check_integral_expr(expr)
        if isinstance(expr, ArrayAccess): return self._check_array_access(expr)
        return None
    
    def _check_array_access(self, expr: ArrayAccess) -> Optional[Type]:
        symbol = self.symbol_table.lookup(expr.name)
        if not symbol:
            self.errors.add_error(Error(
                type=ErrorType.NAME, message=f"Undefined variable '{expr.name}'",
                line=expr.line, column=expr.column
            ))
            return None
        
        self._check_expr(expr.expr) # Проверяем индекс
        # В нашей упрощенной системе считаем, что элементы векторов — это float
        return Type(TypeKind.FLOAT)

    def _check_var_ref(self, expr: VarRef) -> Optional[Type]:
        symbol = self.symbol_table.lookup(expr.name)
        if not symbol:
            self.errors.add_error(Error(
                type=ErrorType.NAME, message=f"Undefined variable '{expr.name}'",
                line=expr.line, column=expr.column
            ))
            return None
        return symbol.type

    def _check_binary_op(self, expr: BinaryOp) -> Optional[Type]:
        left_type = self._check_expr(expr.left)
        right_type = self._check_expr(expr.right)
        if not left_type or not right_type: return None
        
        if expr.op == '=':
            if not self.type_checker.can_assign(left_type, right_type):
                self.errors.add_error(Error(
                    type=ErrorType.TYPE, message=f"Cannot assign {right_type} to {left_type}",
                    line=expr.line, column=expr.column
                ))
            return left_type
            
        if expr.op in ['+', '-', '*', '/', '^']:
            return self.type_checker.get_common_type(left_type, right_type)
        
        if expr.op in ['==', '!=', '<', '>', '<=', '>=']:
            return Type(TypeKind.INT)
            
        return None

    def _check_cast_expr(self, expr: CastExpr) -> Optional[Type]:
        # Проверяем само выражение, которое кастуем
        self._check_expr(expr.expr)
        # Возвращаем тип, к которому приводим
        return self.type_checker.get_type(expr.target_type)

    def _check_integral_expr(self, expr: IntegralExpr) -> Optional[Type]:
        # integral(body, var, start, end)
        self.symbol_table.enter_scope("integral_scope")
        # Переменная интегрирования считается float
        self.symbol_table.add_symbol(Symbol(expr.var, SymbolKind.VARIABLE, Type(TypeKind.FLOAT)))
        self._check_expr(expr.body)
        self.symbol_table.exit_scope()
        
        self._check_expr(expr.start)
        self._check_expr(expr.end)
        return Type(TypeKind.FLOAT)

    def _check_func_call(self, expr: FuncCall) -> Optional[Type]:
        func_symbol = self.symbol_table.lookup_global(expr.name)
        if not func_symbol:
            self.errors.add_error(Error(ErrorType.NAME, f"Undefined function '{expr.name}'", expr.line, expr.column))
            return None
        
        if expr.name == "out":
            for arg in expr.args: self._check_expr(arg)
            return func_symbol.type.return_type

        # 1. Клонируем типы параметров и возврата
        expected_param_types = [t for t in func_symbol.type.param_types]
        return_type = func_symbol.type.return_type

        # 2. ПОДСТАНОВКА (SUBSTITUTION)
        if func_symbol.kind == SymbolKind.TEMPLATE and expr.template_args:
            # Создаем максимально чистый mapping
            mapping = {}
            # Имена параметров из объявления: template <type T> -> ["T"]
            formal_names = [n.strip() for n in (func_symbol.type.template_params or [])]
            
            for i, p_name in enumerate(formal_names):
                if i < len(expr.template_args):
                    # Тип из вызова: Swap<int> -> Type(INT)
                    concrete_type = self.type_checker.get_type(expr.template_args[i])
                    mapping[p_name] = concrete_type

            # Заменяем типы параметров в сигнатуре функции
            for i in range(len(expected_param_types)):
                t = expected_param_types[i]
                if t.kind == TypeKind.GENERIC:
                    # Ищем имя (например "Type") в нашем mapping
                    lookup_name = t.name.strip()
                    if lookup_name in mapping:
                        expected_param_types[i] = mapping[lookup_name]

            # Заменяем тип возврата
            if return_type and return_type.kind == TypeKind.GENERIC:
                lookup_ret = return_type.name.strip()
                if lookup_ret in mapping:
                    return_type = mapping[lookup_ret]

        # 3. ПРОВЕРКА АРГУМЕНТОВ
        # Теперь expected_param_types[i] должен быть уже Type(INT), а не GENERIC("Type")
        if len(expr.args) != len(expected_param_types):
            self.errors.add_error(Error(
                type=ErrorType.ARGUMENT, 
                message=f"Function '{expr.name}' expects {len(expected_param_types)} args, got {len(expr.args)}",
                line=expr.line, column=expr.column
            ))
            return return_type

        for i, arg in enumerate(expr.args):
            arg_type = self._check_expr(arg)
            if i < len(expected_param_types):
                expected = expected_param_types[i]
                if arg_type and not self.type_checker.can_assign(expected, arg_type):
                    self.errors.add_error(Error(
                        type=ErrorType.TYPE, 
                        message=f"Arg {i+1}: expected {expected}, got {arg_type}",
                        line=arg.line, column=arg.column
                    ))
        
        return return_type
    
    def _check_main_function(self):
        main = self.symbol_table.lookup_global("Main")
        if not main:
            self.errors.add_error(Error(ErrorType.SEMANTIC, "Function 'Main' not found"))