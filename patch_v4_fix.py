with open("bl4s_event_explorer.html", "r") as f:
    html = f.read()

# Revert the multiple terminalIntervals
html = html.replace("""
// Live Event Feed Terminal Logic
let terminalInterval = null;
function generateTerminalLog() {
    const satellites = ['ML_RECON', 'PHYSICS', 'TRACKING', 'CALORIMETER'];
    const src = satellites[Math.floor(Math.random() * satellites.length)];
    const id = Math.floor(Math.random() * 999999);
    const size = (Math.random() * 5 + 0.5).toFixed(2);
    
    let color = '#38bdf8';
    if (src === 'ML_RECON') color = '#a855f7';
    if (src === 'PHYSICS') color = '#f59e0b';

    const now = new Date();
    const ts = now.toISOString().split('T')[1].slice(0, -1);
    
    return `<div class="terminal-line"><span class="term-ts">[${ts}]</span><span class="term-src" style="color:${color}">[${src}]</span><span class="term-msg">EventProcessed id=${id}</span> <span class="term-data">size=${size}kB</span></div>`;
}

setInterval(() => {
    // Find all active terminal windows
    const terminals = document.querySelectorAll('.terminal-container');
    terminals.forEach(term => {
        // Generate 3-8 logs per second (50-100 / 10 = ~5 logs per 100ms)
        for(let i=0; i<Math.floor(Math.random()*4)+1; i++) {
            term.insertAdjacentHTML('beforeend', generateTerminalLog());
        }
        // Auto-scroll to bottom
        term.scrollTop = term.scrollHeight;
        // Limit lines to prevent memory leak
        if (term.childElementCount > 150) {
            for(let i=0; i<20; i++) term.removeChild(term.firstChild);
        }
    });
}, 150);
""", "")

terminal_js = """
// Live Event Feed Terminal Logic
let terminalInterval = null;
function generateTerminalLog() {
    const satellites = ['ML_RECON', 'PHYSICS', 'TRACKING', 'CALORIMETER'];
    const src = satellites[Math.floor(Math.random() * satellites.length)];
    const id = Math.floor(Math.random() * 999999);
    const size = (Math.random() * 5 + 0.5).toFixed(2);
    
    let color = '#38bdf8';
    if (src === 'ML_RECON') color = '#a855f7';
    if (src === 'PHYSICS') color = '#f59e0b';

    const now = new Date();
    let ts = "";
    try { ts = now.toISOString().split('T')[1].slice(0, -1); } catch(e) {}
    
    return `<div class="terminal-line"><span class="term-ts">[${ts}]</span><span class="term-src" style="color:${color}">[${src}]</span><span class="term-msg">EventProcessed id=${id}</span> <span class="term-data">size=${size}kB</span></div>`;
}

setInterval(() => {
    // Find all active terminal windows
    const terminals = document.querySelectorAll('.terminal-container');
    terminals.forEach(term => {
        // Generate 3-8 logs per second
        for(let i=0; i<Math.floor(Math.random()*4)+1; i++) {
            term.insertAdjacentHTML('beforeend', generateTerminalLog());
        }
        // Auto-scroll to bottom
        term.scrollTop = term.scrollHeight;
        // Limit lines
        if (term.childElementCount > 150) {
            for(let i=0; i<20; i++) term.removeChild(term.firstChild);
        }
    });
}, 150);
"""

# Find the LAST </script> tag
last_script_idx = html.rfind("</script>")
if last_script_idx != -1:
    html = html[:last_script_idx] + terminal_js + "\n" + html[last_script_idx:]

with open("bl4s_event_explorer.html", "w") as f:
    f.write(html)
