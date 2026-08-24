const fs = require('fs');
const code = fs.readFileSync('temp_clean.js', 'utf8');
let openBraces = 0, openParen = 0, openBracket = 0;
let inString = false, stringChar = null, inComment = false, inLineComment = false;
let lastLines = [];

for (let i = 0; i < code.length; i++) {
    const char = code[i];
    const nextChar = code[i+1];
    
    if (char === '\n') {
        if (inLineComment) inLineComment = false;
        lastLines.push(i);
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
        if (char === '\\') { i++; continue; } // skip escaped char
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
    
    if (char === '{') openBraces++;
    if (char === '}') openBraces--;
    if (char === '(') openParen++;
    if (char === ')') openParen--;
    if (char === '[') openBracket++;
    if (char === ']') openBracket--;
}
console.log(`Braces: ${openBraces}, Parens: ${openParen}, Brackets: ${openBracket}`);
console.log(`In string: ${inString}, stringChar: ${stringChar}`);
