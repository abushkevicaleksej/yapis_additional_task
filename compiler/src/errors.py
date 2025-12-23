# errors.py
from dataclasses import dataclass
from typing import Optional, List
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
    length: int = 1

    def format_with_context(self, source_lines: List[str]) -> str:
        msg = f"{self.type.value} Error at line {self.line}:{self.column + 1}: {self.message}"
        if self.line and 0 < self.line <= len(source_lines):
            line_text = source_lines[self.line - 1]
            clean_line = line_text.replace('\t', '    ')
            msg += f"\n    {clean_line}\n"
            
            tab_count = line_text[:self.column].count('\t')
            pointer_pos = self.column + (tab_count * 3) 
            msg += "    " + " " * pointer_pos + "^"
        return msg

class ErrorCollector:
    def __init__(self, source_code: str = ""):
        self.errors: List[Error] = []
        self.source_lines = source_code.splitlines()
    
    def add_error(self, error: Error):
        self.errors.append(error)
    
    def has_errors(self):
        return len(self.errors) > 0
    
    def print_all(self):
        for error in self.errors:
            print(f"❌ {error.format_with_context(self.source_lines)}")