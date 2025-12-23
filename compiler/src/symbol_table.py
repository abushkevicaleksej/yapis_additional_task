import enum
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from compiler.src.type_system import ErrorType
from compiler.src.ast_nodes import Func, VarDecl

class Scope:
    def __init__(self, name: str, parent: Optional['Scope'] = None):
        self.name = name
        self.parent = parent
        self.symbols: Dict[str, 'Symbol'] = {}
        self.children: List['Scope'] = []
    
    def add_symbol(self, symbol: 'Symbol'):
        if symbol.name in self.symbols:
            raise ValueError(f"Symbol '{symbol.name}' already defined in scope '{self.name}'")
        self.symbols[symbol.name] = symbol
    
    def lookup(self, name: str, current_only: bool = False) -> Optional['Symbol']:
        if name in self.symbols:
            return self.symbols[name]
        
        if not current_only and self.parent:
            return self.parent.lookup(name)
        
        return None
    
    def add_child(self, child: 'Scope'):
        self.children.append(child)

class SymbolKind(enum.Enum):
    VARIABLE = "variable"
    FUNCTION = "function"
    PARAMETER = "parameter"
    TEMPLATE = "template"
    TYPE = "type"

@dataclass
class Symbol:
    name: str
    kind: SymbolKind
    type: any
    node: Optional[Union[VarDecl, Func]] = None
    scope: Optional[Scope] = None
    is_initialized: bool = False
    is_used: bool = False

class SymbolTable:
    def __init__(self):
        self.global_scope = Scope("global")
        self.current_scope = self.global_scope
        self.scope_stack: List[Scope] = [self.global_scope]
    
    def enter_scope(self, name: str):
        new_scope = Scope(name, self.current_scope)
        self.current_scope.add_child(new_scope)
        self.current_scope = new_scope
        self.scope_stack.append(new_scope)
    
    def exit_scope(self):
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()
            self.current_scope = self.scope_stack[-1]
    
    def add_symbol(self, symbol: Symbol):
        symbol.scope = self.current_scope
        self.current_scope.add_symbol(symbol)
    
    def lookup(self, name: str) -> Optional[Symbol]:
        return self.current_scope.lookup(name)
    
    def lookup_global(self, name: str) -> Optional[Symbol]:
        return self.global_scope.lookup(name)
    
    def get_current_function(self) -> Optional[Symbol]:
        for scope in reversed(self.scope_stack):
            for symbol in scope.symbols.values():
                if symbol.kind == SymbolKind.FUNCTION:
                    return symbol
        return None