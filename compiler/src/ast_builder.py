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
        t = ctx.getChild(0).getText()
        name = ctx.getChild(1).getText()
        init = self.visit(ctx.expr()) if ctx.expr() else None
        return self._with_pos(VarDecl(type=t, name=name, init=init), ctx)

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
        cond = self.visit(ctx.expr())
        then_body = []
        bodies = ctx.func_body()
        if bodies:
            for s in bodies[0].statement():
                n = self.visit(s)
                if n: then_body.append(n)
        
        else_body = None
        if len(bodies) > 1:
            else_body = [self.visit(s) for s in bodies[1].statement() if self.visit(s)]
            
        return self._with_pos(IfStmt(cond=cond, then_body=then_body, else_body=else_body), ctx)

    def visitFunc_call(self, ctx):
        name = ctx.ID().getText()
        args = [self.visit(e) for e in (ctx.expr() if isinstance(ctx.expr(), list) else [ctx.expr()])] if ctx.expr() else []
        return self._with_pos(FuncCall(name=name, args=args), ctx)
    
    def visitInput_expr(self, ctx):
        return self._with_pos(FuncCall(name='in', args=[]), ctx)

    def visitOutput_expr(self, ctx):
        arg = self.visit(ctx.expr())
        return self._with_pos(FuncCall(name="out", args=[arg]), ctx)

    def visitCast_expr(self, ctx):
        target = ctx.getChild(1).getText()
        expr = self.visit(ctx.expr())
        return self._with_pos(CastExpr(target_type=target, expr=expr), ctx)