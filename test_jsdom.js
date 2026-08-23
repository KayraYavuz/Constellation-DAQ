const fs = require('fs');
const { JSDOM } = require('jsdom');
const html = fs.readFileSync('bl4s_event_explorer.html', 'utf8');

const dom = new JSDOM(html, {
  url: "file:///Users/kayrayavuz/Desktop/DATA/Constellation-DAQ-Git/bl4s_event_explorer.html",
  runScripts: "dangerously",
  resources: "usable"
});

dom.window.addEventListener('error', (event) => {
  console.error("JSDOM Error:", event.error);
});
console.log("JSDOM loaded successfully.");
