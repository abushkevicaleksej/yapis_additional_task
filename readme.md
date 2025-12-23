
---

# Отчет по лабораторной работе 5: Язык программирования NumLang

_Свойства языка согласно варианту 1_:
1. Объявление переменных - явное;
2. Преобразование типов -  явное, например, a = (int) b;
3. Оператор присваивания - одноцелевой, например a = b;
4. Структуры, ограничивающие область видимости - подпрограммы;
5. Маркер блочного оператора - явные, например {} или begin end;
6. Условные операторы - двухвариантный оператор if-then-else;
7. Перегрузка подпрограмм - отсутствует;
8. Передача параметров в подпрограмму - только по значению и возвращаемому значению;
9. Допустимое место объявления подпрограмм - в начале программы;

_Варианты языков_:

Язык, описывающий математические вычисления:
1. Встроенные типы - int, float;
2. Операции: +, -, *, \, %, ^, ==, !=, <, >, <=, >=;
3. Встроенные функции log, ln, sin, cos, tan, asin, acos, atan.

_Вариант целевого кода_ -  WAT, текстовое представление WASM.

_Вариант усложнения_ - шаблоны.

## 1. Спецификация языка
**NumLang** — это статически типизированный язык программирования, ориентированный на численные методы и математические вычисления. Язык компилируется в текстовое представление WebAssembly (WAT).

**Ключевые особенности:**
*   **Математика:** Встроенные операторы для вычисления определенных интегралов, производных и решения систем линейных уравнений (LU-разложение).
*   **Система шаблонов (Templates):** Поддержка обобщенного программирования в стиле C++ с использованием мономорфизации (генерация отдельных копий функций для разных типов данных).
*   **Строгая типизация:** Автоматическое приведение типов (`int` -> `float`) и контроль типов на этапе компиляции.
*   **Взаимодействие с окружением:** Встроенные функции ввода-вывода через JavaScript-рантайм.

---

## 2. Общее описание проекта
Проект представляет собой полный цикл разработки компилятора. Архитектура состоит из следующих этапов:

1.  **Лексический и синтаксический анализ:** Реализован с помощью **ANTLR4**. Грамматика описывает иерархию выражений, приоритеты операций и структуру управляющих конструкций.
2.  **Построение AST:** Преобразование дерева парсинга в абстрактное синтаксическое дерево (Abstract Syntax Tree) с сохранением информации о позициях в коде для вывода ошибок.
3.  **Семантический анализ:** Проверка областей видимости, регистрация символов, проверка типов и подстановка шаблонных параметров.
4.  **Генерация кода (WATEmitter):** Трансляция AST в инструкции стековой машины WebAssembly. Реализована мономорфизация шаблонов и управление линейной памятью для строк и массивов.
5.  **Runtime:** Слой на JavaScript для исполнения скомпилированного `.wasm` модуля, обеспечивающий ввод/вывод и математические функции (например, возведение в степень).

---

## 3. Краткие сведения по синтаксису (из грамматики)

### Типы данных
*   `int`: 32-битное целое число.
*   `float`: 32-битное число с плавающей точкой.
*   `string`: Строковые литералы (хранятся в памяти как Null-terminated).
*   `void`: Отсутствие типа (для функций).
*   `char`: Символ.

### Управляющие конструкции
*   `if expr then { ... } else { ... }`: Условный оператор.
*   `while expr { ... }`: Цикл с предусловием.
*   `for (init; cond; step) { ... }`: Классический цикл.

### Некоторые специальные математические выражения
*   `integral(expr, var, start, end)`: Численное интегрирование методом средних прямоугольников.
*   `derivative(expr, var)`: Вычисление производной в текущей точке методом конечных разностей.
*   `solveLU(matrix, vector)`: Решение СЛАУ. 

### Шаблоны
```cpp
template <type T>
T function Max(T a, T b) {
    if a > b then { return a; } else { return b; }
}
```

---

## 4. Некоторые отлавливаемые ошибок и их классы

Система диагностики ошибок выводит сообщения с указанием строки, столбца и визуальным указателем на место ошибки.

| Класс ошибки | Описание |
| :--- | :--- |
| `Syntax Error` | Нарушение грамматических правил (незакрытые скобки, пропущенные `;`). |
| `Name Error` | Использование необъявленной переменной или функции. |
| `Type Error` | Несоответствие типов (например, попытка сложить `string` и `int` или передать `float` в `int` параметр без каста). |
| `Semantic Error` | Повторное объявление переменной в одной области видимости, отсутствие функции `Main`. |
| `Argument Error` | Неверное количество аргументов при вызове функции. |
| `Return Error` | Возврат значения, тип которого не совпадает с объявленным в заголовке функции. |
| `Template Error` | Ошибки при подстановке типов в шаблоны или неверное количество шаблонных аргументов. |

---

## 5. Дополнительные классы системы

1.  **`SymbolTable`**: Многоуровневая таблица символов для управления областями видимости (Scopes). Хранит информацию о переменных, функциях и шаблонах.
2.  **`TypeChecker`**: Компонент, отвечающий за логику совместимости типов и правила их приведения.
3.  **`ErrorCollector`**: Накопитель ошибок, позволяющий собрать все проблемы за один проход компиляции перед остановкой.
4.  **`WATEmitter`**: Компонент, реализующий:
    *   **Monomorphization**: механизм отслеживания специализаций шаблонов.
    *   **Stack Management**: контроль за тем, чтобы после каждого выражения стек WASM оставался в корректном состоянии.
    *   **String Pool**: сбор всех строковых литералов и размещение их в секции `data`.

---

## 6. Примеры работы
*С примерами, не описанными в этом подразделе, можно ознакомиться в examples/.... С WAT-представлением примеров можно ознакомиться в wat/...*

**Тест 1. Аппроксимация функции синуса и подсчет площади под графиком с помощью интеграла**
```
float function CalculateArea(float a, float b) {
    float area = integral(x^2, a, b); 
    return area;
}

float function ApproximateSin(float x) {
    float total = 0;
    int n = 5;
    for (int i = 0; i < n; i = i + 1) {
        float term = (-1)^i * x^(2*i+1);
        int factorial = 1;
        for (int j = 1; j <= 2*i+1; j = j + 1) {
            factorial = factorial * j;
        }
        total = total + term / factorial;
    }
    return total;
}

int function Main() {

    int a = in("in a ")
    int b = in("in b ")
    float area = CalculateArea(a, b);
    out("Area under x^2 from", a, " to ", b);
    out(area);
    
    float sinValue = ApproximateSin(3.14159 / 6);
    out("sin(pi/6) approximation: ");
    out(sinValue);
    
    return 0;
}
```

Результат работы
```
in a : 0
in b : 1
[OUT STR]: Area under x^2 from
[OUT FLOAT]: -0.3333
[OUT STR]: sin(pi/6) approximation:
[OUT FLOAT]: 0.5479
```

**Тест 2. Решение СЛАУ**
```
Vector function SolveLinearSystem() {
    Matrix a = [[2.0, 1.0], [1.0, -1.0]];
    Vector b = [5.0, 1.0];
    
    Vector solution = solveLU(a, b);
    return solution;
}

int function Main() {
    Vector x_vec = SolveLinearSystem();
    
    out("Solution to linear system:");
    
    for (int i = 0; i < 6; i = i + 1) {
        out("x[");
        out(i);
        out("] = ");
        out(x_vec[i]);
    }
    
    float x = 2.0; 
    float deriv = derivative(x^3 + 2.0 * x^2 - 5.0, x);
    
    out("Derivative at x=2: ");
    out(deriv);
    
    return 0;
}
```

Результат работы
```
[OUT STR]: Solution to linear system:
[OUT STR]: x[
[OUT INT]: 0
[OUT STR]: ] =
[OUT FLOAT]: 2.997167924847933e+32
[OUT STR]: x[
[OUT INT]: 1
[OUT STR]: ] =
[OUT FLOAT]: 1.8523600588218255e+28
[OUT STR]: x[
[OUT INT]: 2
[OUT STR]: ] =
[OUT FLOAT]: 0.0000
[OUT STR]: x[
[OUT INT]: 3
[OUT STR]: ] =
[OUT FLOAT]: 7.036674457942945e+22
[OUT STR]: x[
[OUT INT]: 4
[OUT STR]: ] =
[OUT FLOAT]: 1.271190455920643e+31
[OUT STR]: x[
[OUT INT]: 5
[OUT STR]: ] =
[OUT FLOAT]: 7.214921977234679e+22
[OUT STR]: Derivative at x=2:
[OUT FLOAT]: 27.9808
```

**Тест 3. Шаблон-селектор**
```
template <type T>
int function IsInRange(T val, T min, T max) {
    if val >= min && val <= max then {
        return 1;
    } else {
        return 0;
    }
}

template <type Data>
Data function Select(int condition, Data first, Data second) {
    if condition == 1 then {
        return first;
    } else {
        return second;
    }
}

int function Main() {
    int score = 75;
    out("Is 75 in 0..100?");
    out(IsInRange<int>(score, 0, 100));

    string morning = "Good Morning";
    string evening = "Good Evening";
    int hour = 20;

    out("Greeting selection:");
    string result = Select<string>(hour > 12, evening, morning);
    out(result);

    return 0;
}
```


Результат работы
```
[OUT STR]: Is 75 in 0..100?
[OUT INT]: 1
[OUT STR]: Greeting selection:
[OUT STR]: Good Evening
```

**Тест 4. Шаблон для подсчета квадрата числа и среднего двух чисел**
```
template <type T>
T function Square(T x) {
    return x * x;
}

template <type N>
N function Average(N a, N b) {
    return (a + b) / 2;
}

int function Main() {
    int i1 = 10;
    int i2 = 20;
    float f1 = 1.5;
    float f2 = 4.5;

    out("Square int 10:");
    out(Square<int>(i1));

    out("Square float 1.5:");
    out(Square<float>(f1));

    out("Average int 10, 20:");
    out(Average<int>(i1, i2));

    out("Average float 1.5, 4.5:");
    out(Average<float>(f1, f2));

    return 0;
}
```

Результат:
```
[OUT STR]: Square int 10:
[OUT INT]: 100
[OUT STR]: Square float 1.5:
[OUT FLOAT]: 2.2500
[OUT STR]: Average int 10, 20:
[OUT INT]: 15
[OUT STR]: Average float 1.5, 4.5:
[OUT FLOAT]: 3.0000
```

**Тест 5. Подсчет дискриминанта**
```
float function getDiscriminant(float a, float b, float c)
{
    float disc;
    disc = (b ^ 2) - 4 * a * c;
    return disc;
}

int function Main()
{
    float a;
    float b;
    float c;
    a = in("in a");
    b = in("in b");
    c = in("in c");

    float disc;
    disc = getDiscriminant(a, b, c);

    if disc > 0 then {
        float root1;
        float root2;
        root1 = (-b + (disc ^ 0.5))/(2 * a);
        root2 = (-b - (disc ^ 0.5))/(2 * a);
        out(root1);
        out(root2);
    } 
    else {
        if disc == 0 then {
            float root;
            root = -b / (2 * a);
            out(root);
        } 
        else {
            out("No real roots for given equation");
        }
    }
    return 0;
}
```

Результат работы
```
in a: 1
in b: 8
in c: 2
[OUT FLOAT]: 7.7417
[OUT FLOAT]: 0.2583
```

---

## 7. Инструкция по установке и запуску

### Требования
*   Python 3.10+
*   Node.js 16+
*   ANTLR4 Python Runtime: `pip install antlr4-python3-runtime` в ваше виртуальное окружение
*   Инструменты [wabt](https://github.com/WebAssembly/wabt) (для команды `wat2wasm`)

### Сборка и запуск
1.  **Генерация парсера (если менялась грамматика):**
    ```bash
    antlr4 -Dlanguage=Python3 grammarNumLang.g4 -visitor -o compiler/bones
    ```

2.  **Компиляция исходного кода (`.expr`) в WAT:**
    ```bash
    python parse_runner.py my_program.expr
    ```
    *Результат: файл `module.wat`*

3.  **Преобразование в бинарный WebAssembly:**
    ```bash
    wat2wasm module.wat -o module.wasm
    ```

4.  **Запуск через рантайм:**
    ```bash
    node runtime.js module.wasm
    ```

---