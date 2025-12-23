from compiler.bones.grammarNumLangVisitor import grammarNumLangVisitor
from compiler.bones.grammarNumLangParser import grammarNumLangParser
from compiler.src.ast_nodes import *

class ASTBuilder(grammarNumLangVisitor):
    def _with_pos(self, node, ctx):
        if hasattr(ctx, 'start'):
            node.line = ctx.start.line
            node.column = ctx.start.column
        return node

    def visitProg(self, ctx):
        funcs = []
        for child in ctx.children:
            res = self.visit(child)
            if isinstance(res, Func):
                funcs.append(res)
        return self._with_pos(Program(funcs=funcs), ctx)

    def _visit_func_decl(self, ctx):
        # Тип возврата
        ret_type = ctx.getChild(0).getText() if ctx.getChild(0).getText() != 'function' else ctx.BASE_TYPE().getText()
        
        # Имя
        name = ctx.FUNC_MAIN_ID().getText() if hasattr(ctx, 'FUNC_MAIN_ID') and ctx.FUNC_MAIN_ID() else None
        if not name:
            for i in range(ctx.getChildCount()):
                if ctx.getChild(i).getText() == 'function':
                    name = ctx.getChild(i+1).getText()
                    break

        # Параметры
        params, param_types = [], []
        if ctx.param_list():
            for p in ctx.param_list().param():
                param_types.append(p.getChild(0).getText())
                params.append(p.getChild(p.getChildCount()-1).getText())
        
        # Тело
        stmts = []
        if ctx.func_body():
            for s in ctx.func_body().statement():
                node = self.visit(s)
                if node: stmts.append(node)

        return self._with_pos(Func(
            name=name, params=params, param_types=param_types, 
            body=stmts, ret_type=ret_type
        ), ctx)

    def visitFunc_decl(self, ctx): return self._visit_func_decl(ctx)
    def visitFunc_main(self, ctx): return self._visit_func_decl(ctx)

    def visitVar_decl(self, ctx):
        # Теперь var_decl — это просто обертка над var_init
        if ctx.var_init():
            return self.visit(ctx.var_init())
        return None
    
    def visitVar_init(self, ctx):
        # Правило: (BASE_TYPE | ID) ID ('=' expr)?
        # Тип — это всегда самый первый ребенок
        var_type = ctx.getChild(0).getText()
        
        # Получаем все ID в этом правиле
        ids = ctx.ID()
        if isinstance(ids, list):
            # Если это 'Vector v', то ids[0] — это 'Vector' (тип), ids[1] — 'v' (имя)
            # Если это 'int i', то ids[0] — это 'i' (имя), а тип взят из BASE_TYPE
            name = ids[-1].getText() 
        else:
            name = ids.getText()

        init = self.visit(ctx.expr()) if ctx.expr() else None
        return self._with_pos(VarDecl(type=var_type, name=name, init=init), ctx)

    def visitSolveLU_expr(self, ctx):
        exprs = ctx.expr()
        return self._with_pos(SolveLUExpr(matrix=self.visit(exprs[0]), vector=self.visit(exprs[1])), ctx)

    def visitDerivative_expr(self, ctx):
        return self._with_pos(DerivativeExpr(body=self.visit(ctx.expr()), var=ctx.ID().getText()), ctx)

    def visitReturn_statement(self, ctx):
        expr = self.visit(ctx.expr()) if ctx.expr() else None
        return self._with_pos(Return(expr=expr), ctx)

    def visitExpr_statement(self, ctx):
        return self._with_pos(ExprStmt(expr=self.visit(ctx.expr())), ctx)

    def visitPrimary_expr(self, ctx):
        node = None
        if ctx.INT(): node = IntConst(value=int(ctx.INT().getText()))
        elif ctx.FLOAT(): node = FloatConst(value=float(ctx.FLOAT().getText()))
        elif ctx.ID(): node = VarRef(name=ctx.ID().getText())
        elif ctx.STRING(): node = StringConst(value=ctx.STRING().getText()[1:-1])
        elif ctx.func_call(): node = self.visit(ctx.func_call())
        elif ctx.expr(): return self.visit(ctx.expr())
        elif ctx.special_expr(): node = self.visit(ctx.special_expr())
        elif ctx.array_access(): return self.visit(ctx.array_access())
        
        return self._with_pos(node, ctx) if node else None

    def visitBinaryOp_helper(self, ctx, next_rule):
        operands = next_rule()
        if not isinstance(operands, list): operands = [operands]
        lhs = self.visit(operands[0])
        for i in range(1, len(operands)):
            op = ctx.getChild(2*i - 1).getText()
            rhs = self.visit(operands[i])
            lhs = self._with_pos(BinaryOp(op=op, left=lhs, right=rhs), ctx)
        return lhs

    def visitAdditive_expr(self, ctx): return self.visitBinaryOp_helper(ctx, ctx.multiplicative_expr)
    def visitMultiplicative_expr(self, ctx): return self.visitBinaryOp_helper(ctx, ctx.unary_expr)
    
    def visitLogic_expr(self, ctx): return self.visitBinaryOp_helper(ctx, ctx.comparison_expr)
    def visitComparison_expr(self, ctx): return self.visitBinaryOp_helper(ctx, ctx.additive_expr)

    def visitAssignment_expr(self, ctx):
        if ctx.getChildCount() > 1 and ctx.getChild(1).getText() == '=':
            lhs = self.visit(ctx.logic_expr())
            rhs = self.visit(ctx.assignment_expr())
            return self._with_pos(BinaryOp(op='=', left=lhs, right=rhs), ctx)
        return self.visit(ctx.logic_expr())

    def visitIf_statement(self, ctx):
        # 1. Условие if
        cond = self.visit(ctx.expr())
        
        # 2. Ветка THEN (всегда первый func_body)
        then_body = []
        if ctx.func_body():
            for s in ctx.func_body(0).statement():
                node = self.visit(s)
                if node: then_body.append(node)
        
        # 3. Ветка ELSE
        else_body = None
        
        # Если есть вложенный if (else if ...)
        if ctx.if_statement():
            else_body = [self.visit(ctx.if_statement())]
            
        # Если есть блок else { ... } (второй func_body в контексте)
        elif len(ctx.func_body()) > 1:
            else_body = []
            for s in ctx.func_body(1).statement():
                node = self.visit(s)
                if node: else_body.append(node)
                    
        return self._with_pos(IfStmt(cond=cond, then_body=then_body, else_body=else_body), ctx)

    def visitFunc_call(self, ctx):
        name = ctx.ID().getText()
        args = [self.visit(e) for e in (ctx.expr() if isinstance(ctx.expr(), list) else [ctx.expr()])] if ctx.expr() else []
        return self._with_pos(FuncCall(name=name, args=args), ctx)
    
    def visitInput_expr(self, ctx):
        # input_expr: 'in' '(' STRING ')'
        prompt_text = ""
        if ctx.STRING():
            prompt_text = ctx.STRING().getText()[1:-1] # Убираем кавычки
        
        # Создаем FuncCall с одним строковым аргументом
        args = [StringConst(value=prompt_text)]
        return self._with_pos(FuncCall(name='in', args=args), ctx)

    def visitOutput_expr(self, ctx):
        arg = self.visit(ctx.expr())
        return self._with_pos(FuncCall(name="out", args=[arg]), ctx)

    def visitCast_expr(self, ctx):
        target = ctx.getChild(1).getText()
        expr = self.visit(ctx.expr())
        return self._with_pos(CastExpr(target_type=target, expr=expr), ctx)
    
    def visitWhile_statement(self, ctx):
        cond = self.visit(ctx.expr())
        body = []
        if ctx.func_body():
            for s in ctx.func_body().statement():
                node = self.visit(s)
                if node: body.append(node)
        return self._with_pos(WhileStmt(cond=cond, body=body), ctx)
    
    def visitFor_statement(self, ctx):
        # for ( (var_init | expr)? ; expr? ; expr? )
        init = None
        if ctx.var_init():
            init = self.visit(ctx.var_init())
        elif ctx.expr():
            # Если первый элемент в скобках — выражение
            init = self.visit(ctx.expr(0))

        # Выражений в скобках может быть несколько. 
        # Нужно аккуратно сопоставить их с cond и step.
        expr_count = len(ctx.expr())
        current_expr_idx = 0
        if not ctx.var_init() and expr_count > 0:
            current_expr_idx = 1 # т.к. нулевой ушел в init
        
        cond = self.visit(ctx.expr(current_expr_idx)) if current_expr_idx < expr_count else None
        step = self.visit(ctx.expr(current_expr_idx + 1)) if (current_expr_idx + 1) < expr_count else None

        body = []
        if ctx.func_body():
            for s in ctx.func_body().statement():
                node = self.visit(s)
                if node: body.append(node)
        return self._with_pos(ForStmt(init=init, cond=cond, step=step, body=body), ctx)
    
    def visitIntegral_expr(self, ctx):
        # В грамматике: 'integral' '(' expr ',' ID ',' ID ')'
        # ctx.expr() вернет один узел
        # ctx.ID() вернет список из двух ID
        
        body = self.visit(ctx.expr())
        
        # Получаем ID границ из списка
        ids = ctx.ID()
        start_id = ids[0].getText() if len(ids) > 0 else "a"
        end_id = ids[1].getText() if len(ids) > 1 else "b"
        
        # Переменную интегрирования в данной грамматике взять не откуда (всего 2 ID),
        # поэтому захардкодим "x" или добавим логику.
        var_name = "x" 
        
        # Конструируем узлы для границ (т.к. это ID, создаем VarRef)
        start_node = VarRef(name=start_id)
        end_node = VarRef(name=end_id)
        
        return self._with_pos(IntegralExpr(
            body=body, 
            var=var_name, 
            start=start_node, 
            end=end_node
        ), ctx)

    def visitSpecial_expr(self, ctx):
        if ctx.integral_expr(): return self.visit(ctx.integral_expr())
        if ctx.derivative_expr(): return self.visit(ctx.derivative_expr())
        if ctx.solveLU_expr(): return self.visit(ctx.solveLU_expr())
        return self.visitChildren(ctx)
    
    def visitSolveLU_expr(self, ctx):
        # solveLU(expr, expr)
        exprs = ctx.expr()
        return self._with_pos(SolveLUExpr(
            matrix=self.visit(exprs[0]), 
            vector=self.visit(exprs[1])
        ), ctx)
    
    def visitDerivative_expr(self, ctx):
        # derivative(expr, ID)
        body = self.visit(ctx.expr())
        var_name = ctx.ID().getText()
        return self._with_pos(DerivativeExpr(body=body, var=var_name), ctx)
    
    def visitArray_access(self, ctx):
        # В грамматике это: ID '[' expr ']'
        name = ctx.ID().getText()
        index = self.visit(ctx.expr())
        return self._with_pos(ArrayAccess(name=name, expr=index), ctx)