import re

with open("bl4s_event_explorer.html", "r") as f:
    html = f.read()

# 1. Update CSS for Modern DFP and Modern CAEN HV
css_start = html.find("/* ================= GECO 2020 STYLE")
css_end = html.find("/* Intro.js for Interactive Tutorial")
if css_start == -1 or css_end == -1:
    # Try finding modern tdaq wrap
    css_start = html.find("/* ================= MODERN DFP PANEL & TERMINAL")
    if css_start == -1:
        print("CSS markers not found")

new_css = """/* ================= MODERN HIGH-TECH CAEN HV CONTROL DASHBOARD ================= */
        .modern-hv-wrap {
            height: 100%; display: flex; flex-direction: column;
            background: #090d16; color: #e2e8f0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            overflow: hidden; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);
        }
        
        /* Header */
        .modern-hv-header {
            background: #0d1527; padding: 12px 18px; border-bottom: 1px solid rgba(56, 189, 248, 0.15);
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;
        }
        .modern-hv-title-area { display: flex; align-items: center; gap: 12px; }
        .modern-hv-badge {
            background: rgba(16, 185, 129, 0.15); color: #10b981; border: 1px solid #10b981;
            padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: 600;
        }
        .modern-hv-stats {
            display: flex; gap: 16px; font-size: 12px; color: #94a3b8; font-family: 'JetBrains Mono', monospace;
        }
        .modern-hv-stat-item { display: flex; align-items: center; gap: 6px; }
        .modern-hv-stat-item b { color: #f8fafc; }
        
        /* Master Controls Bar */
        .modern-hv-actions-bar {
            background: #111a2e; padding: 8px 16px; border-bottom: 1px solid rgba(255,255,255,0.06);
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;
        }
        .modern-hv-tabs { display: flex; gap: 6px; }
        .modern-hv-tab-btn {
            background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #94a3b8;
            padding: 5px 12px; border-radius: 4px; font-size: 12px; cursor: pointer; transition: all 0.2s;
        }
        .modern-hv-tab-btn:hover { background: rgba(56, 189, 248, 0.15); color: #38bdf8; }
        .modern-hv-tab-btn.active { background: rgba(56, 189, 248, 0.25); color: #38bdf8; border-color: #38bdf8; font-weight: 600; }
        
        .modern-hv-btns { display: flex; gap: 8px; }
        .modern-btn-sm {
            padding: 5px 12px; border-radius: 4px; font-size: 11px; font-weight: 600; cursor: pointer;
            border: 1px solid transparent; transition: all 0.2s; display: inline-flex; align-items: center; gap: 5px;
        }
        .btn-hv-on { background: rgba(16, 185, 129, 0.2); color: #10b981; border-color: #10b981; }
        .btn-hv-on:hover { background: #10b981; color: #fff; }
        .btn-hv-off { background: rgba(239, 68, 68, 0.2); color: #ef4444; border-color: #ef4444; }
        .btn-hv-off:hover { background: #ef4444; color: #fff; }
        .btn-hv-reset { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border-color: #f59e0b; }
        .btn-hv-reset:hover { background: #f59e0b; color: #000; }
        
        /* Table Container */
        .modern-hv-table-container {
            flex: 1; overflow-y: auto; background: #070b12;
        }
        .modern-hv-table {
            width: 100%; border-collapse: collapse; font-size: 12px; font-family: 'JetBrains Mono', monospace;
            text-align: left;
        }
        .modern-hv-table th {
            background: #111a2e; color: #94a3b8; padding: 10px 12px; font-weight: 600;
            border-bottom: 1px solid rgba(255,255,255,0.08); position: sticky; top: 0; z-index: 10;
            font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px;
        }
        .modern-hv-table td {
            padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.04); vertical-align: middle;
        }
        .modern-hv-table tr:hover td { background: rgba(56, 189, 248, 0.04); }
        .modern-hv-ch-name { font-weight: bold; color: #f8fafc; display: flex; align-items: center; gap: 8px; }
        .modern-hv-detector-tag {
            font-size: 9px; padding: 2px 6px; border-radius: 3px; background: rgba(255,255,255,0.08); color: #cbd5e1;
        }
        
        /* Modern Switch */
        .hv-switch {
            position: relative; display: inline-block; width: 34px; height: 18px;
        }
        .hv-switch input { opacity: 0; width: 0; height: 0; }
        .hv-slider {
            position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
            background-color: #334155; transition: .3s; border-radius: 18px;
        }
        .hv-slider:before {
            position: absolute; content: ""; height: 12px; width: 12px; left: 3px; bottom: 3px;
            background-color: white; transition: .3s; border-radius: 50%;
        }
        input:checked + .hv-slider { background-color: #10b981; }
        input:checked + .hv-slider:before { transform: translateX(16px); }
        
        .hv-status-pill {
            display: inline-flex; align-items: center; gap: 5px; padding: 3px 8px; border-radius: 12px;
            font-size: 11px; font-weight: 600;
        }
        .hv-status-on { background: rgba(16,185,129,0.15); color: #10b981; border: 1px solid rgba(16,185,129,0.3); }
        .hv-status-off { background: rgba(148,163,184,0.1); color: #94a3b8; border: 1px solid rgba(148,163,184,0.2); }
        .hv-status-trip { background: rgba(239,68,68,0.2); color: #ef4444; border: 1px solid #ef4444; animation: pulseTrip 1.5s infinite; }
        
        @keyframes pulseTrip { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        
        .hv-input-vset {
            background: #1e293b; border: 1px solid #475569; color: #38bdf8; padding: 3px 6px;
            border-radius: 4px; width: 70px; font-family: inherit; font-size: 12px; text-align: right;
        }
        .hv-input-vset:focus { outline: none; border-color: #38bdf8; box-shadow: 0 0 6px rgba(56,189,248,0.4); }

        /* ================= MODERN DFP & BEAMLINE FLOW PANEL ================= */
        .modern-dfp-wrap {
            height: 100%; display: flex; flex-direction: column;
            background: #080d1a; color: #f8fafc; font-family: 'Inter', sans-serif;
            border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); overflow: hidden;
        }
        
        /* Beam Status Banner */
        .dfp-beam-banner {
            background: linear-gradient(90deg, #0e1e38 0%, #11294d 100%);
            padding: 12px 18px; border-bottom: 1px solid rgba(56, 189, 248, 0.2);
            display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;
        }
        .dfp-beam-title { display: flex; align-items: center; gap: 10px; }
        .dfp-beam-pulse {
            width: 10px; height: 10px; border-radius: 50%; background: #10b981;
            box-shadow: 0 0 10px #10b981; animation: beamPulse 1.2s infinite;
        }
        @keyframes beamPulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.4); opacity: 0.7; } }
        
        .dfp-beam-metrics {
            display: flex; gap: 16px; font-family: 'JetBrains Mono', monospace; font-size: 12px;
        }
        .dfp-metric-chip {
            background: rgba(0,0,0,0.3); padding: 4px 10px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.08);
            display: flex; align-items: center; gap: 6px;
        }
        .dfp-metric-chip span { color: #94a3b8; }
        .dfp-metric-chip b { color: #38bdf8; }

        /* Rates Grid */
        .dfp-rates-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 12px; padding: 14px 18px; background: #0c1322;
        }
        .dfp-rate-card {
            background: #111a2e; border: 1px solid rgba(255,255,255,0.06); border-radius: 6px;
            padding: 12px; display: flex; flex-direction: column; gap: 6px; position: relative; overflow: hidden;
        }
        .dfp-rate-card::before {
            content: ''; position: absolute; top: 0; left: 0; width: 3px; height: 100%; background: #38bdf8;
        }
        .dfp-rate-card.calo::before { background: #f59e0b; }
        .dfp-rate-card.track::before { background: #10b981; }
        .dfp-rate-card.trig::before { background: #a855f7; }
        .dfp-rate-card.daq::before { background: #ec4899; }
        
        .dfp-rate-lbl { font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }
        .dfp-rate-val { font-size: 20px; font-weight: 700; font-family: 'JetBrains Mono', monospace; color: #f8fafc; }
        .dfp-rate-sub { font-size: 11px; color: #64748b; font-family: 'JetBrains Mono', monospace; }

        /* Synoptic Beamline Flow */
        .dfp-flow-section {
            flex: 1; padding: 14px 18px; display: flex; flex-direction: column; gap: 10px; overflow-y: auto;
        }
        .dfp-flow-title { font-size: 12px; font-weight: 600; color: #cbd5e1; text-transform: uppercase; letter-spacing: 0.5px; }
        .dfp-flow-chain {
            display: flex; align-items: center; gap: 8px; flex-wrap: wrap; background: #111a2e;
            padding: 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06);
        }
        .dfp-node {
            background: #1e293b; border: 1px solid #334155; border-radius: 6px; padding: 8px 12px;
            font-size: 11px; font-family: 'JetBrains Mono', monospace; display: flex; flex-direction: column; gap: 2px;
            min-width: 120px;
        }
        .dfp-node.active { border-color: #10b981; box-shadow: 0 0 10px rgba(16,185,129,0.15); }
        .dfp-node-name { font-weight: bold; color: #f8fafc; }
        .dfp-node-rate { font-size: 10px; color: #10b981; }
        .dfp-arrow { color: #64748b; font-size: 14px; }
"""

# Replace CSS block
css_match = re.search(r'/\* =+ GECO 2020 STYLE.*?</style>', html, re.DOTALL)
if css_match:
    html = html[:css_match.start()] + new_css + "\n</style>" + html[css_match.end():]
else:
    print("Could not match CSS block with regex")

# 2. Modern GECO Panel HTML
modern_geco_html = """} else if (chartType === 'geco_panel') {
        bodyContent = `
            <div class="modern-hv-wrap" id="hv-mainframe-${viewId}">
                <!-- Crate Header -->
                <div class="modern-hv-header">
                    <div class="modern-hv-title-area">
                        <span style="font-size:15px; font-weight:bold; color:#f8fafc;">CAEN SY5527 High Voltage Mainframe</span>
                        <span class="modern-hv-badge">CRATE ONLINE</span>
                        <span style="color:#fbbf24; background:rgba(245,158,11,0.15); border:1px solid #f59e0b; padding:2px 8px; border-radius:4px; font-size:11px;">SIMULATION & FIELD READY</span>
                    </div>
                    <div class="modern-hv-stats">
                        <div class="modern-hv-stat-item"><span>Crate IP:</span> <b id="hv-crate-ip">192.168.1.100:1470</b></div>
                        <div class="modern-hv-stat-item"><span>Temp:</span> <b id="hv-crate-temp">24.6 °C</b></div>
                        <div class="modern-hv-stat-item"><span>Total Load:</span> <b id="hv-crate-pwr" style="color:#38bdf8;">142.8 W</b></div>
                        <div class="modern-hv-stat-item"><span>Interlock:</span> <b style="color:#10b981;">LOCKED (OK)</b></div>
                    </div>
                </div>
                
                <!-- Actions & Filter Bar -->
                <div class="modern-hv-actions-bar">
                    <div class="modern-hv-tabs">
                        <button class="modern-hv-tab-btn active" onclick="filterHvTable('all')">All Channels (20)</button>
                        <button class="modern-hv-tab-btn" onclick="filterHvTable('calo')">Calorimeter 4×4 (16)</button>
                        <button class="modern-hv-tab-btn" onclick="filterHvTable('scint')">Trigger & Veto (3)</button>
                        <button class="modern-hv-tab-btn" onclick="filterHvTable('tracking')">Tracking & Cherenkov (3)</button>
                    </div>
                    <div class="modern-hv-btns">
                        <button class="modern-btn-sm btn-hv-on" onclick="setAllHvChannels(true)">⚡ Turn All ON</button>
                        <button class="modern-btn-sm btn-hv-off" onclick="setAllHvChannels(false)">⛔ Standby (All OFF)</button>
                        <button class="modern-btn-sm btn-hv-reset" onclick="resetAllHvAlarms()">🔄 Clear Trips / Alarms</button>
                    </div>
                </div>
                
                <!-- Main Channels Table -->
                <div class="modern-hv-table-container">
                    <table class="modern-hv-table" id="hvChannelsTable">
                        <thead>
                            <tr>
                                <th>Slot.Ch</th>
                                <th>Channel Name</th>
                                <th>Detector Subsystem</th>
                                <th>Power</th>
                                <th>Status</th>
                                <th style="text-align:right;">V0Set (V)</th>
                                <th style="text-align:right;">VMon (V)</th>
                                <th style="text-align:right;">IMon (µA)</th>
                                <th style="text-align:right;">I0Limit</th>
                                <th style="text-align:right;">Ramp (V/s)</th>
                            </tr>
                        </thead>
                        <tbody id="hvTableBody">
                            <!-- Populated dynamically / pre-rendered -->
                            ${generateHvChannelRows()}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        footerButtons = '<button class="btn-action" onclick="resetAllHvAlarms()">Reset Crate Interlock</button>';
        """

# 3. Modern DFP Panel HTML
modern_dfp_html = """} else if (chartType === 'dfp_panel') {
        bodyContent = `
            <div class="modern-dfp-wrap" id="tdaq-console-${viewId}">
                <!-- Beam & Spill Banner -->
                <div class="dfp-beam-banner">
                    <div class="dfp-beam-title">
                        <div class="dfp-beam-pulse"></div>
                        <span style="font-size:15px; font-weight:bold; color:#f8fafc;">PS T9 Secondary Hadron Beam & TDAQ Data Flow</span>
                        <span style="background:rgba(16,185,129,0.2); color:#10b981; border:1px solid #10b981; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:600;">BEAM SPILL ACTIVE</span>
                    </div>
                    <div class="dfp-beam-metrics">
                        <div class="dfp-metric-chip"><span>Momentum:</span> <b>10.0 GeV/c</b></div>
                        <div class="dfp-metric-chip"><span>Flux / Spill:</span> <b id="dfp-flux">1.25 × 10⁵</b></div>
                        <div class="dfp-metric-chip"><span>Spill Cycle:</span> <b id="dfp-spill-timer">3.4s / 4.8s</b></div>
                        <div class="dfp-metric-chip"><span>Gate:</span> <b>± 10.0 ns</b></div>
                    </div>
                </div>
                
                <!-- Live Segment Rates Grid -->
                <div class="dfp-rates-grid">
                    <div class="dfp-rate-card trig">
                        <div class="dfp-rate-lbl">Trigger Rate (S1 ∧ S2)</div>
                        <div class="dfp-rate-val" id="dfp-rate-trig" style="color:#a855f7;">14.28 kHz</div>
                        <div class="dfp-rate-sub">Deadtime: <span style="color:#10b981;">0.04%</span> | S1: 14.8k, S2: 14.3k</div>
                    </div>
                    <div class="dfp-rate-card track">
                        <div class="dfp-rate-lbl">Tracking Hit Rate (DWC + TPX3)</div>
                        <div class="dfp-rate-val" id="dfp-rate-track" style="color:#10b981;">12.14 kHz</div>
                        <div class="dfp-rate-sub">DWC Tracks: 12.1k/s | TPX3 Clust: 9.8k/s</div>
                    </div>
                    <div class="dfp-rate-card calo">
                        <div class="dfp-rate-lbl">Calorimeter Stream Rate</div>
                        <div class="dfp-rate-val" id="dfp-rate-calo" style="color:#f59e0b;">11.85 kHz</div>
                        <div class="dfp-rate-sub">16ch ADC Matrix | Mean E: 2.4 GeV</div>
                    </div>
                    <div class="dfp-rate-card daq">
                        <div class="dfp-rate-lbl">HDF5 & Kafka Throughput</div>
                        <div class="dfp-rate-val" id="dfp-rate-daq" style="color:#ec4899;">18.42 MB/s</div>
                        <div class="dfp-rate-sub">Kafka Ingest: 9092 | Builder: 1.8ms</div>
                    </div>
                </div>
                
                <!-- Synoptic Beamline Flow -->
                <div class="dfp-flow-section">
                    <div class="dfp-flow-title">Beamline Hardware & Telemetry Pipeline</div>
                    <div class="dfp-flow-chain">
                        <div class="dfp-node active">
                            <span class="dfp-node-name">T9 Beam Target</span>
                            <span class="dfp-node-rate">10 GeV/c Hadron</span>
                        </div>
                        <div class="dfp-arrow">➔</div>
                        <div class="dfp-node active">
                            <span class="dfp-node-name">S1/S2 Scintillators</span>
                            <span class="dfp-node-rate" id="pipe-s1">14.2 kHz Coinc</span>
                        </div>
                        <div class="dfp-arrow">➔</div>
                        <div class="dfp-node active">
                            <span class="dfp-node-name">DWC & Timepix3</span>
                            <span class="dfp-node-rate" id="pipe-track">Tracking OK</span>
                        </div>
                        <div class="dfp-arrow">➔</div>
                        <div class="dfp-node active">
                            <span class="dfp-node-name">Gas Cherenkov</span>
                            <span class="dfp-node-rate">2.45 bar CO2</span>
                        </div>
                        <div class="dfp-arrow">➔</div>
                        <div class="dfp-node active">
                            <span class="dfp-node-name">4×4 Lead Glass</span>
                            <span class="dfp-node-rate" id="pipe-calo">16 PMTs Active</span>
                        </div>
                        <div class="dfp-arrow">➔</div>
                        <div class="dfp-node active" style="border-color:#38bdf8;">
                            <span class="dfp-node-name">Kafka Broker</span>
                            <span class="dfp-node-rate" style="color:#38bdf8;">Topic: bl4s_events</span>
                        </div>
                        <div class="dfp-arrow">➔</div>
                        <div class="dfp-node active" style="border-color:#ec4899;">
                            <span class="dfp-node-name">HDF5 Data Writer</span>
                            <span class="dfp-node-rate" style="color:#ec4899;">run_004829.h5</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        footerButtons = ' ';
        """

# Replace GECO and DFP blocks
body_pattern = re.compile(r'} else if \(chartType === \'geco_panel\'\) \{.*?} else if \(chartType === \'live_event_feed\'\) \{', re.DOTALL)
html = body_pattern.sub(modern_geco_html + "\n" + modern_dfp_html + "\n        } else if (chartType === 'live_event_feed') {", html)

# 4. Add Helper Functions for Modern HV and DFP
helper_js = """
// ===== MODERN CAEN HV & DFP ENGINE =====
const hvChannelData = [
    // Calorimeter 4x4 PMTs
    { id: 'CAL_00', slot: '00.00', name: 'CAL_00 (Ch 0)', group: 'calo', desc: 'Calo PMT [0,0]', v0: 1350.0, vmon: 1349.8, imon: 412.5, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_01', slot: '00.01', name: 'CAL_01 (Ch 1)', group: 'calo', desc: 'Calo PMT [0,1]', v0: 1350.0, vmon: 1350.2, imon: 415.2, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_02', slot: '00.02', name: 'CAL_02 (Ch 2)', group: 'calo', desc: 'Calo PMT [0,2]', v0: 1380.0, vmon: 1379.7, imon: 422.0, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_03', slot: '00.03', name: 'CAL_03 (Ch 3)', group: 'calo', desc: 'Calo PMT [0,3]', v0: 1380.0, vmon: 1380.1, imon: 419.8, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_04', slot: '00.04', name: 'CAL_04 (Ch 4)', group: 'calo', desc: 'Calo PMT [1,0]', v0: 1420.0, vmon: 1420.4, imon: 432.1, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_05', slot: '00.05', name: 'CAL_05 (Ch 5)', group: 'calo', desc: 'Calo PMT [1,1]', v0: 1420.0, vmon: 1419.9, imon: 430.5, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_06', slot: '00.06', name: 'CAL_06 (Ch 6)', group: 'calo', desc: 'Calo PMT [1,2]', v0: 1450.0, vmon: 1450.3, imon: 438.4, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_07', slot: '00.07', name: 'CAL_07 (Ch 7)', group: 'calo', desc: 'Calo PMT [1,3]', v0: 1450.0, vmon: 1449.6, imon: 436.2, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_08', slot: '01.00', name: 'CAL_08 (Ch 8)', group: 'calo', desc: 'Calo PMT [2,0]', v0: 1460.0, vmon: 1459.8, imon: 441.0, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_09', slot: '01.01', name: 'CAL_09 (Ch 9)', group: 'calo', desc: 'Calo PMT [2,1]', v0: 1460.0, vmon: 1460.5, imon: 442.8, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_10', slot: '01.02', name: 'CAL_10 (Ch 10)', group: 'calo', desc: 'Calo PMT [2,2]', v0: 1480.0, vmon: 1479.6, imon: 448.2, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_11', slot: '01.03', name: 'CAL_11 (Ch 11)', group: 'calo', desc: 'Calo PMT [2,3]', v0: 1480.0, vmon: 1480.2, imon: 447.5, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_12', slot: '01.04', name: 'CAL_12 (Ch 12)', group: 'calo', desc: 'Calo PMT [3,0]', v0: 1500.0, vmon: 1500.1, imon: 452.0, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_13', slot: '01.05', name: 'CAL_13 (Ch 13)', group: 'calo', desc: 'Calo PMT [3,1]', v0: 1500.0, vmon: 1499.7, imon: 450.8, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_14', slot: '01.06', name: 'CAL_14 (Ch 14)', group: 'calo', desc: 'Calo PMT [3,2]', v0: 1500.0, vmon: 1500.4, imon: 453.5, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    { id: 'CAL_15', slot: '01.07', name: 'CAL_15 (Ch 15)', group: 'calo', desc: 'Calo PMT [3,3]', v0: 1500.0, vmon: 1499.9, imon: 451.9, ilim: 500.0, rup: 250, on: true, status: 'ON' },
    
    // Scintillators & Trigger
    { id: 'SCINT_S1', slot: '02.00', name: 'SCINT_S1', group: 'scint', desc: 'Upstream Trigger Scintillator', v0: 1750.0, vmon: 1750.2, imon: 520.4, ilim: 800.0, rup: 250, on: true, status: 'ON' },
    { id: 'SCINT_S2', slot: '02.01', name: 'SCINT_S2', group: 'scint', desc: 'Downstream Trigger Scintillator', v0: 1800.0, vmon: 1799.8, imon: 540.1, ilim: 800.0, rup: 250, on: true, status: 'ON' },
    { id: 'VETO_PMT', slot: '02.02', name: 'VETO_COUNTER', group: 'scint', desc: 'Anti-Coincidence Charged Veto', v0: 1650.0, vmon: 1650.0, imon: 480.0, ilim: 700.0, rup: 250, on: true, status: 'ON' },
    
    // Tracking & Cherenkov
    { id: 'CHERENKOV_PMT', slot: '03.00', name: 'CHERENKOV_PMT', group: 'tracking', desc: 'Gas Cherenkov Detector PMT', v0: 2100.0, vmon: 2099.6, imon: 310.2, ilim: 600.0, rup: 250, on: true, status: 'ON' },
    { id: 'DWC_ANODE', slot: '03.01', name: 'DWC_ANODE', group: 'tracking', desc: 'Delay Wire Chamber Anode Wire', v0: 2650.0, vmon: 2649.9, imon: 24.5, ilim: 100.0, rup: 250, on: true, status: 'ON' },
    { id: 'TIMEPIX_BIAS', slot: '03.02', name: 'TIMEPIX_BIAS', group: 'tracking', desc: 'Timepix3 Silicon Sensor Bias', v0: -50.0, vmon: -50.0, imon: 1.8, ilim: 20.0, rup: 50, on: true, status: 'ON' }
];

let currentHvFilter = 'all';

function generateHvChannelRows() {
    return hvChannelData.map(ch => {
        const isHidden = (currentHvFilter !== 'all' && ch.group !== currentHvFilter) ? 'style="display:none;"' : '';
        const statusClass = ch.on ? 'hv-status-on' : 'hv-status-off';
        const statusText = ch.on ? '● ON (STABLE)' : '○ STANDBY';
        return `
            <tr id="row-${ch.id}" class="hv-ch-row" data-group="${ch.group}" ${isHidden}>
                <td style="color:#64748b;">${ch.slot}</td>
                <td>
                    <div class="modern-hv-ch-name">
                        <span>${ch.name}</span>
                    </div>
                </td>
                <td><span class="modern-hv-detector-tag">${ch.desc}</span></td>
                <td>
                    <label class="hv-switch">
                        <input type="checkbox" id="sw-${ch.id}" ${ch.on ? 'checked' : ''} onchange="toggleHvChannel('${ch.id}', this.checked)">
                        <span class="hv-slider"></span>
                    </label>
                </td>
                <td><span class="hv-status-pill ${statusClass}" id="st-${ch.id}">${statusText}</span></td>
                <td style="text-align:right;">
                    <input type="number" class="hv-input-vset" id="v0-${ch.id}" value="${ch.v0}" onchange="setHvTarget('${ch.id}', this.value)">
                </td>
                <td style="text-align:right; font-weight:bold; color:#38bdf8;" id="vmon-${ch.id}">${ch.vmon.toFixed(1)} V</td>
                <td style="text-align:right; color:#10b981;" id="imon-${ch.id}">${ch.imon.toFixed(1)} µA</td>
                <td style="text-align:right; color:#94a3b8;">${ch.ilim.toFixed(0)} µA</td>
                <td style="text-align:right; color:#64748b;">${ch.rup} V/s</td>
            </tr>
        `;
    }).join('');
}

function filterHvTable(group) {
    currentHvFilter = group;
    document.querySelectorAll('.modern-hv-tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    document.querySelectorAll('.hv-ch-row').forEach(row => {
        const rowGroup = row.getAttribute('data-group');
        if (group === 'all' || rowGroup === group) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

function toggleHvChannel(chId, state) {
    const ch = hvChannelData.find(c => c.id === chId);
    if (!ch) return;
    ch.on = state;
    const stEl = document.getElementById(`st-${chId}`);
    if (stEl) {
        stEl.className = `hv-status-pill ${state ? 'hv-status-on' : 'hv-status-off'}`;
        stEl.textContent = state ? '● RAMPING UP' : '○ RAMPING DOWN';
        setTimeout(() => {
            if (stEl) stEl.textContent = state ? '● ON (STABLE)' : '○ STANDBY';
        }, 1200);
    }
}

function setHvTarget(chId, newV0) {
    const ch = hvChannelData.find(c => c.id === chId);
    if (!ch) return;
    ch.v0 = parseFloat(newV0);
}

function setAllHvChannels(state) {
    hvChannelData.forEach(ch => {
        ch.on = state;
        const sw = document.getElementById(`sw-${ch.id}`);
        if (sw) sw.checked = state;
        const st = document.getElementById(`st-${ch.id}`);
        if (st) {
            st.className = `hv-status-pill ${state ? 'hv-status-on' : 'hv-status-off'}`;
            st.textContent = state ? '● ON (STABLE)' : '○ STANDBY';
        }
    });
}

function resetAllHvAlarms() {
    alert("All CAEN Crate Alarms & Interlock loops cleared. All channels normal.");
}

// Telemetry & Ripple Update Loop
setInterval(() => {
    hvChannelData.forEach(ch => {
        if (ch.on) {
            // Small realistic micro-jitter
            const jitter = (Math.random() - 0.5) * 0.4;
            ch.vmon = ch.v0 + jitter;
            ch.imon = (ch.v0 / 3.4) + (Math.random() - 0.5) * 1.5;
            if (ch.imon < 0) ch.imon = 1.2;
        } else {
            ch.vmon = Math.max(0, ch.vmon * 0.7);
            ch.imon = Math.max(0, ch.imon * 0.6);
        }
        
        const vEl = document.getElementById(`vmon-${ch.id}`);
        if (vEl) vEl.textContent = `${ch.vmon.toFixed(1)} V`;
        const iEl = document.getElementById(`imon-${ch.id}`);
        if (iEl) iEl.textContent = `${ch.imon.toFixed(1)} µA`;
    });
    
    // Live DFP Spill / Rate Updates
    const fluxEl = document.getElementById('dfp-flux');
    if (fluxEl) fluxEl.textContent = `${(1.2 + Math.random() * 0.1).toFixed(2)} × 10⁵`;
    const rTrig = document.getElementById('dfp-rate-trig');
    if (rTrig) rTrig.textContent = `${(14.0 + Math.random() * 0.6).toFixed(2)} kHz`;
    const rTrack = document.getElementById('dfp-rate-track');
    if (rTrack) rTrack.textContent = `${(12.0 + Math.random() * 0.4).toFixed(2)} kHz`;
    const rCalo = document.getElementById('dfp-rate-calo');
    if (rCalo) rCalo.textContent = `${(11.7 + Math.random() * 0.5).toFixed(2)} kHz`;
    const rDaq = document.getElementById('dfp-rate-daq');
    if (rDaq) rDaq.textContent = `${(18.2 + Math.random() * 0.5).toFixed(2)} MB/s`;
}, 1000);
"""

# Append helper_js before the last </script>
last_script_idx = html.rfind("</script>")
if last_script_idx != -1:
    html = html[:last_script_idx] + helper_js + "\n" + html[last_script_idx:]

with open("bl4s_event_explorer.html", "w") as f:
    f.write(html)
print("Updated successfully!")
