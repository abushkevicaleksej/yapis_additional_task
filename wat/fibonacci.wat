(module
  (import "env" "out_i32" (func $out_i32 (param i32)))
  (import "env" "out_f32" (func $out_f32 (param f32)))
  (import "env" "out_str" (func $out_str (param i32)))
  (import "env" "in_i32" (func $in_i32 (param i32) (result i32)))
  (import "env" "pow_f32" (func $pow_f32 (param f32 f32) (result f32)))
  (memory (export "memory") 1)
  (data (i32.const 0) "Enter number to calculate fibonacci value...\00")
  (func $CalculateFibonacci (param $n i32) (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    (local $expression i32)
    local.get $n
    i32.const 0
    i32.le_s
    if
    i32.const 0
    return
    else
    local.get $n
    i32.const 1
    i32.eq
    if
    i32.const 1
    return
    else
    local.get $n
    i32.const 1
    i32.sub
    call $CalculateFibonacci
    local.get $n
    i32.const 2
    i32.sub
    call $CalculateFibonacci
    i32.add
    local.set $expression
    local.get $expression
    return
    end
    end
    i32.const 0
  )
  (export "CalculateFibonacci" (func $CalculateFibonacci))
  (func $Main  (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    (local $in_value i32)
    (local $out_result i32)
    i32.const 0
    call $in_i32
    local.set $in_value
    local.get $in_value
    call $CalculateFibonacci
    local.set $out_result
    local.get $out_result
    call $out_i32
    i32.const 0
    drop
    i32.const 0
    return
    i32.const 0
  )
  (export "Main" (func $Main))
)