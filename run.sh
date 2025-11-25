set -e

if [ $# -ne 1 ]; then
  echo "Usage: $0 path/to/test.expr"
  exit 1
fi

TEST_EXPR="$1"

python parser_runner.py "$TEST_EXPR"

./wabt-1.0.39/bin/wat2wasm module.wat -o module.wasm

node runtime.js module.wasm Main
