import re

with open("bl4s_event_explorer.html", "r") as f:
    html = f.read()

# 1. FIX ECHARTS INIT CRASH
# Replace:
#     } else {
#         const dom = document.getElementById(`chart-${viewId}`);
#         chart = echarts.init(dom);
# With:
#     } else if (chartType === 'dfp_panel' || chartType === 'live_event_feed' || chartType === 'geco_panel') {
#         chart = { type: chartType };
#     } else {
#         const dom = document.getElementById(`chart-${viewId}`);
#         chart = dom ? echarts.init(dom) : null;
#         if (chart) {

# Find the else block around line 2878
target_str = """    } else {
        const dom = document.getElementById(`chart-${viewId}`);
        chart = echarts.init(dom);"""

replacement_str = """    } else if (chartType === 'dfp_panel' || chartType === 'live_event_feed' || chartType === 'geco_panel') {
        chart = { type: chartType };
    } else {
        const dom = document.getElementById(`chart-${viewId}`);
        chart = dom ? echarts.init(dom) : null;
        if (chart) {"""

html = html.replace(target_str, replacement_str)

# Add closing brace for `if (chart) {` at the end of the `else` block
# Wait, the else block ends right before `activePanels[viewId] = { chart, satellite, chartType };`
end_else_str = """        } else if (chartType === 'coincidence_view') {
            createCoincidenceChart(chart);
        }
    }

    activePanels[viewId] = { chart, satellite, chartType };"""
end_else_repl = """        } else if (chartType === 'coincidence_view') {
            createCoincidenceChart(chart);
        }
        }
    }

    activePanels[viewId] = { chart, satellite, chartType };"""
html = html.replace(end_else_str, end_else_repl)

# 2. ADD GECO PANEL TO SIDEBAR
dfp_sidebar_str = """<div class="tree-view-item" onclick="openPanel('dfp_panel', 'TDAQ System', 'DFP Panel & Network', 'dfp_panel', true)" data-view="dfp_panel">"""
geco_sidebar = """<div class="tree-view-item" onclick="openPanel('geco_panel', 'Slow Control', 'CAEN GECO2020 High Voltage', 'geco_panel', true)" data-view="geco_panel">
                        <span>HV Control (GECO)</span>
                        <span class="badge-tag" style="background:rgba(16,185,129,0.15);color:#10b981;border:1px solid #10b981;">CAEN</span>
                    </div>\n                    """
html = html.replace(dfp_sidebar_str, geco_sidebar + dfp_sidebar_str)

# 3. ADD GECO CSS
geco_css = """
        /* ================= GECO 2020 STYLE ================= */
        .geco-wrap {
            height: 100%; display: flex; flex-direction: row; font-family: 'Arial', sans-serif;
            background: #8e9591; /* Grey background */
            color: #000; overflow: hidden; border: 2px solid #334155;
        }
        .geco-main {
            flex: 1; display: flex; flex-direction: column; border-right: 2px solid #555;
            background: #c3c7c2;
        }
        .geco-header-bar {
            background: #3e5a40; /* Dark green */
            color: white; padding: 4px 10px; font-size: 11px; font-weight: bold;
            display: flex; align-items: center; justify-content: space-between;
        }
        .geco-table {
            width: 100%; border-collapse: collapse; font-size: 10px; font-family: 'Tahoma', sans-serif;
        }
        .geco-table th {
            background: #a9afa8; color: #333; border: 1px solid #888; padding: 4px;
            text-align: center; font-weight: bold;
        }
        .geco-table td {
            background: #e2e6df; color: #000; border: 1px solid #888; padding: 3px 6px;
            text-align: right;
        }
        .geco-table td:nth-child(2) { text-align: left; font-weight: bold; }
        .geco-table tr.geco-tripped td { background: #d32f2f !important; color: white !important; font-weight: bold; }
        .geco-table tr.geco-off td.geco-pw { color: #555; }
        .geco-table tr.geco-on td.geco-pw { color: #10b981; font-weight: bold; }
        
        .geco-side {
            width: 160px; background: #3e5a40; display: flex; flex-direction: column;
            padding: 8px; gap: 8px; overflow-y: auto;
        }
        .geco-board {
            background: #80b585; border: 1px solid #1a2f1b; border-radius: 2px;
            padding: 6px; font-size: 10px; color: #000;
        }
        .geco-board-title {
            background: #1a2f1b; color: white; padding: 3px; font-weight: bold;
            text-align: center; margin-bottom: 6px;
        }
        .geco-board-row { display: flex; justify-content: space-between; margin-bottom: 2px; }
"""
html = html.replace("/* ================= MODERN DFP PANEL & TERMINAL ================= */", geco_css + "\n        /* ================= MODERN DFP PANEL & TERMINAL ================= */")


# 4. ADD GECO BODY CONTENT
geco_body = """        } else if (chartType === 'geco_panel') {
        bodyContent = `
            <div class="geco-wrap">
                <div class="geco-main">
                    <div class="geco-header-bar">
                        <span>System</span>
                        <span>MultiChannel High Voltage System</span>
                    </div>
                    <div style="flex:1; overflow-y:auto;">
                        <table class="geco-table" id="geco-table-${viewId}">
                            <thead>
                                <tr>
                                    <th>Custom</th><th>Name</th><th>I0Set</th><th>V0Set</th><th>IMon</th><th>VMon</th><th>Pw</th><th>Status</th><th>RUp</th><th>RDown</th><th>Trip</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr id="gch-CAL9"><td>00.007</td><td>CAL9</td><td>500.0 uA</td><td>1350.0 V</td><td class="imon">402.6 uA</td><td class="vmon">1351.0 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td></tr>
                                <tr id="gch-CAL10"><td>00.008</td><td>CAL10</td><td>500.0 uA</td><td>1475.0 V</td><td class="imon">436.5 uA</td><td class="vmon">1476.0 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td></tr>
                                <tr id="gch-CAL11"><td>00.009</td><td>CAL11</td><td>500.0 uA</td><td>1500.0 V</td><td class="imon">445.5 uA</td><td class="vmon">1505.5 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td></tr>
                                <tr id="gch-CAL12"><td>00.010</td><td>CAL12</td><td>500.0 uA</td><td>1500.0 V</td><td class="imon">448.0 uA</td><td class="vmon">1501.0 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td></tr>
                                <tr id="gch-S2"><td>02.006</td><td>S2</td><td>2000.0 uA</td><td>2100.0 V</td><td class="imon">0.0 uA</td><td class="vmon">0.0 V</td><td class="geco-pw" style="color:#555">Off</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td></tr>
                                <tr id="gch-S3"><td>02.007</td><td>S3</td><td>2000.0 uA</td><td>2250.0 V</td><td class="imon">0.0 uA</td><td class="vmon">0.0 V</td><td class="geco-pw" style="color:#555">Off</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td></tr>
                                <tr id="gch-MESH" class="geco-off"><td>02.008</td><td>MESH</td><td>0.0 uA</td><td>1055.0 V</td><td class="imon">0.0 uA</td><td class="vmon">0.0 V</td><td class="geco-pw" style="color:#555">Off</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>5.0 sec</td></tr>
                                <tr id="gch-DRIFT" class="geco-tripped"><td>02.009</td><td>DRIFT</td><td>0.0 uA</td><td>0.0 V</td><td class="imon">0.0 uA</td><td class="vmon">0.0 V</td><td class="geco-pw">Off</td><td class="status">I-Tripped</td><td>250 Vps</td><td>250 Vps</td><td>5.0 sec</td></tr>
                                <tr id="gch-DWC0"><td>04.000</td><td>DWC0</td><td>20.00 uA</td><td>2600.0 V</td><td class="imon">0.016 uA</td><td class="vmon">2599.95 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td></tr>
                                <tr id="gch-DWC1"><td>04.001</td><td>DWC1</td><td>20.00 uA</td><td>2700.0 V</td><td class="imon">0.030 uA</td><td class="vmon">2699.85 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
                
                <div class="geco-side">
                    <div style="color:white; font-size:11px; font-weight:bold; margin-bottom:4px;">BOARDS</div>
                    
                    <div class="geco-board">
                        <div class="geco-board-title">▼ Board00 - A1535D</div>
                        <div style="display:flex; gap:10px; margin-bottom:8px;">
                            <div style="width:12px; height:40px; background:#4CAF50; border:1px solid #111;"></div>
                            <div style="flex:1; text-align:center; padding-top:10px;">A1535D<br>Module</div>
                        </div>
                        <div class="geco-board-row"><span>BdStatus</span><span>OK</span></div>
                        <div class="geco-board-row"><span>HVMax</span><span>3579.00</span></div>
                        <div class="geco-board-row"><span>Temp</span><span>26.00 C</span></div>
                    </div>
                    
                    <div class="geco-board">
                        <div class="geco-board-title">▼ Board02 - A1535D</div>
                        <div style="display:flex; gap:10px; margin-bottom:8px;">
                            <div style="width:12px; height:40px; background:#4CAF50; border:1px solid #111;"></div>
                            <div style="flex:1; text-align:center; padding-top:10px;">A1535D<br>Module</div>
                        </div>
                        <div class="geco-board-row"><span>BdStatus</span><span>OK</span></div>
                        <div class="geco-board-row"><span>HVMax</span><span>3506.00</span></div>
                        <div class="geco-board-row"><span>Temp</span><span>25.00 C</span></div>
                    </div>
                    
                    <div class="geco-board" style="background:#b59880;">
                        <div class="geco-board-title" style="background:#5c351b;">▼ Board04 - A7030DP</div>
                        <div style="display:flex; gap:10px; margin-bottom:8px;">
                            <div style="width:12px; height:40px; background:#f44336; border:1px solid #111;"></div>
                            <div style="flex:1; text-align:center; padding-top:10px;">A7030DP<br>Module</div>
                        </div>
                        <div class="geco-board-row"><span>BdStatus</span><span style="color:#d32f2f;font-weight:bold;">TRIP</span></div>
                        <div class="geco-board-row"><span>HVMax</span><span>3177.00</span></div>
                        <div class="geco-board-row"><span>Temp</span><span>29.00 C</span></div>
                    </div>
                </div>
            </div>
        `;
        footerButtons = '<button class="btn-action" style="background:#d32f2f; color:white; border:1px solid #b71c1c;" onclick="alert(\\\'Sending Clear Alarm command to CAEN crate...\\\')">Clear Alarm</button>';
        
"""

dfp_find_str = "} else if (chartType === 'dfp_panel') {"
html = html.replace(dfp_find_str, geco_body + dfp_find_str)


# 5. Add Live Simulation for GECO values (fluctuations)
geco_js = """
setInterval(() => {
    // Randomly fluctuate VMon and IMon for active channels
    const rows = document.querySelectorAll('.geco-table tbody tr:not(.geco-off):not(.geco-tripped)');
    rows.forEach(row => {
        const vmonCell = row.querySelector('.vmon');
        const imonCell = row.querySelector('.imon');
        if (vmonCell && vmonCell.innerText !== '0.0 V') {
            const baseV = parseFloat(row.querySelector('td:nth-child(4)').innerText);
            vmonCell.innerText = (baseV + (Math.random() * 2 - 1)).toFixed(1) + ' V';
        }
        if (imonCell && imonCell.innerText !== '0.0 uA') {
            const currentI = parseFloat(imonCell.innerText);
            imonCell.innerText = (currentI + (Math.random() * 0.4 - 0.2)).toFixed(1) + ' uA';
        }
    });
}, 500);
"""
# Insert before final script tag
last_script_idx = html.rfind("</script>")
html = html[:last_script_idx] + geco_js + "\n" + html[last_script_idx:]

with open("bl4s_event_explorer.html", "w") as f:
    f.write(html)
