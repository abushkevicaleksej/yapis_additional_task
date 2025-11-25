from bones.grammarNumLangVisitor import grammarNumLangVisitor
from bones.grammarNumLangParser import grammarNumLangParser
from src.ast_nodes import *

class ASTBuilder(grammarNumLangVisitor):
    def visitChildren(self, node):
        return super().visitChildren(node)
    
    def visitFunc_decl(self, ctx):
        return self._visit_func_decl(ctx)
    
    def visitFunc_main(self, ctx):
        return self._visit_func_decl(ctx)

    def _visit_func_decl(self, ctx):
        ret_type = None
        if hasattr(ctx, 'BASE_TYPE') and ctx.BASE_TYPE():
            ret_type = ctx.BASE_TYPE().getText()
        else:
            first = ctx.getChild(0).getText()
            if first in ("int", "float", "char", "string", "void"):
                ret_type = first
        
        name = None
        # Ищем имя функции
        if hasattr(ctx, 'FUNC_MAIN_ID'):
             name = ctx.FUNC_MAIN_ID().getText()
        else:
            found_function = False
            for child in ctx.children:
                txt = child.getText()
                if txt == 'function':
                    found_function = True
                    continue
                if found_function and txt.isidentifier():
                    name = txt
                    break
        
        if not name and hasattr(ctx, 'ID'):
             # Fallback
             try: name = ctx.ID().getText()
             except: pass

        # Сбор параметров И их типов
        params = []
        param_types = []
        if hasattr(ctx, 'param_list') and ctx.param_list():
            pl = ctx.param_list()
            for p in pl.param():
                # param: BASE_TYPE ID | ID '[' ']' ID | ID ID
                # Упрощенно берем первый токен как тип, последний как имя
                p_type = p.getChild(0).getText()
                p_name = p.getChild(p.getChildCount()-1).getText()
                params.append(p_name)
                param_types.append(p_type)
        
        stmts = []
        if hasattr(ctx, 'func_body') and ctx.func_body():
            fb = ctx.func_body()
            for s in fb.statement():
                node = self.visit(s)
                if node: stmts.append(node)
        
        templ_params = None
        if hasattr(ctx, 'template_params') and ctx.template_params():
            templ_params = [tp.getText() for tp in ctx.template_params().template_arg()]

        is_template = (templ_params is not None)
        return Func(name=name, params=params, param_types=param_types, 
                    body=stmts, ret_type=ret_type,
                    is_template=is_template, template_params=templ_params)

    def visitVar_decl(self, ctx):
        t = None
        name = None
        if ctx.BASE_TYPE():
            t = ctx.BASE_TYPE().getText()
            name = ctx.ID(0).getText()
        else:
            # Случай ID ID
            if len(ctx.ID()) > 1:
                t = ctx.ID(0).getText()
                name = ctx.ID(1).getText()
            else:
                name = ctx.ID(0).getText()

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
        
        # Поиск else
        else_index = -1
        for i in range(ctx.getChildCount()):
            if ctx.getChild(i).getText() == 'else':
                else_index = i
                break
        
        if else_index != -1:
            child = ctx.getChild(else_index + 1)
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
        # Упрощенная логика
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
    def visitExpr(self, ctx):
        return self.visit(ctx.assignment_expr())

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