(module
  (import "env" "out_i32" (func $out_i32 (param i32)))
  (import "env" "out_f32" (func $out_f32 (param f32)))
  (import "env" "out_str" (func $out_str (param i32)))
  (import "env" "in_i32" (func $in_i32 (param i32) (result i32)))
  (import "env" "pow_f32" (func $pow_f32 (param f32 f32) (result f32)))
  (memory (export "memory") 1)
  (data (i32.const 0) "Is 75 in 0..100?\00")
  (data (i32.const 17) "Good Morning\00")
  (data (i32.const 30) "Good Evening\00")
  (data (i32.const 43) "Greeting selection:\00")
  (func $IsInRange_int (param $val i32) (param $min i32) (param $max i32) (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    local.get $val
    local.get $min
    i32.add
    local.get $val
    local.get $max
    i32.add
    i32.add
    if
    i32.const 1
    return
    else
    i32.const 0
    return
    end
    i32.const 0
  )
  (export "IsInRange_int" (func $IsInRange_int))
  (func $Select_string (param $condition i32) (param $first i32) (param $second i32) (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    local.get $condition
    i32.const 1
    i32.eq
    if
    local.get $first
    return
    else
    local.get $second
    return
    end
    i32.const 0
  )
  (export "Select_string" (func $Select_string))
  (func $Main  (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    (local $score i32)
    (local $morning i32)
    (local $evening i32)
    (local $hour i32)
    (local $result i32)
    i32.const 75
    local.set $score
    i32.const 0
    call $out_str
i32.const 0
    drop
    local.get $score
    i32.const 0
    i32.const 100
    call $IsInRange_int
    call $out_i32
i32.const 0
    drop
    i32.const 17
    local.set $morning
    i32.const 30
    local.set $evening
    i32.const 20
    local.set $hour
    i32.const 43
    call $out_str
i32.const 0
    drop
    local.get $hour
    i32.const 12
    i32.gt_s
    local.get $evening
    local.get $morning
    call $Select_string
    local.set $result
    local.get $result
    call $out_str
i32.const 0
    drop
    i32.const 0
    return
    i32.const 0
  )
  (export "Main" (func $Main))
)