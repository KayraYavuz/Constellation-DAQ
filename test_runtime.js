const fs = require('fs');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;
const html = fs.readFileSync('bl4s_event_explorer.html', 'utf8');
const dom = new JSDOM(html, { runScripts: "dangerously", resources: "usable" });
dom.window.onerror = function(msg, url, lineNo, columnNo, error) {
    console.error('JSDOM Error:', msg, lineNo, columnNo, error);
};
setTimeout(() => {
    console.log("JSDOM initialization complete. checking window errors.");
}, 2000);
