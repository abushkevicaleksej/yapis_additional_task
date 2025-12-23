from dataclasses import dataclass, field
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
    GENERIC = auto() 

@dataclass
class Type:
    kind: TypeKind
    name: str = "" 
    return_type: Optional['Type'] = None
    param_types: List['Type'] = field(default_factory=list)
    template_params: List[str] = field(default_factory=list)

    def __str__(self):
        if self.kind == TypeKind.GENERIC:
            return self.name # Выведет "T" или "Type"
        return self.kind.name.lower()

class TypeChecker:
    def get_type(self, type_name: str) -> Type:
        tn = type_name.strip()
        mapping = {
            'int': TypeKind.INT,
            'float': TypeKind.FLOAT,
            'char': TypeKind.CHAR,
            'string': TypeKind.STRING,
            'void': TypeKind.VOID
        }
        if tn in mapping:
            return Type(mapping[tn], name=tn)
        
        # Если это не базовый тип, возвращаем GENERIC тип с этим именем (например, "T")
        return Type(TypeKind.GENERIC, name=tn)

    def is_numeric(self, t: Type) -> bool:
        return t.kind in [TypeKind.INT, TypeKind.FLOAT]

    def can_assign(self, target: Type, source: Type) -> bool:
        # Самое важное: если мы сравниваем GENERIC с чем-то другим, они НЕ равны
        if target.kind == TypeKind.GENERIC or source.kind == TypeKind.GENERIC:
            return target.kind == source.kind and target.name == source.name
        
        if target.kind == source.kind: return True
        if target.kind == TypeKind.FLOAT and source.kind == TypeKind.INT: return True
        return False

    def get_common_type(self, t1: Type, t2: Type) -> Optional[Type]:
        if t1.kind == TypeKind.FLOAT or t2.kind == TypeKind.FLOAT:
            return Type(TypeKind.FLOAT)
        return Type(TypeKind.INT)