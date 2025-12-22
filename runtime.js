const fs = require('fs');

if (process.argv.length < 3) {
    console.log("Usage: node runtime.js <wasm-file>");
    process.exit(1);
}

const wasmBuffer = fs.readFileSync(process.argv[2]);

const importObject = {
    env: {
        out_i32: (value) => console.log(`[OUT INT]: ${value}`),
        out_f32: (value) => console.log(`[OUT FLOAT]: ${value.toFixed(4)}`),
        in_i32: () => {
            // Синхронный ввод подсказки в stderr (чтобы не буферизировалось)
            process.stderr.write("[INPUT]: ");
            
            // Читаем до переноса строки
            let input = "";
            const buffer = Buffer.alloc(1);
            while (true) {
                try {
                    const bytesRead = fs.readSync(0, buffer, 0, 1);
                    if (bytesRead === 0 || buffer[0] === 10) break; // 10 = \n
                    input += buffer.toString();
                } catch (e) { break; }
            }
            const num = parseInt(input.trim(), 10);
            return isNaN(num) ? 0 : num;
        }
    }
};

(async () => {
    try {
        const wasmModule = await WebAssembly.instantiate(wasmBuffer, importObject);
        const exports = wasmModule.instance.exports;
        const mainFunc = exports.Main || exports.main;
        if (mainFunc) {
            const result = mainFunc();
            console.log(`Program finished with result: ${result}`);
        }
    } catch (err) {
        console.error("Runtime Error:", err);
    }
})();