const fs = require('fs');

if (process.argv.length < 3) {
    console.log("Usage: node runtime.js <wasm-file>");
    process.exit(1);
}

const wasmBuffer = fs.readFileSync(process.argv[2]);

let wasmInstance;

const importObject = {
    env: {
        out_i32: (value) => console.log(`[OUT INT]: ${value}`),
        out_f32: (value) => console.log(`[OUT FLOAT]: ${value.toFixed(4)}`),
        pow_f32: (base, exp) => Math.pow(base, exp),
        
        out_str: (offset) => {
            const memory = wasmInstance.exports.memory;
            const view = new Uint8Array(memory.buffer, offset);
            let length = 0;
            while (view[length] !== 0 && offset + length < view.length) {
                length++;
            }
            const bytes = new Uint8Array(memory.buffer, offset, length);
            const str = new TextDecoder("utf-8").decode(bytes);
            console.log(`[OUT STR]: ${str}`);
        },
        
        in_i32: (offset) => {
            const memory = wasmInstance.exports.memory;
            const view = new Uint8Array(memory.buffer, offset);
            let length = 0;
            while (view[length] !== 0) length++;

            const bytes = new Uint8Array(memory.buffer, offset, length);
            const prompt = new TextDecoder("utf-8").decode(bytes);
            process.stdout.write(`${prompt}: `);

            const BUF_SIZE = 1024;
            const buffer = Buffer.alloc(BUF_SIZE);
            try {
                const bytesRead = fs.readSync(0, buffer, 0, BUF_SIZE);
                const input = buffer.toString('utf8', 0, bytesRead).trim();
                return parseInt(input, 10) || 0;
            } catch (e) {
                return 0;
            }
        },
    }
};

(async () => {
    const wasmModule = await WebAssembly.instantiate(wasmBuffer, importObject);
    wasmInstance = wasmModule.instance;
    
    const mainFunc = wasmInstance.exports.Main || wasmInstance.exports.main;
    if (mainFunc) mainFunc();
})();