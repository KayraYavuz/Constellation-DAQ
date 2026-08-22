const fs = require('fs');
const jsdom = require("jsdom");
const { JSDOM } = jsdom;

const html = fs.readFileSync('bl4s_event_explorer.html', 'utf8');
const dom = new JSDOM(html, { runScripts: "dangerously" });

// Mock echarts to avoid errors
dom.window.echarts = {
    init: function() { return { setOption: function(){}, resize: function(){} }; }
};
dom.window.fetch = async () => ({ json: async () => ({}) });

try {
    dom.window.openPanel('dfp_panel', 'TDAQ System', 'DFP Panel & Network', 'dfp_panel', true);
    console.log("DFP Panel opened successfully. activePanels:", Object.keys(dom.window.activePanels));
} catch (e) {
    console.error("Error opening DFP Panel:", e);
}
