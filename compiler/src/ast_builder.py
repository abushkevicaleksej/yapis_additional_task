from compiler.bones.grammarNumLangVisitor import grammarNumLangVisitor
from compiler.bones.grammarNumLangParser import grammarNumLangParser
from compiler.src.ast_nodes import *

class ASTBuilder(grammarNumLangVisitor):
    def visitChildren(self, node):
        return super().visitChildren(node)
    
    def visitProg(self, ctx):
        funcs = []
        for child in ctx.children:
            res = self.visit(child)
            if res and isinstance(res, Func):
                funcs.append(res)
        return Program(funcs=funcs)

    # --- Template Declaration ---
    def visitTemplate_decl(self, ctx):
        # template_decl: 'template' '<' template_param_list '>' func_decl;
        
        # 1. Извлекаем параметры шаблона (T, Type и т.д.)
        template_params = []
        if ctx.template_param_list():
            for tp in ctx.template_param_list().template_param():
                # template_param: 'type' ID
                # ID обычно второй ребенок (индекс 1) или можно найти по типу
                template_params.append(tp.ID().getText())
        
        # 2. Посещаем вложенную декларацию функции
        func_node = self.visit(ctx.func_decl())
        
        # 3. Добавляем информацию о шаблоне в объект функции
        if isinstance(func_node, Func):
            func_node.is_template = True
            func_node.template_params = template_params
            
        return func_node

    # --- Function Declaration ---
    def visitFunc_decl(self, ctx):
        return self._visit_func_decl(ctx)
    
    def visitFunc_main(self, ctx):
        return self._visit_func_decl(ctx)

    def _visit_func_decl(self, ctx):
        # Тип возврата
        ret_type = None
        if hasattr(ctx, 'BASE_TYPE') and ctx.BASE_TYPE():
            ret_type = ctx.BASE_TYPE().getText()
        else:
            # Если тип шаблонный (например T), он будет первым токеном (не function)
            first = ctx.getChild(0).getText()
            if first != 'function':
                ret_type = first

        # Имя функции
        name = None
        if hasattr(ctx, 'FUNC_MAIN_ID'):
             name = ctx.FUNC_MAIN_ID().getText()
        else:
            # Ищем ID после слова function
            found = False
            for child in ctx.children:
                if child.getText() == 'function':
                    found = True
                    continue
                if found and hasattr(child, 'getSymbol') and child.getSymbol().type == grammarNumLangParser.ID:
                    name = child.getText()
                    break

        # Параметры и их типы
        params = []
        param_types = []
        if hasattr(ctx, 'param_list') and ctx.param_list():
            pl = ctx.param_list()
            for p in pl.param():
                # Структура param: TYPE NAME
                p_type = p.getChild(0).getText()
                p_name = p.getChild(p.getChildCount()-1).getText()
                params.append(p_name)
                param_types.append(p_type)
        
        # Тело функции
        stmts = []
        if hasattr(ctx, 'func_body') and ctx.func_body():
            fb = ctx.func_body()
            for s in fb.statement():
                node = self.visit(s)
                if node: stmts.append(node)

        # Важно: здесь мы НЕ парсим template_params, это делает visitTemplate_decl
        return Func(name=name, params=params, param_types=param_types, 
                    body=stmts, ret_type=ret_type,
                    is_template=False, template_params=None)

    # --- Statements ---
    def visitVar_decl(self, ctx):
        # var_decl: TYPE ID ...
        t = ctx.getChild(0).getText()
        name = ctx.getChild(1).getText()
        init = None
        if ctx.expr():
            init = self.visit(ctx.expr())
        return VarDecl(type=t, name=name, init=init)

    def visitReturn_statement(self, ctx):
        e = self.visit(ctx.expr()) if ctx.expr() else None
        return Return(expr=e)

    def visitExpr_statement(self, ctx):
        return ExprStmt(expr=self.visit(ctx.expr()))

    def visitIf_statement(self, ctx):
        cond = self.visit(ctx.expr())
        then_body = []
        else_body = None
        bodies = ctx.func_body()
        if bodies:
            for s in bodies[0].statement():
                n = self.visit(s)
                if n: then_body.append(n)
        
        else_idx = -1
        for i in range(ctx.getChildCount()):
            if ctx.getChild(i).getText() == 'else':
                else_idx = i; break
        
        if else_idx != -1:
            child = ctx.getChild(else_idx + 1)
            if isinstance(child, grammarNumLangParser.If_statementContext):
                else_body = [self.visit(child)]
            elif len(bodies) > 1:
                else_body = []
                for s in bodies[1].statement():
                    n = self.visit(s)
                    if n: else_body.append(n)
        return IfStmt(cond=cond, then_body=then_body, else_body=else_body)

    def visitWhile_statement(self, ctx):
        cond = self.visit(ctx.expr())
        body = []
        if ctx.func_body():
            for s in ctx.func_body().statement():
                n = self.visit(s)
                if n: body.append(n)
        return WhileStmt(cond=cond, body=body)

    def visitFor_statement(self, ctx):
        init_node = None
        if ctx.var_decl(): init_node = self.visit(ctx.var_decl())
        exprs = ctx.expr()
        cond_node, step_node = None, None
        
        if init_node:
            if exprs and len(exprs) >= 1: cond_node = self.visit(exprs[0])
            if exprs and len(exprs) >= 2: step_node = self.visit(exprs[1])
        else:
            if len(exprs) == 3:
                init_node = ExprStmt(self.visit(exprs[0]))
                cond_node = self.visit(exprs[1])
                step_node = self.visit(exprs[2])
            elif len(exprs) == 2:
                cond_node = self.visit(exprs[0])
                step_node = self.visit(exprs[1])
            elif len(exprs) == 1:
                cond_node = self.visit(exprs[0])

        body = []
        if ctx.func_body():
            for s in ctx.func_body().statement():
                n = self.visit(s)
                if n: body.append(n)
        return ForStmt(init=init_node, cond=cond_node, step=step_node, body=body)

    # --- Expressions ---
    def visitExpr(self, ctx): return self.visit(ctx.assignment_expr())
    
    def visitAssignment_expr(self, ctx):
        if ctx.getChildCount() > 1 and ctx.getChild(1).getText() == '=':
            return BinaryOp(op='=', left=self.visit(ctx.logic_expr()), right=self.visit(ctx.assignment_expr()))
        return self.visit(ctx.logic_expr())

    def visitLogic_expr(self, ctx): return self._visit_binary_op(ctx, ctx.comparison_expr)
    def visitComparison_expr(self, ctx): return self._visit_binary_op(ctx, ctx.additive_expr)
    def visitAdditive_expr(self, ctx): return self._visit_binary_op(ctx, ctx.multiplicative_expr)
    def visitMultiplicative_expr(self, ctx): return self._visit_binary_op(ctx, ctx.unary_expr)

    def _visit_binary_op(self, ctx, rule):
        operands = rule()
        if not isinstance(operands, list): operands = [operands]
        lhs = self.visit(operands[0])
        for i in range(1, len(operands)):
            op = ctx.getChild(2*i - 1).getText()
            rhs = self.visit(operands[i])
            lhs = BinaryOp(op=op, left=lhs, right=rhs)
        return lhs

    def visitUnary_expr(self, ctx):
        if ctx.getChildCount() == 2:
            return UnaryOp(op=ctx.getChild(0).getText(), expr=self.visit(ctx.unary_expr()))
        return self.visit(ctx.primary_expr())

    def visitPrimary_expr(self, ctx):
        if ctx.INT(): return IntConst(int(ctx.INT().getText()))
        if ctx.FLOAT(): return FloatConst(float(ctx.FLOAT().getText()))
        if ctx.STRING(): return StringConst(ctx.STRING().getText()[1:-1])
        if ctx.CHAR(): return CharConst(ctx.CHAR().getText()[1:-1])
        if ctx.ID(): return VarRef(ctx.ID().getText())
        if ctx.func_call(): return self.visit(ctx.func_call())
        if ctx.expr(): return self.visit(ctx.expr())
        if ctx.special_expr(): return self.visit(ctx.special_expr())
        return None

    def visitFunc_call(self, ctx):
        args = []
        if ctx.expr():
            ex = ctx.expr()
            if not isinstance(ex, list): ex = [ex]
            for e in ex: args.append(self.visit(e))
        t_args = None
        if ctx.template_arg_list():
            t_args = [t.getText() for t in ctx.template_arg_list().template_arg()]
        return FuncCall(name=ctx.ID().getText(), args=args, template_args=t_args)

    def visitInput_expr(self, ctx):
        s = ctx.STRING().getText()[1:-1] if ctx.STRING() else ""
        return FuncCall(name='in', args=[StringConst(s)])

    def visitOutput_expr(self, ctx):
        return FuncCall(name='out', args=[self.visit(ctx.expr())])
    
    def visitCast_expr(self, ctx):
        return CastExpr(target_type=ctx.getChild(1).getText(), expr=self.visit(ctx.expr()))