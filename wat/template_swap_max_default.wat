(module
  (import "env" "out_i32" (func $out_i32 (param i32)))
  (import "env" "out_f32" (func $out_f32 (param f32)))
  (import "env" "out_str" (func $out_str (param i32)))
  (import "env" "in_i32" (func $in_i32 (param i32) (result i32)))
  (import "env" "pow_f32" (func $pow_f32 (param f32 f32) (result f32)))
  (memory (export "memory") 1)
  (data (i32.const 0) "Inside Swap:\00")
  (data (i32.const 13) "Swap\00")
  (data (i32.const 18) "maxVal\00")
  (data (i32.const 25) "Default int\00")
  (data (i32.const 37) "Default float\00")
  (data (i32.const 51) "A\00")
  (data (i32.const 53) "B\00")
  (data (i32.const 55) "Swap strings\00")
  (func $Swap_string (param $a i32) (param $b i32) 
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    (local $temp i32)
    local.get $a
    local.set $temp
    local.get $b
    local.tee $a
    drop
    local.get $temp
    local.tee $b
    drop
    i32.const 0
    call $out_str
i32.const 0
    drop
    local.get $a
    call $out_str
i32.const 0
    drop
    local.get $b
    call $out_str
i32.const 0
    drop
  )
  (export "Swap_string" (func $Swap_string))
  (func $Swap_int (param $a i32) (param $b i32) 
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    (local $temp i32)
    local.get $a
    local.set $temp
    local.get $b
    local.tee $a
    drop
    local.get $temp
    local.tee $b
    drop
    i32.const 0
    call $out_str
i32.const 0
    drop
    local.get $a
    call $out_i32
i32.const 0
    drop
    local.get $b
    call $out_i32
i32.const 0
    drop
  )
  (export "Swap_int" (func $Swap_int))
  (func $Max_string (param $a i32) (param $b i32) (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
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
  (export "Max_string" (func $Max_string))
  (func $Max_int (param $a i32) (param $b i32) (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
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
  (export "Max_int" (func $Max_int))
  (func $GetDefault_float  (result f32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    i32.const 0
    f32.convert_i32_s
    return
    f32.const 0.0
  )
  (export "GetDefault_float" (func $GetDefault_float))
  (func $GetDefault_int  (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    i32.const 0
    return
    i32.const 0
  )
  (export "GetDefault_int" (func $GetDefault_int))
  (func $Main  (result i32)
    (local $tmp_sq f32)
    (local $int_i i32)
    (local $int_h f32)
    (local $int_sum f32)
    (local $x_int_var f32)
    (local $x i32)
    (local $y i32)
    (local $maxVal i32)
    (local $defaultInt i32)
    (local $defaultFloat f32)
    (local $a i32)
    (local $b i32)
    (local $maxStr i32)
    i32.const 5
    local.set $x
    i32.const 10
    local.set $y
    i32.const 13
    call $out_str
i32.const 0
    drop
    local.get $x
    call $out_i32
i32.const 0
    drop
    local.get $y
    call $out_i32
i32.const 0
    drop
    local.get $x
    local.get $y
    call $Swap_int
    local.get $x
    call $out_i32
i32.const 0
    drop
    local.get $y
    call $out_i32
i32.const 0
    drop
    i32.const 18
    call $out_str
i32.const 0
    drop
    local.get $x
    local.get $y
    call $Max_int
    local.set $maxVal
    local.get $maxVal
    call $out_i32
i32.const 0
    drop
    call $GetDefault_int
    local.set $defaultInt
    call $GetDefault_float
    local.set $defaultFloat
    i32.const 25
    call $out_str
i32.const 0
    drop
    local.get $defaultInt
    call $out_i32
i32.const 0
    drop
    i32.const 37
    call $out_str
i32.const 0
    drop
    local.get $defaultFloat
    call $out_f32
i32.const 0
    drop
    i32.const 51
    local.set $a
    i32.const 53
    local.set $b
    i32.const 55
    call $out_str
i32.const 0
    drop
    local.get $a
    call $out_str
i32.const 0
    drop
    local.get $b
    call $out_str
i32.const 0
    drop
    local.get $a
    local.get $b
    call $Swap_string
    local.get $a
    call $out_str
i32.const 0
    drop
    local.get $b
    call $out_str
i32.const 0
    drop
    local.get $a
    local.get $b
    call $Max_string
    local.set $maxStr
    local.get $maxStr
    call $out_str
i32.const 0
    drop
    i32.const 0
    return
    i32.const 0
  )
  (export "Main" (func $Main))
)