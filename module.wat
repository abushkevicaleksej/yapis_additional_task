(module
  (import "env" "out_i32" (func $out_i32 (param i32)))
  (import "env" "out_f32" (func $out_f32 (param f32)))
  (import "env" "in_i32" (func $in_i32 (result i32)))
  (func $calculateArea (param $a f32) (param $b f32) (param $c f32) (result f32)
    (local $s f32)
    (local $temp f32)
    (local $area f32)
    local.get $a
    local.get $b
    f32.add
    local.get $c
    f32.add
    f32.const 2.0
    f32.div
    local.set $s
    local.get $s
    local.get $s
    local.get $a
    f32.sub
    f32.mul
    local.get $s
    local.get $b
    f32.sub
    f32.mul
    local.get $s
    local.get $c
    f32.sub
    f32.mul
    local.set $temp
    local.get $temp
    f32.const 0.5
    drop
    f32.sqrt
    local.set $area
    local.get $area
    return
    f32.const 0.0
  )
  (export "calculateArea" (func $calculateArea))
  (func $Main  (result i32)
    (local $x i32)
    (local $y i32)
    (local $z i32)
    (local $result f32)
    i32.const 5
    local.set $x
    i32.const 6
    local.set $y
    i32.const 7
    local.set $z
    local.get $x
    f32.convert_i32_s
    local.get $y
    f32.convert_i32_s
    local.get $z
    f32.convert_i32_s
    call $calculateArea
    local.set $result
    local.get $result
    local.get $result
    f32.ne
    if
    i32.const 0
    call $out_i32
    i32.const 0
    drop
    else
    local.get $result
    call $out_f32
    i32.const 0
    drop
    end
    i32.const 0
    return
    i32.const 0
  )
  (export "Main" (func $Main))
)