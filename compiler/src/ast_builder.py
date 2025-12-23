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
    
    def visitTemplate_decl(self, ctx):
        template_params = []
        if ctx.template_param_list():
            for p in ctx.template_param_list().template_param():
                template_params.append(p.ID().getText())
        
        func_node = self.visit(ctx.func_decl())
        
        func_node.is_template = True
        func_node.template_params = template_params
        return func_node

    def _visit_func_decl(self, ctx):
        is_template = False
        template_params = []
        
        for i in range(ctx.getChildCount()):
            if ctx.getChild(i).getText() == 'template':
                is_template = True
                start_idx = -1
                for j in range(i, ctx.getChildCount()):
                    if ctx.getChild(j).getText() == '<': start_idx = j
                    if ctx.getChild(j).getText() == '>':
                        for k in range(start_idx + 1, j):
                            token = ctx.getChild(k).getText().strip()
                            if token not in [',', 'type', '<', '>']:
                                template_params.append(token)
                        break
                break

        name = ""
        ret_type = "void"
        func_keyword_idx = -1
        
        for i in range(ctx.getChildCount()):
            if ctx.getChild(i).getText() == "function":
                func_keyword_idx = i
                name = ctx.getChild(i+1).getText()
                break
        
        if func_keyword_idx > 0:
            potential_ret = ctx.getChild(func_keyword_idx - 1).getText()
            if potential_ret not in ['>', 'template']:
                ret_type = potential_ret

        if hasattr(ctx, 'FUNC_MAIN_ID') and ctx.FUNC_MAIN_ID():
            name = ctx.FUNC_MAIN_ID().getText()

        params, param_types = [], []
        if hasattr(ctx, 'param_list') and ctx.param_list():
            p_list = ctx.param_list()
            if callable(p_list): p_list = p_list()
            for p in p_list.param():
                param_types.append(p.getChild(0).getText().strip())
                params.append(p.getChild(p.getChildCount()-1).getText().strip())

        stmts = []
        body_node = None
        if hasattr(ctx, 'func_body'): body_node = ctx.func_body()
        if body_node:
            if callable(body_node): body_node = body_node()
            if isinstance(body_node, list): body_node = body_node[0]
            for s in body_node.statement():
                node = self.visit(s)
                if node: stmts.append(node)

        return self._with_pos(Func(
            name=name, params=params, param_types=param_types, 
            body=stmts, ret_type=ret_type,
            is_template=is_template,
            template_params=template_params
        ), ctx)

    def visitFunc_decl(self, ctx):
        
        all_ids = ctx.ID()
        
        if ctx.BASE_TYPE():
            ret_type = ctx.BASE_TYPE().getText()
        else:
            ret_type = all_ids[0].getText()

        name = all_ids[-1].getText()

        params, param_types = [], []
        if ctx.param_list():
            for p in ctx.param_list().param():
                p_all_ids = p.ID()
                p_name = p_all_ids[-1].getText()
                
                if p.BASE_TYPE():
                    p_type = p.BASE_TYPE().getText()
                else:
                    p_type = p_all_ids[0].getText()
                
                param_types.append(p_type)
                params.append(p_name)

        stmts = []
        if ctx.func_body():
            for s in ctx.func_body().statement():
                node = self.visit(s)
                if node: stmts.append(node)

        return self._with_pos(Func(
            name=name, params=params, param_types=param_types, 
            body=stmts, ret_type=ret_type,
            is_template=False,
            template_params=[]
        ), ctx)
    
    def visitFunc_main(self, ctx):
        ret_type = ctx.BASE_TYPE().getText()
        name = ctx.FUNC_MAIN_ID().getText()

        params, param_types = [], []
        if ctx.param_list():
            for p in ctx.param_list().param():
                p_all_ids = p.ID()
                p_name = p_all_ids[-1].getText()
                p_type = ctx.BASE_TYPE().getText() if p.BASE_TYPE() else p_all_ids[0].getText()
                param_types.append(p_type)
                params.append(p_name)

        stmts = []
        if ctx.func_body():
            for s in ctx.func_body().statement():
                node = self.visit(s)
                if node: stmts.append(node)

        return self._with_pos(Func(
            name=name, params=params, param_types=param_types, 
            body=stmts, ret_type=ret_type
        ), ctx)

    def visitVar_decl(self, ctx):
        if ctx.var_init():
            return self.visit(ctx.var_init())
        return None
    
    def visitVar_init(self, ctx):
        all_ids = ctx.ID()
        
        if ctx.BASE_TYPE():
            var_type = ctx.BASE_TYPE().getText()
            name = all_ids[0].getText()
        else:
            var_type = all_ids[0].getText()
            name = all_ids[1].getText()

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
        cond = self.visit(ctx.expr())
        
        then_body = []
        if ctx.func_body():
            for s in ctx.func_body(0).statement():
                node = self.visit(s)
                if node: then_body.append(node)
        
        else_body = None
        
        if ctx.if_statement():
            else_body = [self.visit(ctx.if_statement())]
            
        elif len(ctx.func_body()) > 1:
            else_body = []
            for s in ctx.func_body(1).statement():
                node = self.visit(s)
                if node: else_body.append(node)
                    
        return self._with_pos(IfStmt(cond=cond, then_body=then_body, else_body=else_body), ctx)

    def visitFunc_call(self, ctx):
        name = ctx.ID().getText()
        
        template_args = []
        if ctx.template_arg_list():
            for arg in ctx.template_arg_list().template_arg():
                template_args.append(arg.getText())

        args = []
        if ctx.expr():
            e_nodes = ctx.expr() if isinstance(ctx.expr(), list) else [ctx.expr()]
            args = [self.visit(e) for e in e_nodes]

        node = FuncCall(name=name, args=args)
        node.template_args = template_args
        return self._with_pos(node, ctx)
    
    def visitInput_expr(self, ctx):
        prompt_text = ""
        if ctx.STRING():
            prompt_text = ctx.STRING().getText()[1:-1]
        
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
        init = None
        if ctx.var_init():
            init = self.visit(ctx.var_init())
        elif ctx.expr():
            init = self.visit(ctx.expr(0))

        expr_count = len(ctx.expr())
        current_expr_idx = 0
        if not ctx.var_init() and expr_count > 0:
            current_expr_idx = 1
        
        cond = self.visit(ctx.expr(current_expr_idx)) if current_expr_idx < expr_count else None
        step = self.visit(ctx.expr(current_expr_idx + 1)) if (current_expr_idx + 1) < expr_count else None

        body = []
        if ctx.func_body():
            for s in ctx.func_body().statement():
                node = self.visit(s)
                if node: body.append(node)
        return self._with_pos(ForStmt(init=init, cond=cond, step=step, body=body), ctx)
    
    def visitIntegral_expr(self, ctx):
        
        body = self.visit(ctx.expr())
        
        ids = ctx.ID()
        start_id = ids[0].getText() if len(ids) > 0 else "a"
        end_id = ids[1].getText() if len(ids) > 1 else "b"
        
        var_name = "x" 
        
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
        exprs = ctx.expr()
        return self._with_pos(SolveLUExpr(
            matrix=self.visit(exprs[0]), 
            vector=self.visit(exprs[1])
        ), ctx)
    
    def visitDerivative_expr(self, ctx):
        body = self.visit(ctx.expr())
        var_name = ctx.ID().getText()
        return self._with_pos(DerivativeExpr(body=body, var=var_name), ctx)
    
    def visitArray_access(self, ctx):
        name = ctx.ID().getText()
        index = self.visit(ctx.expr())
        return self._with_pos(ArrayAccess(name=name, expr=index), ctx)
    
