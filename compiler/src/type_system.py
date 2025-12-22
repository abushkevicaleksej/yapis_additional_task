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