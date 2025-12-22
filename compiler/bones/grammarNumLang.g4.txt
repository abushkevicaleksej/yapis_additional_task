grammar grammarNumLang;

// Лексер
WS: [ \t\r\n]+ -> skip;
BASE_TYPE: 'int' | 'float' | 'char' | 'string' | 'void';
FUNCTION: 'function';
FUNC_MAIN_ID: 'Main';
LFIG_BR: '{';
RFIG_BR: '}';
INT: [0-9]+;
FLOAT: [0-9]+ '.' [0-9]+;
CHAR: '\'' ~['] '\'';
STRING: '"' ~["]* '"';
ID: [a-zA-Z_][a-zA-Z_0-9]*;

// Правила парсера
prog: (func_decl | func_main | template_decl)* EOF;
template_decl: 'template' '<' template_param_list '>' func_decl;
template_param_list: template_param (',' template_param)*;
template_param: 'type' ID;
func_decl: (BASE_TYPE | ID) FUNCTION ID '(' param_list? ')' LFIG_BR func_body RFIG_BR;
func_main: BASE_TYPE FUNCTION FUNC_MAIN_ID '(' param_list? ')' LFIG_BR func_body RFIG_BR;
param_list: param (',' param)*;
param: BASE_TYPE ID | ID '[' ']' ID | ID ID;
func_body: statement*;
statement: expr_statement | if_statement | for_statement | while_statement | break_statement | continue_statement | var_decl | return_statement | ';';
expr_statement: expr ';';
if_statement: 'if' expr 'then' LFIG_BR func_body RFIG_BR ('else' (if_statement | LFIG_BR func_body RFIG_BR))?;
for_statement: 'for' '(' (var_decl | expr)? ';' expr? ';' expr? ')' LFIG_BR func_body RFIG_BR;
while_statement: 'while' expr LFIG_BR func_body RFIG_BR;
break_statement: 'break' ';';
continue_statement: 'continue' ';';
var_decl: BASE_TYPE ID ('=' expr)? ';' | ID ID ('=' expr)? ';';
return_statement: 'return' expr ';';

// Иерархия выражений с приоритетом
expr: assignment_expr;
assignment_expr: logic_expr ('=' assignment_expr)?;
logic_expr: comparison_expr (('&&' | '||') comparison_expr)*;
comparison_expr: additive_expr (('>' | '<' | '<=' | '==' | '>=' | '!=') additive_expr)*;
additive_expr: multiplicative_expr (('+' | '-') multiplicative_expr)*;
multiplicative_expr: unary_expr (('*' | '/' | '^') unary_expr)*;
unary_expr: ('!' | '+' | '-') unary_expr | primary_expr;
primary_expr: INT | FLOAT | ID | STRING | CHAR | vector | '(' expr ')' | func_call | array_access | special_expr;
special_expr: cast_expr | sum_expr | integral_expr | derivative_expr | input_expr | output_expr | solveLU_expr;
cast_expr: '(' (BASE_TYPE | ID) ')' expr;
sum_expr: 'sum' '(' ID ',' ID ',' expr ')';
integral_expr: 'integral' '(' expr ',' ID ',' ID ')';
derivative_expr: 'derivative' '(' expr ',' ID ')';
input_expr: 'in' '(' STRING ')';
output_expr: 'out' '(' expr ')';
solveLU_expr: 'solveLU' '(' matrix ',' vector ')';
func_call: ID '(' (expr (',' expr)*)? ')' | ID '<' template_arg_list '>' '(' (expr (',' expr)*)? ')';
template_arg_list: template_arg (',' template_arg)*;
template_arg: BASE_TYPE | ID;
array_access: ID '[' expr ']';
matrix: '[' row (',' row)* ']';
row: '[' expr (',' expr)* ']';
vector: '[' expr (',' expr)* ']';