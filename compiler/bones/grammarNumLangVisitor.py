# Generated from bones/grammarNumLang.g4 by ANTLR 4.13.2
from antlr4 import *
if "." in __name__:
    from .grammarNumLangParser import grammarNumLangParser
else:
    from grammarNumLangParser import grammarNumLangParser

# This class defines a complete generic visitor for a parse tree produced by grammarNumLangParser.

class grammarNumLangVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by grammarNumLangParser#prog.
    def visitProg(self, ctx:grammarNumLangParser.ProgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#template_decl.
    def visitTemplate_decl(self, ctx:grammarNumLangParser.Template_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#template_param_list.
    def visitTemplate_param_list(self, ctx:grammarNumLangParser.Template_param_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#template_param.
    def visitTemplate_param(self, ctx:grammarNumLangParser.Template_paramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#func_decl.
    def visitFunc_decl(self, ctx:grammarNumLangParser.Func_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#func_main.
    def visitFunc_main(self, ctx:grammarNumLangParser.Func_mainContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#param_list.
    def visitParam_list(self, ctx:grammarNumLangParser.Param_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#param.
    def visitParam(self, ctx:grammarNumLangParser.ParamContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#func_body.
    def visitFunc_body(self, ctx:grammarNumLangParser.Func_bodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#statement.
    def visitStatement(self, ctx:grammarNumLangParser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#expr_statement.
    def visitExpr_statement(self, ctx:grammarNumLangParser.Expr_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#if_statement.
    def visitIf_statement(self, ctx:grammarNumLangParser.If_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#for_statement.
    def visitFor_statement(self, ctx:grammarNumLangParser.For_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#while_statement.
    def visitWhile_statement(self, ctx:grammarNumLangParser.While_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#break_statement.
    def visitBreak_statement(self, ctx:grammarNumLangParser.Break_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#continue_statement.
    def visitContinue_statement(self, ctx:grammarNumLangParser.Continue_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#var_decl.
    def visitVar_decl(self, ctx:grammarNumLangParser.Var_declContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#return_statement.
    def visitReturn_statement(self, ctx:grammarNumLangParser.Return_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#expr.
    def visitExpr(self, ctx:grammarNumLangParser.ExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#assignment_expr.
    def visitAssignment_expr(self, ctx:grammarNumLangParser.Assignment_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#logic_expr.
    def visitLogic_expr(self, ctx:grammarNumLangParser.Logic_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#comparison_expr.
    def visitComparison_expr(self, ctx:grammarNumLangParser.Comparison_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#additive_expr.
    def visitAdditive_expr(self, ctx:grammarNumLangParser.Additive_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#multiplicative_expr.
    def visitMultiplicative_expr(self, ctx:grammarNumLangParser.Multiplicative_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#unary_expr.
    def visitUnary_expr(self, ctx:grammarNumLangParser.Unary_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#primary_expr.
    def visitPrimary_expr(self, ctx:grammarNumLangParser.Primary_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#special_expr.
    def visitSpecial_expr(self, ctx:grammarNumLangParser.Special_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#cast_expr.
    def visitCast_expr(self, ctx:grammarNumLangParser.Cast_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#sum_expr.
    def visitSum_expr(self, ctx:grammarNumLangParser.Sum_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#integral_expr.
    def visitIntegral_expr(self, ctx:grammarNumLangParser.Integral_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#derivative_expr.
    def visitDerivative_expr(self, ctx:grammarNumLangParser.Derivative_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#input_expr.
    def visitInput_expr(self, ctx:grammarNumLangParser.Input_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#output_expr.
    def visitOutput_expr(self, ctx:grammarNumLangParser.Output_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#solveLU_expr.
    def visitSolveLU_expr(self, ctx:grammarNumLangParser.SolveLU_exprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#func_call.
    def visitFunc_call(self, ctx:grammarNumLangParser.Func_callContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#template_arg_list.
    def visitTemplate_arg_list(self, ctx:grammarNumLangParser.Template_arg_listContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#template_arg.
    def visitTemplate_arg(self, ctx:grammarNumLangParser.Template_argContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#array_access.
    def visitArray_access(self, ctx:grammarNumLangParser.Array_accessContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#matrix.
    def visitMatrix(self, ctx:grammarNumLangParser.MatrixContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#row.
    def visitRow(self, ctx:grammarNumLangParser.RowContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by grammarNumLangParser#vector.
    def visitVector(self, ctx:grammarNumLangParser.VectorContext):
        return self.visitChildren(ctx)



del grammarNumLangParser