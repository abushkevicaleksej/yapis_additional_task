const fs = require('fs');

if (process.argv.length < 3) {
    console.log("Usage: node runtime.js <wasm-file> [function-name]");
    process.exit(1);
}

const wasmPath = process.argv[2];
const funcName = process.argv[3] || 'Main';
const wasmBuffer = fs.readFileSync(wasmPath);

const importObject = {
    env: {
        out_i32: (value) => {
            console.log(`[OUT INT]: ${value}`);
        },
        // Добавлена поддержка вывода float
        out_f32: (value) => {
            console.log(`[OUT FLOAT]: ${value}`);
        },
        in_i32: () => {
            process.stdout.write("[IN] Enter a number: ");
            const buffer = Buffer.alloc(100);
            try {
                const bytesRead = fs.readSync(0, buffer, 0, 100, null);
                if (bytesRead === 0) return 0;
                const str = buffer.toString('utf8', 0, bytesRead).trim();
                const num = parseInt(str, 10);
                if (isNaN(num)) return 0;
                return num;
            } catch (e) {
                return 0;
            }
        }
    }
};

(async () => {
    try {
        const wasmModule = await WebAssembly.instantiate(wasmBuffer, importObject);
        const exports = wasmModule.instance.exports;

        if (exports[funcName]) {
            console.log(`Running '${funcName}'...`);
            const result = exports[funcName]();
            console.log(`Result: ${result}`);
        } else {
            console.error(`Error: Function '${funcName}' not found.`);
        }
    } catch (err) {
        console.error("Runtime error:", err);
    }
})();