const fs = require('fs');
const code = fs.readFileSync('temp_clean.js', 'utf8');
let openBraces = [];
let inString = false, stringChar = null, inComment = false, inLineComment = false;
let lineNum = 1;

for (let i = 0; i < code.length; i++) {
    const char = code[i];
    const nextChar = code[i+1];
    
    if (char === '\n') {
        if (inLineComment) inLineComment = false;
        lineNum++;
        continue;
    }
    
    if (inLineComment) continue;
    
    if (inComment) {
        if (char === '*' && nextChar === '/') {
            inComment = false;
            i++;
        }
        continue;
    }
    
    if (inString) {
        if (char === '\\') { i++; continue; }
        if (char === stringChar) {
            inString = false;
            stringChar = null;
        }
        continue;
    }
    
    if (char === '/' && nextChar === '/') {
        inLineComment = true;
        i++;
        continue;
    }
    if (char === '/' && nextChar === '*') {
        inComment = true;
        i++;
        continue;
    }
    
    if (char === '"' || char === "'" || char === '`') {
        inString = true;
        stringChar = char;
        continue;
    }
    
    if (char === '{') openBraces.push(lineNum);
    if (char === '}') openBraces.pop();
}
console.log(`Unclosed braces at lines:`, openBraces);
