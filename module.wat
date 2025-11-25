(module
  (import "env" "out_i32" (func $out_i32 (param i32)))
  (import "env" "out_f32" (func $out_f32 (param f32)))
  (import "env" "in_i32" (func $in_i32 (result i32)))
  (func $Main  (result i32)
    (local $a i32)
    (local $b f32)
    (local $squareA i32)
    (local $squareB f32)
    (local $cubicA i32)
    (local $pi f32)
    (local $piInt i32)
    (local $code i32)
    (local $character i32)
    (local $isAPositive i32)
    (local $defaultInt i32)
    (local $defaultFloat f32)
    (local $defaultChar i32)
    (local $x_val f32)
    (local $deriv_result f32)
    (local $testVec i32)
    (local $vecSum i32)
    (local $maxInt i32)
    (local $maxFloat f32)
    (local $minInt i32)
    (local $minFloat f32)
    (local $char1 i32)
    (local $char2 i32)
    (local $maxChar i32)
    i32.const 5
    local.set $a
    f32.const 2.5
    local.set $b
    local.get $a
    call $Square__int
    local.set $squareA
    local.get $b
    i32.trunc_f32_s
    call $Square__float
    local.set $squareB
    local.get $squareA
    call $out_i32
    i32.const 0
    drop
    local.get $squareB
    call $out_f32
    i32.const 0
    drop
    local.get $a
    call $Cubic__int
    local.set $cubicA
    local.get $cubicA
    call $out_i32
    i32.const 0
    drop
    f32.const 3.14
    local.set $pi
    local.get $pi
    i32.trunc_f32_s
    call $Convert__int_float
    local.set $piInt
    local.get $piInt
    call $out_i32
    i32.const 0
    drop
    i32.const 65
    local.set $code
    local.get $code
    call $Convert__char_int
    local.set $character
    local.get $character
    call $out_i32
    i32.const 0
    drop
    local.get $a
    call $IsPositive__int
    local.set $isAPositive
    local.get $isAPositive
    call $out_i32
    i32.const 0
    drop
    call $GetDefault__int
    local.set $defaultInt
    call $GetDefault__float
    local.set $defaultFloat
    call $GetDefault__char
    local.set $defaultChar
    local.get $defaultInt
    call $out_i32
    i32.const 0
    drop
    local.get $defaultFloat
    call $out_f32
    i32.const 0
    drop
    local.get $defaultChar
    call $out_i32
    i32.const 0
    drop
    f32.const 2.0
    local.set $x_val
    local.get $deriv_result
    call $out_f32
    i32.const 0
    drop
    i32.const 1
    i32.const 2
    i32.const 3
    call $CreateVector__int
    local.set $testVec
    local.get $testVec
    call $out_i32
    i32.const 0
    drop
    local.get $testVec
    call $VectorSum__int
    local.set $vecSum
    local.get $vecSum
    call $out_i32
    i32.const 0
    drop
    i32.const 10
    i32.const 20
    call $Max__int
    local.set $maxInt
    f32.const 3.14
    i32.trunc_f32_s
    f32.const 2.71
    i32.trunc_f32_s
    call $Max__float
    local.set $maxFloat
    local.get $maxInt
    call $out_i32
    i32.const 0
    drop
    local.get $maxFloat
    call $out_f32
    i32.const 0
    drop
    i32.const 10
    i32.const 20
    call $Min__int
    local.set $minInt
    f32.const 3.14
    i32.trunc_f32_s
    f32.const 2.71
    i32.trunc_f32_s
    call $Min__float
    local.set $minFloat
    local.get $minInt
    call $out_i32
    i32.const 0
    drop
    local.get $minFloat
    call $out_f32
    i32.const 0
    drop
    i32.const 65
    local.set $char1
    i32.const 90
    local.set $char2
    local.get $char1
    local.get $char2
    call $Max__char
    local.set $maxChar
    local.get $maxChar
    call $out_i32
    i32.const 0
    drop
    i32.const 0
    return
    i32.const 0
  )
  (export "Main" (func $Main))
  (func $Square__int (param $x i32) (result i32)
    local.get $x
    local.get $x
    i32.mul
    return
    i32.const 0
  )
  (export "Square__int" (func $Square__int))
  (func $Square__float (param $x f32) (result f32)
    local.get $x
    local.get $x
    f32.mul
    return
    f32.const 0.0
  )
  (export "Square__float" (func $Square__float))
  (func $Cubic__int (param $x i32) (result i32)
    local.get $x
    local.get $x
    i32.mul
    local.get $x
    i32.mul
    return
    i32.const 0
  )
  (export "Cubic__int" (func $Cubic__int))
  (func $Convert__int_float (param $value f32) (result i32)
    local.get $value
    i32.trunc_f32_s
    return
    i32.const 0
  )
  (export "Convert__int_float" (func $Convert__int_float))
  (func $Convert__char_int (param $value i32) (result i32)
    local.get $value
    return
    i32.const 0
  )
  (export "Convert__char_int" (func $Convert__char_int))
  (func $IsPositive__int (param $value i32) (result i32)
    local.get $value
    i32.const 0
    i32.gt_s
    if
    local.get $true
    return
    else
    local.get $false
    return
    end
    i32.const 0
  )
  (export "IsPositive__int" (func $IsPositive__int))
  (func $GetDefault__int  (result i32)
    (local $zero i32)
    i32.const 0
    local.set $zero
    local.get $zero
    return
    i32.const 0
  )
  (export "GetDefault__int" (func $GetDefault__int))
  (func $GetDefault__float  (result f32)
    (local $zero f32)
    i32.const 0
    f32.convert_i32_s
    local.set $zero
    local.get $zero
    return
    f32.const 0.0
  )
  (export "GetDefault__float" (func $GetDefault__float))
  (func $GetDefault__char  (result i32)
    (local $zero i32)
    i32.const 0
    local.set $zero
    local.get $zero
    return
    i32.const 0
  )
  (export "GetDefault__char" (func $GetDefault__char))
  (func $Max__int (param $a i32) (param $b i32) (result i32)
    local.get $a
    local.get $b
    i32.gt_s
    if
    local.get $a
    return
    else
    local.get $b
    return
    end
    i32.const 0
  )
  (export "Max__int" (func $Max__int))
  (func $Max__float (param $a f32) (param $b f32) (result f32)
    local.get $a
    local.get $b
    f32.gt
    if
    local.get $a
    return
    else
    local.get $b
    return
    end
    f32.const 0.0
  )
  (export "Max__float" (func $Max__float))
  (func $Min__int (param $a i32) (param $b i32) (result i32)
    local.get $a
    local.get $b
    i32.lt_s
    if
    local.get $a
    return
    else
    local.get $b
    return
    end
    i32.const 0
  )
  (export "Min__int" (func $Min__int))
  (func $Min__float (param $a f32) (param $b f32) (result f32)
    local.get $a
    local.get $b
    f32.lt
    if
    local.get $a
    return
    else
    local.get $b
    return
    end
    f32.const 0.0
  )
  (export "Min__float" (func $Min__float))
  (func $Max__char (param $a i32) (param $b i32) (result i32)
    local.get $a
    local.get $b
    i32.gt_s
    if
    local.get $a
    return
    else
    local.get $b
    return
    end
    i32.const 0
  )
  (export "Max__char" (func $Max__char))
)