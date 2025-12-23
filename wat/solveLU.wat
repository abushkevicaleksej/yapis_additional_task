(module
  (import "env" "out_i32" (func $out_i32 (param i32)))
  (import "env" "out_f32" (func $out_f32 (param f32)))
  (import "env" "out_str" (func $out_str (param i32)))
  (import "env" "in_i32" (func $in_i32 (param i32) (result i32)))
  (import "env" "pow_f32" (func $pow_f32 (param f32 f32) (result f32)))
  (memory (export "memory") 1)
  (data (i32.const 0) "Solution to linear system:\00")
  (data (i32.const 27) "x[\00")
  (data (i32.const 30) "] = \00")
  (data (i32.const 35) "Derivative at x=2: \00")
  (func $SolveLinearSystem  (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    (local $a i32)
    (local $b i32)
    (local $solution i32)
    local.get $a
    drop
    local.get $b
    drop
    i32.const 0
    local.set $solution
    local.get $solution
    return
    i32.const 0
  )
  (export "SolveLinearSystem" (func $SolveLinearSystem))
  (func $Main  (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    (local $x_vec i32)
    (local $i i32)
    (local $x f32)
    (local $deriv f32)
    call $SolveLinearSystem
    local.set $x_vec
    i32.const 0
    call $out_str
    i32.const 0
    drop
    i32.const 0
    local.set $i
    block
      loop
    local.get $i
    i32.const 6
    i32.lt_s
        i32.eqz
        br_if 1
    i32.const 27
    call $out_str
    i32.const 0
    drop
    local.get $i
    call $out_i32
    i32.const 0
    drop
    i32.const 30
    call $out_str
    i32.const 0
    drop
    local.get $x_vec
    local.get $i
    i32.const 4
    i32.mul
    i32.add
    f32.load
    call $out_f32
    i32.const 0
    drop
    local.get $i
    i32.const 1
    i32.add
    local.tee $i
    drop
        br 0
      end
    end
    f32.const 2.0
    local.set $x
    local.get $x
    local.set $tmp_sq
    local.get $tmp_sq
    f32.const 0.0001
    f32.add
    local.set $x
    local.get $x
    i32.const 3
    f32.convert_i32_s
    f32.add
    f32.const 2.0
    local.get $x
    f32.mul
    i32.const 2
    f32.convert_i32_s
    f32.add
    f32.add
    f32.const 5.0
    f32.sub
    local.get $tmp_sq
    f32.const 0.0001
    f32.sub
    local.set $x
    local.get $x
    i32.const 3
    f32.convert_i32_s
    f32.add
    f32.const 2.0
    local.get $x
    f32.mul
    i32.const 2
    f32.convert_i32_s
    f32.add
    f32.add
    f32.const 5.0
    f32.sub
    f32.sub
    f32.const 0.0002
    f32.div
    local.get $tmp_sq
    local.set $x
    local.set $deriv
    i32.const 35
    call $out_str
    i32.const 0
    drop
    local.get $deriv
    call $out_f32
    i32.const 0
    drop
    i32.const 0
    return
    i32.const 0
  )
  (export "Main" (func $Main))
)