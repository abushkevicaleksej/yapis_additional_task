(module
  (import "env" "out_i32" (func $out_i32 (param i32)))
  (import "env" "out_f32" (func $out_f32 (param f32)))
  (import "env" "out_str" (func $out_str (param i32)))
  (import "env" "in_i32" (func $in_i32 (param i32) (result i32)))
  (import "env" "pow_f32" (func $pow_f32 (param f32 f32) (result f32)))
  (memory (export "memory") 1)
  (data (i32.const 0) "Square int 10:\00")
  (data (i32.const 15) "Square float 1.5:\00")
  (data (i32.const 33) "Average int 10, 20:\00")
  (data (i32.const 53) "Average float 1.5, 4.5:\00")
  (func $Square_int (param $x i32) (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    local.get $x
    local.get $x
    i32.mul
    return
    i32.const 0
  )
  (export "Square_int" (func $Square_int))
  (func $Square_float (param $x f32) (result f32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    local.get $x
    local.get $x
    f32.mul
    return
    f32.const 0.0
  )
  (export "Square_float" (func $Square_float))
  (func $Average_int (param $a i32) (param $b i32) (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    local.get $a
    local.get $b
    i32.add
    i32.const 2
    i32.div_s
    return
    i32.const 0
  )
  (export "Average_int" (func $Average_int))
  (func $Average_float (param $a f32) (param $b f32) (result f32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    local.get $a
    local.get $b
    f32.add
    i32.const 2
    f32.convert_i32_s
    f32.div
    return
    f32.const 0.0
  )
  (export "Average_float" (func $Average_float))
  (func $Main  (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    (local $i1 i32)
    (local $i2 i32)
    (local $f1 f32)
    (local $f2 f32)
    i32.const 10
    local.set $i1
    i32.const 20
    local.set $i2
    f32.const 1.5
    local.set $f1
    f32.const 4.5
    local.set $f2
    i32.const 0
    call $out_str
i32.const 0
    drop
    local.get $i1
    call $Square_int
    call $out_i32
i32.const 0
    drop
    i32.const 15
    call $out_str
i32.const 0
    drop
    local.get $f1
    call $Square_float
    call $out_f32
i32.const 0
    drop
    i32.const 33
    call $out_str
i32.const 0
    drop
    local.get $i1
    local.get $i2
    call $Average_int
    call $out_i32
i32.const 0
    drop
    i32.const 53
    call $out_str
i32.const 0
    drop
    local.get $f1
    local.get $f2
    call $Average_float
    call $out_f32
i32.const 0
    drop
    i32.const 0
    return
    i32.const 0
  )
  (export "Main" (func $Main))
)