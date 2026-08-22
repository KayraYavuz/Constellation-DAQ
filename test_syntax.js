const fs = require('fs');
const html = fs.readFileSync('bl4s_event_explorer.html', 'utf8');
const scriptRegex = /<script.*?>([\s\S]*?)<\/script>/gi;
let match;
let scripts = [];
while ((match = scriptRegex.exec(html)) !== null) {
    scripts.push(match[1]);
}
fs.writeFileSync('script_1.js', scripts.join('\n'));
try {
    require('child_process').execSync('node -c script_1.js');
    console.log("Syntax OK!");
} catch (e) {
    console.log("Syntax Error!");
    process.exit(1);
}
