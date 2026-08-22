import re

with open("bl4s_event_explorer.html", "r") as f:
    html = f.read()

# 1. REMOVE ALL EMOJIS (as requested: "ayrıca tüm emojileri kaldır")
emojis = ["⚡ ", "🌿 ", "🏷️ ", "📈 ", "🚀", "🎛️ ", "🖥️ ", "⏱️ ", "📊 ", "🌡️ ", "📸 ", "⏸ ", "▶ ", "⏹ ", "🔄 ", "🔗 ", "⚙️ ", 
          "⚡", "🌿", "🏷️", "📈", "🚀", "🎛️", "🖥️", "⏱️", "📊", "🌡️", "📸", "⏸", "▶", "⏹", "🔄", "🔗", "⚙️", "⚛️", "💡", "🔬", "📐", "🖲️", "🎯", "🗑️", "◀"]
for e in emojis:
    html = html.replace(e, "")

# 2. SIDEBAR REPLACEMENTS
# Remove Trigger Rate Series
trigger_sidebar_regex = r"<!-- Trigger -->\s*<div class=\"tree-sat\">\s*<div class=\"tree-sat-header\".*?<span>Trigger Rate Series</span>\s*</div>\s*</div>\s*</div>"
html = re.sub(trigger_sidebar_regex, "", html, flags=re.DOTALL)

# Remove Slow Control
sc_sidebar_regex = r"<div class=\"tree-view-item\" onclick=\"openPanel\('slow_control_view', 'Slow Control', 'Slow Control & Hardware Telemetry', 'slow_control', true\)\" data-view=\"slow_control_view\">\s*<span>Slow Control & Hardware</span>\s*<span class=\"badge-tag\" style=\"background:rgba\(245,158,11,0\.2\);color:#f59e0b;border:1px solid #f59e0b;\">EPICS</span>\s*</div>"
html = re.sub(sc_sidebar_regex, "", html, flags=re.DOTALL)

# Replace DAQ Run Control with Modern DFP Panel and Live Event Feed
rc_sidebar_regex = r"<div class=\"tree-view-item\" onclick=\"openPanel\('run_control_console', 'TDAQ System', 'DAQ Run Control & Partition Manager', 'run_control_console', true\)\" data-view=\"run_control_console\">\s*<span>DAQ Run Control</span>\s*<span class=\"badge-tag highlight\" style=\"background:rgba\(244,63,94,0\.2\);color:#f43f5e;border:1px solid #f43f5e;\">RC</span>\s*</div>"
df_sidebar_item = """<div class="tree-view-item" onclick="openPanel('dfp_panel', 'TDAQ System', 'DFP Panel & Network', 'dfp_panel', true)" data-view="dfp_panel">
                        <span>DFP Panel</span>
                        <span class="badge-tag highlight" style="background:rgba(56,189,248,0.15);color:#38bdf8;border:1px solid #38bdf8;">DFP</span>
                    </div>
                    <div class="tree-view-item" onclick="openPanel('live_event_feed', 'TDAQ System', 'Live Event Feed (Kafka)', 'live_event_feed', true)" data-view="live_event_feed">
                        <span>Live Event Feed</span>
                        <span class="badge-tag highlight" style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid #10b981;">LOG</span>
                    </div>"""
html = re.sub(rc_sidebar_regex, df_sidebar_item, html, flags=re.DOTALL)

# 3. ADD CSS FOR TERMINAL & DFP PANEL
modern_css = """
        /* ================= MODERN DFP PANEL & TERMINAL ================= */
        .modern-tdaq-wrap {
            height: 100%; display: flex; flex-direction: column;
            background: rgba(15, 23, 42, 0.4); border-radius: 8px; color: #f8fafc;
            border: 1px solid rgba(255, 255, 255, 0.05); font-family: 'Inter', sans-serif;
            overflow: hidden;
        }
        .modern-stats-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px; padding: 16px;
        }
        .modern-stat-card {
            background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 8px; padding: 12px; display: flex; flex-direction: column; gap: 4px;
        }
        .modern-stat-lbl { color: #94a3b8; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }
        .modern-stat-val { color: #f8fafc; font-size: 18px; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
        
        .terminal-container {
            flex: 1; background: #000; color: #10b981; font-family: 'JetBrains Mono', monospace;
            font-size: 12px; padding: 10px; overflow-y: auto; border-top: 1px solid #333;
            box-shadow: inset 0 0 20px rgba(0,0,0,0.8);
        }
        .terminal-line { margin-bottom: 4px; line-height: 1.4; word-wrap: break-word; }
        .term-ts { color: #64748b; margin-right: 8px; }
        .term-src { color: #f43f5e; margin-right: 8px; font-weight: bold; }
        .term-msg { color: #e2e8f0; }
        .term-data { color: #38bdf8; }
"""
html = html.replace("</style>", modern_css + "\n</style>")


# 4. REPLACE RUN CONTROL LOGIC WITH DFP AND TERMINAL
start_rc_idx = html.find("        } else if (chartType === 'run_control_console') {")
end_rc_idx = html.find("    } else if (chartType === 'run_control_console') {", start_rc_idx)

new_rc_code = """        } else if (chartType === 'dfp_panel') {
        bodyContent = `
            <div class="modern-tdaq-wrap">
                <div class="modern-stats-grid">
                    <div class="modern-stat-card"><span class="modern-stat-lbl">Network Bandwidth</span><span class="modern-stat-val" style="color:#38bdf8;">1.2 Gbps</span></div>
                    <div class="modern-stat-card"><span class="modern-stat-lbl">Data Written</span><span class="modern-stat-val" style="color:#a855f7;">4.2 TB</span></div>
                    <div class="modern-stat-card"><span class="modern-stat-lbl">Fragment Loss</span><span class="modern-stat-val" style="color:#10b981;">0.00%</span></div>
                    <div class="modern-stat-card"><span class="modern-stat-lbl">Kafka Broker Status</span><span class="modern-stat-val" style="color:#10b981;">HEALTHY</span></div>
                </div>
                <div style="flex:1; background:rgba(0,0,0,0.2); padding:20px; display:flex; flex-direction:column; gap:10px;">
                    <div style="color:#94a3b8; font-size:12px;">Active Pipeline: Satellites -> Kafka -> Builder -> HDF5</div>
                    <div style="color:#cbd5e1; font-size:11px; margin-top:20px;">
                        The Machine Learning and Physics Reconstruction satellites are processing events in real-time.<br><br>
                        They are currently analyzing synthetic collision data generated by the ML model.
                    </div>
                </div>
            </div>
        `;
        footerButtons = ' ';
        } else if (chartType === 'live_event_feed') {
        bodyContent = `
            <div class="modern-tdaq-wrap">
                <div style="background:#1e293b; padding:8px 16px; font-size:12px; font-weight:bold; border-bottom:1px solid #334155; display:flex; justify-content:space-between;">
                    <span>LIVE EVENT FEED</span>
                    <span style="color:#10b981;">Connected to Kafka:9092</span>
                </div>
                <div class="terminal-container" id="terminal-${viewId}">
                    <div class="terminal-line"><span class="term-ts">[SYSTEM]</span><span class="term-msg">Initializing TDAQ Live Event Feed...</span></div>
                    <div class="terminal-line"><span class="term-ts">[SYSTEM]</span><span class="term-msg">Subscribing to topics: 'ml_recon', 'physics_trigger'...</span></div>
                </div>
            </div>
        `;
        footerButtons = ' ';
        
"""

html = html[:start_rc_idx] + new_rc_code + html[end_rc_idx:]

# Also remove the second run_control_console if condition
start_rc_idx_2 = html.find("    } else if (chartType === 'run_control_console') {")
end_rc_idx_2 = html.find("} else if (chartType === 'dqm_view') {", start_rc_idx_2)
# We replace it with nothing since we handle dfp_panel and live_event_feed in the first pass
html = html[:start_rc_idx_2] + "    " + html[end_rc_idx_2:]


# 5. INJECT JAVASCRIPT FOR TERMINAL LOGIC
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
"""
# Append terminal JS before the final script close
html = html.replace("</script>", terminal_js + "\n</script>")


with open("bl4s_event_explorer.html", "w") as f:
    f.write(html)
