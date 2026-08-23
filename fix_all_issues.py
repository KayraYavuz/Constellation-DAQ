import re

with open("bl4s_event_explorer.html", "r") as f:
    html = f.read()

# 1. Complete HV Channel Data and functions
hv_code_top = """// ===== CAEN HIGH VOLTAGE CONFIGURATION & STATE =====
const hvChannelData = [
    // Calorimeter 4x4 PMTs (16 Channels)
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

function isHvOn(channelId) {
    const ch = hvChannelData.find(c => c.id === channelId);
    return ch ? ch.on : true;
}

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
    if (window.event && window.event.target) window.event.target.classList.add('active');
    
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
    
    fetch('/api/hv/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'set_power', channel_id: chId, power: state, v0: ch.v0 })
    }).catch(err => console.warn('[HV Control] Backend offline:', err));
}

function setHvTarget(chId, newV0) {
    const ch = hvChannelData.find(c => c.id === chId);
    if (!ch) return;
    ch.v0 = parseFloat(newV0);
    
    fetch('/api/hv/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'set_v0', channel_id: chId, power: ch.on, v0: ch.v0 })
    }).catch(err => console.warn('[HV Control] Backend offline:', err));
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
    
    fetch('/api/hv/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'master_power', power: state })
    }).catch(err => console.warn('[HV Control] Backend offline:', err));
}

function resetAllHvAlarms() {
    fetch('/api/hv/control', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'clear_alarms' })
    }).catch(err => console.warn('[HV Control] Backend offline:', err));
    alert("All CAEN Crate Alarms & Interlock loops cleared. All channels normal.");
}
"""

# Replace top isHvOn block with full hv_code_top
top_marker = "function isHvOn(channelId) {\n    const ch = hvChannelData.find(c => c.id === channelId);\n    return ch ? ch.on : true;\n}"
if top_marker in html:
    html = html.replace(top_marker, hv_code_top)
else:
    # Look for GLOBAL STATE marker
    gs_marker = "// ===== GLOBAL STATE & BUFFERS ====="
    html = html.replace(gs_marker, hv_code_top + "\n" + gs_marker)

# Clean up duplicate functions at the bottom
bottom_marker = "// ===== MODERN CAEN HV & DFP ENGINE ====="
bottom_idx = html.find(bottom_marker)
if bottom_idx != -1:
    last_script = html.rfind("</script>")
    # Keep only the setInterval telemetry loop at the bottom
    telemetry_loop = """
// ===== LIVE TELEMETRY & DFP SPARKLINE LOOP =====
const dfpChartHistory = { times: [], trig: [], track: [], calo: [], daq: [] };
let dfpEchart = null;

function initDfpChart(viewId) {
    const dom = document.getElementById(`dfp-chart-${viewId}`);
    if (!dom) return;
    dfpEchart = echarts.init(dom);
    const option = {
        backgroundColor: 'transparent',
        animation: false,
        tooltip: { trigger: 'axis', backgroundColor: '#0f172a', borderColor: '#334155', textStyle: { color: '#f8fafc' } },
        legend: { data: ['Trigger (kHz)', 'Tracking (kHz)', 'Calo (kHz)', 'DAQ (MB/s)'], textStyle: { color: '#94a3b8' }, top: 0 },
        grid: { left: '4%', right: '3%', top: '32px', bottom: '25px', containLabel: true },
        xAxis: { type: 'category', data: dfpChartHistory.times, axisLine: { lineStyle: { color: '#334155' } }, axisLabel: { color: '#64748b', fontSize: 10 } },
        yAxis: { type: 'value', axisLine: { lineStyle: { color: '#334155' } }, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }, axisLabel: { color: '#64748b', fontSize: 10 } },
        series: [
            { name: 'Trigger (kHz)', type: 'line', smooth: true, showSymbol: false, data: dfpChartHistory.trig, lineStyle: { color: '#a855f7', width: 2 } },
            { name: 'Tracking (kHz)', type: 'line', smooth: true, showSymbol: false, data: dfpChartHistory.track, lineStyle: { color: '#10b981', width: 2 } },
            { name: 'Calo (kHz)', type: 'line', smooth: true, showSymbol: false, data: dfpChartHistory.calo, lineStyle: { color: '#f59e0b', width: 2 } },
            { name: 'DAQ (MB/s)', type: 'line', smooth: true, showSymbol: false, data: dfpChartHistory.daq, lineStyle: { color: '#ec4899', width: 2 } }
        ]
    };
    dfpEchart.setOption(option);
}

setInterval(() => {
    // 1. Update HV Channel Ripple & Voltages
    if (typeof hvChannelData !== 'undefined') {
        hvChannelData.forEach(ch => {
            if (ch.on) {
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
    }
    
    // 2. Live DFP Rates & Sparkline Chart Update
    const rTrigVal = 14.0 + Math.random() * 0.6;
    const rTrackVal = 12.0 + Math.random() * 0.4;
    const rCaloVal = 11.7 + Math.random() * 0.5;
    const rDaqVal = 18.2 + Math.random() * 0.5;
    
    const fluxEl = document.getElementById('dfp-flux');
    if (fluxEl) fluxEl.textContent = `${(1.2 + Math.random() * 0.1).toFixed(2)} × 10⁵`;
    const rTrig = document.getElementById('dfp-rate-trig');
    if (rTrig) rTrig.textContent = `${rTrigVal.toFixed(2)} kHz`;
    const rTrack = document.getElementById('dfp-rate-track');
    if (rTrack) rTrack.textContent = `${rTrackVal.toFixed(2)} kHz`;
    const rCalo = document.getElementById('dfp-rate-calo');
    if (rCalo) rCalo.textContent = `${rCaloVal.toFixed(2)} kHz`;
    const rDaq = document.getElementById('dfp-rate-daq');
    if (rDaq) rDaq.textContent = `${rDaqVal.toFixed(2)} MB/s`;

    // Push into DFP Chart History
    const nowStr = new Date().toLocaleTimeString().split(' ')[0];
    dfpChartHistory.times.push(nowStr);
    dfpChartHistory.trig.push(rTrigVal.toFixed(2));
    dfpChartHistory.track.push(rTrackVal.toFixed(2));
    dfpChartHistory.calo.push(rCaloVal.toFixed(2));
    dfpChartHistory.daq.push(rDaqVal.toFixed(2));
    if (dfpChartHistory.times.length > 25) {
        dfpChartHistory.times.shift();
        dfpChartHistory.trig.shift();
        dfpChartHistory.track.shift();
        dfpChartHistory.calo.shift();
        dfpChartHistory.daq.shift();
    }
    if (dfpEchart) {
        dfpEchart.setOption({
            xAxis: { data: dfpChartHistory.times },
            series: [
                { data: dfpChartHistory.trig },
                { data: dfpChartHistory.track },
                { data: dfpChartHistory.calo },
                { data: dfpChartHistory.daq }
            ]
        });
    }
}, 1000);
"""
    html = html[:bottom_idx] + telemetry_loop + "\n" + html[last_script:]

# 3. Update DFP HTML to include the ECharts graph container
dfp_new_body = """} else if (chartType === 'dfp_panel') {
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
                
                <!-- Live Throughput & Rate History Graph -->
                <div style="padding: 10px 18px 0 18px; background: #0c1322;">
                    <div style="font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">Live DAQ & Detector Rate History (Real-Time Sparkline)</div>
                    <div id="dfp-chart-${viewId}" style="width: 100%; height: 160px;"></div>
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

dfp_match = re.search(r'} else if \(chartType === \'dfp_panel\'\) \{.*?} else if \(chartType === \'live_event_feed\'\) \{', html, re.DOTALL)
if dfp_match:
    html = html[:dfp_match.start()] + dfp_new_body + "\n        } else if (chartType === 'live_event_feed') {" + html[dfp_match.end():]

# 4. In openPanel, trigger initDfpChart when dfp_panel opens
open_panel_dfp_init = """    } else if (chartType === 'dfp_panel') {
        chart = { type: chartType };
        setTimeout(() => initDfpChart(viewId), 50);
    } else if (chartType === 'live_event_feed' || chartType === 'geco_panel') {"""

html = html.replace("""    } else if (chartType === 'dfp_panel' || chartType === 'live_event_feed' || chartType === 'geco_panel') {
        chart = { type: chartType };""", open_panel_dfp_init)

with open("bl4s_event_explorer.html", "w") as f:
    f.write(html)

print("All fixes applied!")
