from typing import List, Dict, Optional
from compiler.src.errors import ErrorCollector, Error, ErrorType
from compiler.src.symbol_table import SymbolTable, Symbol, SymbolKind, Scope
from compiler.src.ast_nodes import *

class SemanticAnalyzer:
    def __init__(self, error_collector: ErrorCollector):
        self.errors = error_collector
        self.symbol_table = SymbolTable()
        self.type_checker = TypeChecker()
        self.current_function: Optional[Symbol] = None
        self.loop_depth = 0
        self.in_assignment = False
        self.template_instances: Dict[str, Func] = {}
    
    def analyze(self, program: Program):
        # Первый проход: собираем объявления функций
        self._collect_declarations(program)
        
        # Второй проход: проверяем тела функций
        self._check_functions(program)
        
        # Проверяем наличие main функции
        self._check_main_function()
    
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
        except ValueError as e:
            self.errors.add_error(Error(
                type=ErrorType.SEMANTIC,
                message=f"Function '{func.name}' already defined",
                context=f"Previous declaration in scope '{symbol.scope.name}'"
            ))
    
    def _collect_template_declaration(self, func: Func):
        template_type = Type(TypeKind.TEMPLATE)
        template_type.template_params = func.template_params
        
        symbol = Symbol(
            name=func.name,
            kind=SymbolKind.TEMPLATE,
            type=template_type,
            node=func
        )
        
        try:
            self.symbol_table.add_symbol(symbol)
        except ValueError as e:
            self.errors.add_error(Error(
                type=ErrorType.SEMANTIC,
                message=f"Template '{func.name}' already defined"
            ))
    
    def _check_functions(self, program: Program):
        for func in program.funcs:
            if not func.is_template:
                self._check_function(func)
    
    def _check_function(self, func: Func):
        func_symbol = self.symbol_table.lookup_global(func.name)
        if not func_symbol:
            return
        
        self.current_function = func_symbol
        self.symbol_table.enter_scope(f"function_{func.name}")
        
        # Добавляем параметры в scope
        for param_name, param_type in zip(func.params, func.param_types):
            param_symbol = Symbol(
                name=param_name,
                kind=SymbolKind.PARAMETER,
                type=self.type_checker.get_type(param_type)
            )
            self.symbol_table.add_symbol(param_symbol)
        
        # Проверяем тело функции
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
        # ... другие типы statements
    
    def _check_var_decl(self, decl: VarDecl):
        var_type = self.type_checker.get_type(decl.type) if decl.type else Type(TypeKind.INT)
        
        # Проверяем, не объявлена ли переменная уже
        existing = self.symbol_table.lookup(decl.name)
        if existing:
            self.errors.add_error(Error(
                type=ErrorType.SEMANTIC,
                message=f"Variable '{decl.name}' already declared in this scope"
            ))
            return
        
        symbol = Symbol(
            name=decl.name,
            kind=SymbolKind.VARIABLE,
            type=var_type,
            node=decl
        )
        self.symbol_table.add_symbol(symbol)
        
        if decl.init:
            init_type = self._check_expr(decl.init)
            if init_type and not self.type_checker.can_assign(var_type, init_type):
                self.errors.add_error(Error(
                    type=ErrorType.TYPE,
                    message=f"Cannot assign {init_type} to {var_type}"
                ))
            else:
                symbol.is_initialized = True
    
    def _check_return(self, stmt: Return):
        if not self.current_function:
            self.errors.add_error(Error(
                type=ErrorType.SEMANTIC,
                message="Return statement outside of function"
            ))
            return
        
        expected_type = self.current_function.type.return_type
        
        if stmt.expr:
            actual_type = self._check_expr(stmt.expr)
            if actual_type and not self.type_checker.can_assign(expected_type, actual_type):
                self.errors.add_error(Error(
                    type=ErrorType.RETURN,
                    message=f"Function returns {expected_type}, but got {actual_type}"
                ))
        elif expected_type.kind != TypeKind.VOID:
            self.errors.add_error(Error(
                type=ErrorType.RETURN,
                message=f"Non-void function must return a value"
            ))
    
    def _check_if_stmt(self, stmt: IfStmt):
        cond_type = self._check_expr(stmt.cond)
        if cond_type and cond_type.kind != TypeKind.INT:
            self.errors.add_error(Error(
                type=ErrorType.TYPE,
                message=f"Condition must be of type int, got {cond_type}"
            ))
        
        self.symbol_table.enter_scope("if_block")
        for s in stmt.then_body:
            self._check_statement(s)
        self.symbol_table.exit_scope()
        
        if stmt.else_body:
            self.symbol_table.enter_scope("else_block")
            for s in stmt.else_body:
                self._check_statement(s)
            self.symbol_table.exit_scope()
    
    def _check_while_stmt(self, stmt: WhileStmt):
        cond_type = self._check_expr(stmt.cond)
        if cond_type and cond_type.kind != TypeKind.INT:
            self.errors.add_error(Error(
                type=ErrorType.TYPE,
                message=f"While condition must be of type int, got {cond_type}"
            ))
        
        self.loop_depth += 1
        self.symbol_table.enter_scope("while_block")
        for s in stmt.body:
            self._check_statement(s)
        self.symbol_table.exit_scope()
        self.loop_depth -= 1
    
    def _check_for_stmt(self, stmt: ForStmt):
        self.symbol_table.enter_scope("for_block")
        self.loop_depth += 1
        
        if stmt.init:
            self._check_statement(stmt.init)
        
        if stmt.cond:
            cond_type = self._check_expr(stmt.cond)
            if cond_type and cond_type.kind != TypeKind.INT:
                self.errors.add_error(Error(
                    type=ErrorType.TYPE,
                    message=f"For condition must be of type int, got {cond_type}"
                ))
        
        if stmt.step:
            self._check_expr(stmt.step)
        
        for s in stmt.body:
            self._check_statement(s)
        
        self.symbol_table.exit_scope()
        self.loop_depth -= 1
    
    def _check_expr(self, expr: Expr) -> Optional[Type]:
        if isinstance(expr, IntConst):
            return Type(TypeKind.INT)
        elif isinstance(expr, FloatConst):
            return Type(TypeKind.FLOAT)
        elif isinstance(expr, CharConst):
            return Type(TypeKind.CHAR)
        elif isinstance(expr, StringConst):
            return Type(TypeKind.STRING)
        elif isinstance(expr, VarRef):
            return self._check_var_ref(expr)
        elif isinstance(expr, BinaryOp):
            return self._check_binary_op(expr)
        elif isinstance(expr, UnaryOp):
            return self._check_unary_op(expr)
        elif isinstance(expr, FuncCall):
            return self._check_func_call(expr)
        elif isinstance(expr, CastExpr):
            return self._check_cast_expr(expr)
        return None
    
    def _check_var_ref(self, expr: VarRef) -> Optional[Type]:
        symbol = self.symbol_table.lookup(expr.name)
        if not symbol:
            self.errors.add_error(Error(
                type=ErrorType.NAME,
                message=f"Undefined variable '{expr.name}'"
            ))
            return None
        
        symbol.is_used = True
        return symbol.type
    
    def _check_binary_op(self, expr: BinaryOp) -> Optional[Type]:
        left_type = self._check_expr(expr.left)
        right_type = self._check_expr(expr.right)
        
        if not left_type or not right_type:
            return None
        
        if expr.op == '=':
            # Проверяем, что левая часть - lvalue
            if not isinstance(expr.left, VarRef):
                self.errors.add_error(Error(
                    type=ErrorType.SEMANTIC,
                    message="Left side of assignment must be a variable"
                ))
                return None
            
            if not self.type_checker.can_assign(left_type, right_type):
                self.errors.add_error(Error(
                    type=ErrorType.TYPE,
                    message=f"Cannot assign {right_type} to {left_type}"
                ))
            return left_type
        
        # Арифметические операции
        if expr.op in ['+', '-', '*', '/', '^']:
            if not (self.type_checker.is_numeric(left_type) and 
                   self.type_checker.is_numeric(right_type)):
                self.errors.add_error(Error(
                    type=ErrorType.TYPE,
                    message=f"Operator '{expr.op}' requires numeric operands"
                ))
                return None
            
            common_type = self.type_checker.get_common_type(left_type, right_type)
            if not common_type:
                self.errors.add_error(Error(
                    type=ErrorType.TYPE,
                    message=f"Incompatible types for '{expr.op}': {left_type} and {right_type}"
                ))
                return None
            return common_type
        
        # Операции сравнения
        if expr.op in ['==', '!=', '<', '>', '<=', '>=']:
            if not (self.type_checker.is_numeric(left_type) and 
                   self.type_checker.is_numeric(right_type)):
                self.errors.add_error(Error(
                    type=ErrorType.TYPE,
                    message=f"Comparison '{expr.op}' requires numeric operands"
                ))
                return None
            
            return Type(TypeKind.INT)  # Boolean результат
        
        # Логические операции
        if expr.op in ['&&', '||']:
            if left_type.kind != TypeKind.INT or right_type.kind != TypeKind.INT:
                self.errors.add_error(Error(
                    type=ErrorType.TYPE,
                    message=f"Logical operator '{expr.op}' requires integer operands"
                ))
                return None
            
            return Type(TypeKind.INT)
        
        return None
    
    def _check_func_call(self, expr: FuncCall) -> Optional[Type]:
        func_symbol = self.symbol_table.lookup_global(expr.name)
        if not func_symbol:
            self.errors.add_error(Error(
                type=ErrorType.NAME,
                message=f"Undefined function '{expr.name}'"
            ))
            return None
        
        if func_symbol.kind == SymbolKind.TEMPLATE:
            return self._check_template_call(expr, func_symbol)
        
        # Проверка обычной функции
        if len(expr.args) != len(func_symbol.type.param_types):
            self.errors.add_error(Error(
                type=ErrorType.ARGUMENT,
                message=f"Function '{expr.name}' expects {len(func_symbol.type.param_types)} arguments, got {len(expr.args)}"
            ))
        
        # Проверяем типы аргументов
        for i, (arg, expected_type) in enumerate(zip(expr.args, func_symbol.type.param_types)):
            actual_type = self._check_expr(arg)
            if actual_type and not self.type_checker.can_assign(expected_type, actual_type):
                self.errors.add_error(Error(
                    type=ErrorType.TYPE,
                    message=f"Argument {i+1} of '{expr.name}': expected {expected_type}, got {actual_type}"
                ))
        
        return func_symbol.type.return_type
    
    def _check_template_call(self, expr: FuncCall, template_symbol: Symbol) -> Optional[Type]:
        template_func = template_symbol.node
        
        if not expr.template_args:
            self.errors.add_error(Error(
                type=ErrorType.TEMPLATE,
                message=f"Template function '{expr.name}' requires type arguments"
            ))
            return None
        
        if len(expr.template_args) != len(template_func.template_params):
            self.errors.add_error(Error(
                type=ErrorType.TEMPLATE,
                message=f"Template '{expr.name}' expects {len(template_func.template_params)} type parameters"
            ))
            return None
        
        # TODO: Проверка инстанцирования шаблона
        # Здесь можно добавить логику проверки корректности подстановки типов
        
        # Для простоты возвращаем тип из шаблона
        return self.type_checker.get_type(template_func.ret_type)
    
    def _check_main_function(self):
        main_symbol = self.symbol_table.lookup_global("Main")
        if not main_symbol:
            self.errors.add_error(Error(
                type=ErrorType.SEMANTIC,
                message="Program must have a 'Main' function"
            ))
            return
        
        if main_symbol.kind != SymbolKind.FUNCTION:
            self.errors.add_error(Error(
                type=ErrorType.SEMANTIC,
                message="'Main' must be a function"
            ))
        
        if main_symbol.type.return_type.kind != TypeKind.INT:
            self.errors.add_error(Error(
                type=ErrorType.SEMANTIC,
                message="'Main' function must return int"
            ))
        
        if main_symbol.type.param_types:
            self.errors.add_error(Error(
                type=ErrorType.SEMANTIC,
                message="'Main' function must have no parameters"
            ))