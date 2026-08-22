import sys

with open("bl4s_event_explorer.html", "r") as f:
    html = f.read()

# Locate the GECO CSS block
css_start = html.find("/* ================= GECO 2020 STYLE ================= */")
css_end = html.find("/* ================= MODERN DFP PANEL & TERMINAL ================= */")
if css_start == -1 or css_end == -1:
    print("Could not find CSS markers")
    sys.exit(1)

new_geco_css = """
        /* ================= GECO 2020 STYLE EXACT REPLICA ================= */
        .geco-wrap {
            height: 100%; display: flex; flex-direction: column; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #d4d0c8; /* Classic Windows grey */
            color: #000; overflow: hidden; border: 1px solid #888;
        }
        
        /* Top Menu Bar */
        .geco-top-menu {
            display: flex; gap: 15px; padding: 2px 10px; font-size: 11px; background: #f0f0f0; border-bottom: 1px solid #ccc;
            cursor: pointer;
        }
        .geco-top-menu span:hover { text-decoration: underline; }
        
        /* Title Bar */
        .geco-title-bar {
            background: #505050; color: white; padding: 6px 12px; font-size: 16px; font-weight: bold;
            display: flex; align-items: center; justify-content: space-between;
        }
        
        /* Toolbar */
        .geco-toolbar {
            background: #e0e0e0; padding: 4px 10px; border-bottom: 1px solid #999;
            display: flex; justify-content: flex-end; gap: 4px;
        }
        .geco-toolbar-btn {
            width: 16px; height: 12px; background: #bbb; border: 1px solid #888; border-radius: 1px;
        }
        
        /* Main Workspace */
        .geco-workspace {
            flex: 1; display: flex; flex-direction: row; background: #617765; padding: 4px; gap: 4px;
            overflow: hidden;
        }
        
        /* Left Sidebar (Tree) */
        .geco-left-tree {
            width: 120px; background: #d0d7cf; border: 1px solid #555; display: flex; flex-direction: column;
        }
        .geco-tree-header {
            background: #a9afa8; font-size: 10px; font-weight: bold; padding: 2px 4px; border-bottom: 1px solid #888; text-align: center;
        }
        .geco-tree-content {
            flex: 1; padding: 4px; font-size: 10px; font-weight: bold; font-family: 'Tahoma', sans-serif; background: #e2e6df;
        }
        .geco-tree-node { margin-bottom: 2px; display: flex; align-items: center; cursor:pointer; }
        .geco-tree-dot { width: 6px; height: 6px; border-radius: 50%; background: #4CAF50; display: inline-block; margin-right: 4px; border: 1px solid #222; }
        
        /* Center Table Area */
        .geco-main-center {
            flex: 1; display: flex; flex-direction: column; background: #d0d7cf; border: 1px solid #555;
        }
        .geco-tab-bar {
            display: flex; background: #a9afa8; padding-top: 2px;
        }
        .geco-tab-active {
            background: #d0d7cf; border: 1px solid #888; border-bottom: none; padding: 2px 20px; font-size: 10px; margin-left: 20px; border-top-left-radius: 3px; border-top-right-radius: 3px;
        }
        
        /* Table */
        .geco-table-container {
            flex: 1; overflow-y: auto; background: white;
        }
        .geco-table {
            width: 100%; border-collapse: collapse; font-size: 10px; font-family: 'Tahoma', sans-serif;
            white-space: nowrap;
        }
        .geco-table th {
            background: #8e9591; color: white; border: 1px solid #555; padding: 3px 2px;
            text-align: center; font-weight: normal; position: sticky; top: 0; z-index: 10;
        }
        .geco-table td {
            background: #e2e6df; color: #000; border: 1px solid #888; padding: 2px 4px;
            text-align: right;
        }
        .geco-table td:nth-child(2) { text-align: left; }
        .geco-table tr.geco-tripped td { background: #d32f2f !important; color: white !important; }
        .geco-table tr.geco-off td.geco-pw { color: #555; }
        .geco-table tr.geco-on td.geco-pw { color: #10b981; font-weight: bold; }
        .geco-table tr:nth-child(even) td { background: #d4dbd1; }
        
        /* Right Panels (Boards) */
        .geco-right-panel {
            width: 140px; background: #3e5a40; display: flex; flex-direction: column;
            border: 1px solid #222;
        }
        .geco-board-header {
            color: white; font-size: 9px; font-weight: bold; padding: 2px; border-bottom: 1px solid #222;
        }
        .geco-boards-scroll {
            flex: 1; overflow-y: auto; padding: 2px; display: flex; flex-direction: column; gap: 4px;
        }
        .geco-board {
            background: #80b585; border: 1px solid #1a2f1b; font-size: 9px; color: #000;
        }
        .geco-board-title {
            background: #4CAF50; color: black; padding: 2px; font-weight: bold; border-bottom: 1px solid #1a2f1b; cursor: pointer;
        }
        .geco-board-title-red {
            background: #4CAF50; color: black; padding: 2px; font-weight: bold; border-bottom: 1px solid #1a2f1b;
        }
        .geco-board-body { padding: 4px; display: flex; gap: 4px; }
        .geco-board-col1 { width: 10px; border: 1px solid #333; background: #666; display:flex; flex-direction:column; justify-content:space-between; }
        .geco-board-col2 { flex: 1; display:flex; flex-direction:column; justify-content:center; align-items:center; text-align:center; font-family:serif; }
        .geco-board-stats { font-family: 'Tahoma', sans-serif; padding: 2px; }
        .geco-board-row { display: flex; justify-content: space-between; margin-bottom: 1px; }
"""
html = html[:css_start] + new_geco_css + "\n" + html[css_end:]

# Now replace bodyContent for geco_panel
body_start = html.find("} else if (chartType === 'geco_panel') {")
body_end = html.find("} else if (chartType === 'dfp_panel') {")
if body_start == -1 or body_end == -1:
    print("Could not find body content markers")
    sys.exit(1)

new_body_content = """} else if (chartType === 'geco_panel') {
        bodyContent = `
            <div class="geco-wrap">
                <!-- Top Menus -->
                <div class="geco-top-menu">
                    <span>System</span>
                    <span>Window</span>
                    <span>Help</span>
                </div>
                
                <!-- Title Bar -->
                <div class="geco-title-bar">
                    <div style="display:flex; align-items:center;">
                        <span style="color:#f44336; margin-right:4px;">■</span>
                        <span>General Control Software</span>
                    </div>
                    <span style="color:#fbbf24; background:#78350f; padding:2px 6px; border-radius:2px; font-size:10px; border:1px solid #b45309;">SIMULATION MODE (NO HARDWARE IP)</span>
                </div>
                
                <!-- Toolbar -->
                <div class="geco-toolbar">
                    <div class="geco-toolbar-btn"></div><div class="geco-toolbar-btn"></div><div class="geco-toolbar-btn"></div>
                </div>
                
                <!-- Workspace -->
                <div class="geco-workspace">
                    
                    <!-- Left Sidebar (Tree) -->
                    <div class="geco-left-tree">
                        <div class="geco-tree-header">Configure</div>
                        <div class="geco-tree-content">
                            <div style="color:#4CAF50; font-style:italic; margin-bottom:6px; font-size:9px;">MULTICHANNEL<br>SYSTEM</div>
                            <div class="geco-tree-node" style="margin-left:2px;">▼ SystemOne</div>
                            <div class="geco-tree-node" style="margin-left:12px;"><span class="geco-tree-dot"></span> 1716</div>
                            <div class="geco-tree-node" style="margin-left:12px;"><span class="geco-tree-dot"></span> 1680</div>
                            <div class="geco-tree-node" style="margin-left:12px;"><span class="geco-tree-dot"></span> 1716</div>
                            <div class="geco-tree-node" style="margin-left:12px; margin-top:8px; color:#555;">Disabled</div>
                        </div>
                    </div>
                    
                    <!-- Main Table -->
                    <div class="geco-main-center">
                        <div class="geco-tab-bar">
                            <div class="geco-tab-active">System</div>
                        </div>
                        <div class="geco-table-container">
                            <table class="geco-table" id="geco-table-${viewId}">
                                <thead>
                                    <tr>
                                        <th>Custom</th><th>Name</th><th>I0Set</th><th>V0Set</th><th>IMon</th><th>VMon</th><th>Pw</th><th>Status</th><th>RUp</th><th>RDown</th><th>Trip</th><th>V1Set</th><th>I1Set</th><th>SVMax</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    <tr id="gch-CAL9"><td>00.007</td><td>CAL9</td><td>500.0 uA</td><td>1350.0 V</td><td class="imon">402.6 uA</td><td class="vmon">1351.0 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td><td>0.0 V</td><td>300.0 uA</td><td>3500 V</td></tr>
                                    <tr id="gch-CAL10"><td>00.008</td><td>CAL10</td><td>500.0 uA</td><td>1475.0 V</td><td class="imon">436.5 uA</td><td class="vmon">1476.0 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td><td>0.0 V</td><td>300.0 uA</td><td>3500 V</td></tr>
                                    <tr id="gch-CAL11"><td>00.009</td><td>CAL11</td><td>500.0 uA</td><td>1500.0 V</td><td class="imon">445.5 uA</td><td class="vmon">1505.5 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td><td>0.0 V</td><td>300.0 uA</td><td>3500 V</td></tr>
                                    <tr id="gch-CAL12"><td>00.010</td><td>CAL12</td><td>500.0 uA</td><td>1500.0 V</td><td class="imon">448.0 uA</td><td class="vmon">1501.0 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td><td>0.0 V</td><td>300.0 uA</td><td>3500 V</td></tr>
                                    <tr id="gch-CAL13"><td>00.011</td><td>CAL13</td><td>500.0 uA</td><td>1350.0 V</td><td class="imon">401.0 uA</td><td class="vmon">1350.5 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td><td>0.0 V</td><td>300.0 uA</td><td>3500 V</td></tr>
                                    <tr id="gch-CAL14"><td>02.000</td><td>CAL14</td><td>500.0 uA</td><td>1350.0 V</td><td class="imon">404.0 uA</td><td class="vmon">1351.0 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td><td>0.0 V</td><td>300.0 uA</td><td>3500 V</td></tr>
                                    <tr id="gch-CAL17"><td>02.001</td><td>CAL17</td><td>500.0 uA</td><td>1400.0 V</td><td class="imon">416.5 uA</td><td class="vmon">1401.0 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td><td>0.0 V</td><td>300.0 uA</td><td>3500 V</td></tr>
                                    <tr id="gch-S2"><td>02.006</td><td>S2</td><td>2000.0 uA</td><td>2100.0 V</td><td class="imon">0.0 uA</td><td class="vmon">0.0 V</td><td class="geco-pw" style="color:#555">Off</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td><td>0.0 V</td><td>300.0 uA</td><td>3500 V</td></tr>
                                    <tr id="gch-S3"><td>02.007</td><td>S3</td><td>2000.0 uA</td><td>2250.0 V</td><td class="imon">0.0 uA</td><td class="vmon">0.0 V</td><td class="geco-pw" style="color:#555">Off</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td><td>0.0 V</td><td>300.0 uA</td><td>3500 V</td></tr>
                                    <tr id="gch-MESH" class="geco-off"><td>02.008</td><td>MESH</td><td>0.0 uA</td><td>1055.0 V</td><td class="imon">0.0 uA</td><td class="vmon">0.0 V</td><td class="geco-pw" style="color:#555">Off</td><td class="status">250 Vps</td><td>250 Vps</td><td>5.0 sec</td><td>0.0 V</td><td>300.0 uA</td><td>3500 V</td></tr>
                                    <tr id="gch-DRIFT" class="geco-tripped"><td>02.009</td><td>DRIFT</td><td>0.0 uA</td><td>0.0 V</td><td class="imon">0.0 uA</td><td class="vmon">0.0 V</td><td class="geco-pw">Off</td><td class="status">I-Tripped</td><td>250 Vps</td><td>250 Vps</td><td>5.0 sec</td><td>0.0 V</td><td>300.0 uA</td><td>3500 V</td></tr>
                                    <tr id="gch-DWC0"><td>04.000</td><td>DWC0</td><td>20.00 uA</td><td>2600.0 V</td><td class="imon">0.016 uA</td><td class="vmon">2599.95 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td><td>0.0 V</td><td>101.00 uA</td><td>3000 V</td></tr>
                                    <tr id="gch-DWC1"><td>04.001</td><td>DWC1</td><td>20.00 uA</td><td>2700.0 V</td><td class="imon">0.030 uA</td><td class="vmon">2699.85 V</td><td class="geco-pw">On</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td><td>0.0 V</td><td>101.00 uA</td><td>3000 V</td></tr>
                                    <tr id="gch-CH02"><td>04.002</td><td>CHANNEL02</td><td>10.00 uA</td><td>0.00 V</td><td class="imon">0.008 uA</td><td class="vmon">8.16 V</td><td class="geco-pw" style="color:#555">Off</td><td class="status">250 Vps</td><td>250 Vps</td><td>250 Vps</td><td>10.0 sec</td><td>0.0 V</td><td>101.00 uA</td><td>3000 V</td></tr>
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    <!-- Right Board Panels -->
                    <div class="geco-right-panel">
                        <div class="geco-board-header">BOARDS</div>
                        <div class="geco-boards-scroll">
                        
                            <div class="geco-board">
                                <div class="geco-board-title">▼ Board00 - A1535D - [</div>
                                <div class="geco-board-body">
                                    <div class="geco-board-col1"><div style="background:#4CAF50;height:4px;"></div><div style="background:#4CAF50;height:4px;"></div></div>
                                    <div class="geco-board-col2">A1535D<br>Module</div>
                                </div>
                                <div class="geco-board-stats">
                                    <div class="geco-board-row"><span>BdStatus</span><span>OK</span></div>
                                    <div class="geco-board-row"><span>HVMax</span><span>3579.00</span></div>
                                    <div class="geco-board-row"><span>Temp</span><span>26.00</span></div>
                                </div>
                            </div>
                            
                            <div class="geco-board">
                                <div class="geco-board-title">▼ Board02 - A1535D - [</div>
                                <div class="geco-board-body">
                                    <div class="geco-board-col1"><div style="background:#4CAF50;height:4px;"></div><div style="background:#4CAF50;height:4px;"></div></div>
                                    <div class="geco-board-col2">A1535D<br>Module</div>
                                </div>
                                <div class="geco-board-stats">
                                    <div class="geco-board-row"><span>BdStatus</span><span>OK</span></div>
                                    <div class="geco-board-row"><span>HVMax</span><span>3506.00</span></div>
                                    <div class="geco-board-row"><span>Temp</span><span>25.00</span></div>
                                </div>
                            </div>
                            
                            <div class="geco-board" style="background:#80b585;">
                                <div class="geco-board-title">▼ Board04 - A7030DP - [</div>
                                <div class="geco-board-body">
                                    <div class="geco-board-col1"><div style="background:#4CAF50;height:4px;"></div><div style="background:#4CAF50;height:4px;"></div></div>
                                    <div class="geco-board-col2">A7030DP<br>Module</div>
                                </div>
                                <div class="geco-board-stats">
                                    <div class="geco-board-row"><span>BdStatus</span><span style="color:#222;">OK</span></div>
                                    <div class="geco-board-row"><span>HVMax</span><span>3177.00</span></div>
                                    <div class="geco-board-row"><span>Temp</span><span>29.00</span></div>
                                </div>
                            </div>
                            
                        </div>
                    </div>
                    
                </div> <!-- End Workspace -->
            </div>
        `;
        footerButtons = ' ';
        
"""

html = html[:body_start] + new_body_content + html[body_end:]

with open("bl4s_event_explorer.html", "w") as f:
    f.write(html)
