from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class ASTNode:
    # Оставляем значения по умолчанию здесь
    line: int = 0
    column: int = 0

@dataclass
class Program(ASTNode):
    # Теперь и здесь обязано быть значение по умолчанию
    funcs: List['Func'] = field(default_factory=list)

@dataclass 
class Func(ASTNode):
    name: str = ""
    params: List[str] = field(default_factory=list)
    param_types: List[str] = field(default_factory=list)
    body: List['Stmt'] = field(default_factory=list)
    ret_type: Optional[str] = None
    is_template: bool = False
    template_params: Optional[List[str]] = None

@dataclass
class Stmt(ASTNode):
    pass

@dataclass
class VarDecl(Stmt):
    type: Optional[str] = None
    name: str = ""
    init: Optional['Expr'] = None

@dataclass 
class Return(Stmt):
    expr: Optional['Expr'] = None

@dataclass
class ExprStmt(Stmt):
    expr: Optional['Expr'] = None

@dataclass
class IfStmt(Stmt):
    cond: Optional['Expr'] = None
    then_body: List[Stmt] = field(default_factory=list)
    else_body: Optional[List[Stmt]] = None

@dataclass
class WhileStmt(Stmt):
    cond: Optional['Expr'] = None
    body: List[Stmt] = field(default_factory=list)

@dataclass
class ForStmt(Stmt):
    init: Optional[Stmt] = None
    cond: Optional['Expr'] = None
    step: Optional['Expr'] = None
    body: List[Stmt] = field(default_factory=list)

@dataclass
class Expr(ASTNode):
    pass

@dataclass
class IntConst(Expr):
    value: int = 0

@dataclass
class FloatConst(Expr):
    value: float = 0.0

@dataclass
class StringConst(Expr):
    value: str = ""

@dataclass
class CharConst(Expr):
    value: str = ""

@dataclass
class VarRef(Expr):
    name: str = ""

@dataclass
class BinaryOp(Expr):
    op: str = ""
    left: Optional[Expr] = None
    right: Optional[Expr] = None

@dataclass
class UnaryOp(Expr):
    op: str = ""
    expr: Optional[Expr] = None

@dataclass
class FuncCall(Expr):
    name: str = ""
    args: List[Expr] = field(default_factory=list)
    template_args: Optional[List[str]] = None

@dataclass
class CastExpr(Expr):
    target_type: str = ""
    expr: Optional[Expr] = None

@dataclass
class IntegralExpr(Expr):
    body: Optional[Expr] = None
    var: str = ""
    start: Optional[Expr] = None
    end: Optional[Expr] = None