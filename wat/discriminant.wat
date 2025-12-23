(module
  (import "env" "out_i32" (func $out_i32 (param i32)))
  (import "env" "out_f32" (func $out_f32 (param f32)))
  (import "env" "out_str" (func $out_str (param i32)))
  (import "env" "in_i32" (func $in_i32 (param i32) (result i32)))
  (import "env" "pow_f32" (func $pow_f32 (param f32 f32) (result f32)))
  (memory (export "memory") 1)
  (data (i32.const 0) "in a\00")
  (data (i32.const 5) "in b\00")
  (data (i32.const 10) "in c\00")
  (data (i32.const 15) "No real roots for given equation\00")
  (func $getDiscriminant (param $a f32) (param $b f32) (param $c f32) (result f32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    (local $disc f32)
    local.get $b
    i32.const 2
    f32.convert_i32_s
    f32.add
    i32.const 4
    f32.convert_i32_s
    local.get $a
    f32.mul
    local.get $c
    f32.mul
    f32.sub
    local.tee $disc
    drop
    local.get $disc
    return
    f32.const 0.0
  )
  (export "getDiscriminant" (func $getDiscriminant))
  (func $Main  (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    (local $a f32)
    (local $b f32)
    (local $c f32)
    (local $disc f32)
    (local $root1 f32)
    (local $root2 f32)
    (local $root f32)
    i32.const 0
    call $in_i32
    f32.convert_i32_s
    local.tee $a
    drop
    i32.const 5
    call $in_i32
    f32.convert_i32_s
    local.tee $b
    drop
    i32.const 10
    call $in_i32
    f32.convert_i32_s
    local.tee $c
    drop
    local.get $a
    local.get $b
    local.get $c
    call $getDiscriminant
    local.tee $disc
    drop
    local.get $disc
    i32.const 0
    f32.convert_i32_s
    f32.gt
    if
    local.get $b
    local.get $disc
    f32.const 0.5
    f32.add
    f32.add
    i32.const 2
    f32.convert_i32_s
    local.get $a
    f32.mul
    f32.div
    local.tee $root1
    drop
    local.get $b
    local.get $disc
    f32.const 0.5
    f32.add
    f32.sub
    i32.const 2
    f32.convert_i32_s
    local.get $a
    f32.mul
    f32.div
    local.tee $root2
    drop
    local.get $root1
    call $out_f32
    i32.const 0
    drop
    local.get $root2
    call $out_f32
    i32.const 0
    drop
    else
    local.get $disc
    i32.const 0
    f32.convert_i32_s
    f32.eq
    if
    local.get $b
    i32.const 2
    f32.convert_i32_s
    local.get $a
    f32.mul
    f32.div
    local.tee $root
    drop
    local.get $root
    call $out_f32
    i32.const 0
    drop
    else
    i32.const 15
    call $out_str
    i32.const 0
    drop
    end
    end
    i32.const 0
    return
    i32.const 0
  )
  (export "Main" (func $Main))
)