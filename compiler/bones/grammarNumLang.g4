grammar grammarNumLang;

// ==============================================
// ЛЕКСЕР
// ==============================================

WS              : [ \t\r\n]+ -> skip;            // Пропускаем пробелы, табы, переводы строк
BASE_TYPE       : 'int' | 'float' | 'char' | 'string' | 'void';
FUNCTION        : 'function';
FUNC_MAIN_ID    : 'Main';
LFIG_BR         : '{';
RFIG_BR         : '}';
INT             : [0-9]+;
FLOAT           : [0-9]+ '.' [0-9]+;
CHAR            : '\'' ~['] '\'';
STRING          : '"' ~["]* '"';
ID              : [a-zA-Z_][a-zA-Z_0-9]*;
COMMENT         : '//' ~[\r\n]* -> skip;         // Однострочные комментарии

// ==============================================
// ПАРСЕР
// ==============================================

// Главное правило программы
prog
    : (func_decl | func_main | template_decl)* EOF
    ;

// Объявление шаблона
template_decl
    : 'template' '<' template_param_list '>' func_decl
    ;

// Список параметров шаблона
template_param_list
    : template_param (',' template_param)*
    ;

// Параметр шаблона
template_param
    : 'type' ID
    ;

// Объявление функции
func_decl
    : (BASE_TYPE | ID) FUNCTION ID '(' param_list? ')' LFIG_BR func_body RFIG_BR
    ;

// Главная функция
func_main
    : BASE_TYPE FUNCTION FUNC_MAIN_ID '(' param_list? ')' LFIG_BR func_body RFIG_BR
    ;

// Список параметров функции
param_list
    : param (',' param)*
    ;

// Параметр функции
param
    : BASE_TYPE ID          // Обычный параметр
    | ID '[' ']' ID        // Массив как параметр
    | ID ID                // Параметр шаблонного типа
    ;

// Тело функции
func_body
    : statement*
    ;

// Оператор
statement
    : expr_statement
    | if_statement
    | for_statement
    | while_statement
    | break_statement
    | continue_statement
    | var_decl
    | return_statement
    | ';'                  // Пустой оператор
    ;

// Оператор выражения
expr_statement
    : expr ';'
    ;

// Условный оператор if
if_statement
    : 'if' expr 'then' LFIG_BR func_body RFIG_BR 
      ('else' (if_statement | LFIG_BR func_body RFIG_BR))?
    ;

// Цикл for
for_statement
    : 'for' '(' (var_init | expr)? ';' expr? ';' expr? ')' 
      LFIG_BR func_body RFIG_BR
    ;

// Цикл while
while_statement
    : 'while' expr LFIG_BR func_body RFIG_BR
    ;

// Оператор break
break_statement
    : 'break' ';'
    ;

// Оператор continue
continue_statement
    : 'continue' ';'
    ;

// Инициализация переменной
var_init
    : (BASE_TYPE | ID) ID ('=' expr)?
    ;

// Объявление переменной
var_decl
    : var_init ';'
    ;

// Оператор return
return_statement
    : 'return' expr ';'
    ;

// ==============================================
// ВЫРАЖЕНИЯ (с иерархией приоритетов)
// ==============================================

// Корневое правило выражений
expr
    : assignment_expr
    ;

// Присваивание (низший приоритет)
assignment_expr
    : logic_expr ('=' assignment_expr)?
    ;

// Логические операции
logic_expr
    : comparison_expr (('&&' | '||') comparison_expr)*
    ;

// Операции сравнения
comparison_expr
    : additive_expr (('>' | '<' | '<=' | '==' | '>=' | '!=') additive_expr)*
    ;

// Сложение и вычитание
additive_expr
    : multiplicative_expr (('+' | '-') multiplicative_expr)*
    ;

// Умножение, деление и степень
multiplicative_expr
    : unary_expr (('*' | '/' | '^') unary_expr)*
    ;

// Унарные операции
unary_expr
    : ('!' | '+' | '-') unary_expr
    | primary_expr
    ;

// Первичные выражения
primary_expr
    : INT
    | FLOAT
    | ID
    | STRING
    | CHAR
    | vector
    | '(' expr ')'
    | func_call
    | array_access
    | special_expr
    ;

// Специальные выражения
special_expr
    : cast_expr
    | sum_expr
    | integral_expr
    | derivative_expr
    | input_expr
    | output_expr
    | solveLU_expr
    ;

// Приведение типа
cast_expr
    : '(' (BASE_TYPE | ID) ')' expr
    ;

// Сумма (суммирование)
sum_expr
    : 'sum' '(' ID ',' ID ',' expr ')'
    ;

// Интеграл
integral_expr
    : 'integral' '(' expr ',' ID ',' ID ')'
    ;

// Производная
derivative_expr
    : 'derivative' '(' expr ',' ID ')'
    ;

// Ввод данных
input_expr
    : 'in' '(' STRING ')'
    ;

// Вывод данных
output_expr
    : 'out' '(' expr ')'
    ;

// Решение СЛАУ методом LU
solveLU_expr
    : 'solveLU' '(' expr ',' expr ')'
    ;

// Вызов функции
func_call
    : ID '(' (expr (',' expr)*)? ')'
    | ID '<' template_arg_list '>' '(' (expr (',' expr)*)? ')'
    ;

// Список аргументов шаблона
template_arg_list
    : template_arg (',' template_arg)*
    ;

// Аргумент шаблона
template_arg
    : BASE_TYPE
    | ID
    ;

// Доступ к элементу массива
array_access
    : ID '[' expr ']'
    ;

// Матрица
matrix
    : '[' row (',' row)* ']'
    ;

// Строка матрицы
row
    : '[' expr (',' expr)* ']'
    ;

// Вектор
vector
    : '[' expr (',' expr)* ']'
    ;