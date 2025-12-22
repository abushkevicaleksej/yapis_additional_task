from dataclasses import dataclass
from typing import Optional
from enum import Enum

class ErrorType(Enum):
    SEMANTIC = "Semantic"
    SYNTAX = "Syntax"
    TYPE = "Type"
    NAME = "Name"
    SCOPE = "Scope"
    ARGUMENT = "Argument"
    RETURN = "Return"
    TEMPLATE = "Template"

@dataclass
class Error:
    type: ErrorType
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    context: Optional[str] = None
    
    def __str__(self):
        result = f"{self.type.value} Error"
        if self.line is not None:
            result += f" at line {self.line}"
            if self.column is not None:
                result += f":{self.column}"
        result += f": {self.message}"
        if self.context:
            result += f"\nContext: {self.context}"
        return result

class ErrorCollector:
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def add_error(self, error: Error):
        self.errors.append(error)
    
    def add_warning(self, error: Error):
        self.warnings.append(error)
    
    def has_errors(self):
        return len(self.errors) > 0
    
    def print_all(self):
        for error in self.errors:
            print(f"❌ {error}")
        for warning in self.warnings:
            print(f"⚠️  {warning}")
    
    def clear(self):
        self.errors.clear()
        self.warnings.clear()

from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TypeKind(Enum):
    INT = auto()
    FLOAT = auto()
    CHAR = auto()
    STRING = auto()
    VOID = auto()
    FUNCTION = auto()
    TEMPLATE = auto()

@dataclass
class Type:
    kind: TypeKind
    return_type: Optional['Type'] = None
    param_types: List['Type'] = None
    template_params: List[str] = None

    def __str__(self):
        return self.kind.name.lower()

class TypeChecker:
    def get_type(self, type_name: str) -> Type:
        mapping = {
            'int': TypeKind.INT,
            'float': TypeKind.FLOAT,
            'char': TypeKind.CHAR,
            'string': TypeKind.STRING,
            'void': TypeKind.VOID
        }
        kind = mapping.get(type_name, TypeKind.INT)
        return Type(kind)

    def is_numeric(self, t: Type) -> bool:
        return t.kind in [TypeKind.INT, TypeKind.FLOAT]

    def can_assign(self, target: Type, source: Type) -> bool:
        if target.kind == source.kind: return True
        if target.kind == TypeKind.FLOAT and source.kind == TypeKind.INT: return True
        return False

    def get_common_type(self, t1: Type, t2: Type) -> Optional[Type]:
        if t1.kind == TypeKind.FLOAT or t2.kind == TypeKind.FLOAT:
            return Type(TypeKind.FLOAT)
        return Type(TypeKind.INT)