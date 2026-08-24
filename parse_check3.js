const fs = require('fs');
const code = fs.readFileSync('just_js.js', 'utf8');
let openBraces = [];
let inString = false, stringChar = null, inComment = false, inLineComment = false, inTemplateLiteral = false;
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
    
    if (inString || inTemplateLiteral) {
        if (char === '\\') { i++; continue; }
        if (inString && char === stringChar) {
            inString = false;
            stringChar = null;
        } else if (inTemplateLiteral && char === '`') {
            inTemplateLiteral = false;
        } else if (inTemplateLiteral && char === '$' && nextChar === '{') {
            // we ignore interpolation depth for this simple check, assume it's valid
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
    
    if (char === '"' || char === "'") {
        inString = true;
        stringChar = char;
        continue;
    }
    if (char === '`') {
        inTemplateLiteral = true;
        continue;
    }
    
    if (char === '{') openBraces.push(lineNum);
    if (char === '}') openBraces.pop();
}
console.log(`Unclosed braces at lines:`, openBraces);
console.log(`String state: inString=${inString}, inTemplate=${inTemplateLiteral}`);
