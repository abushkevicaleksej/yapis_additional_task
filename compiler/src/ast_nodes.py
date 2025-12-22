from dataclasses import dataclass, field
from typing import List, Optional, Any

@dataclass
class Program:
    funcs: List['Func']

@dataclass 
class Func:
    name: str
    params: List[str]
    # Добавляем список типов параметров
    param_types: List[str] 
    body: List['Stmt']
    ret_type: Optional[str]
    is_template: bool = False
    template_params: List[str] = None

@dataclass
class Stmt:
    pass

@dataclass
class VarDecl:
    type: Optional[str]
    name: str
    init: Optional['Expr']

@dataclass 
class Return(Stmt):
    expr: Optional['Expr']

@dataclass
class ExprStmt(Stmt):
    expr: 'Expr'

@dataclass
class IfStmt(Stmt):
    cond: 'Expr'
    then_body: List[Stmt]
    else_body: Optional[List[Stmt]]

@dataclass
class WhileStmt(Stmt):
    cond: 'Expr'
    body: List[Stmt]

@dataclass
class ForStmt(Stmt):
    init: Optional[Stmt]
    cond: Optional['Expr']
    step: Optional['Expr']
    body: List[Stmt]

@dataclass
class Expr:
    pass

@dataclass
class IntConst(Expr):
    value: int

@dataclass
class FloatConst(Expr):
    value: float

@dataclass
class StringConst(Expr):
    value: str

@dataclass
class CharConst(Expr):
    value: str

@dataclass
class VarRef(Expr):
    name: str

@dataclass
class BinaryOp(Expr):
    op: str
    left: Expr
    right: Expr

@dataclass
class UnaryOp(Expr):
    op: str
    expr: Expr

@dataclass
class FuncCall(Expr):
    name: str
    args: List[Expr]
    template_args: Optional[List[str]] = None

@dataclass
class CastExpr(Expr):
    target_type: str
    expr: Expr