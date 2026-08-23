import re

with open('bl4s_event_explorer.html', 'r') as f:
    html = f.read()

# 1. Define generateHvChannelRows and add hvChannelData if missing
hv_data_script = """
const hvChannelData = [
    { id: 'calo-0', slot: '00', ch: '00', name: 'CALO_PMT_0', sub: 'Calorimeter', on: true, status: 'RAMP_UP', v0: 1450, vmon: 1420, imon: 0.8, ilim: 12.0, ramp: 50, type: 'calo' },
    { id: 'calo-1', slot: '00', ch: '01', name: 'CALO_PMT_1', sub: 'Calorimeter', on: true, status: 'ON', v0: 1450, vmon: 1449.8, imon: 0.85, ilim: 12.0, ramp: 50, type: 'calo' },
    { id: 'calo-2', slot: '00', ch: '02', name: 'CALO_PMT_2', sub: 'Calorimeter', on: true, status: 'ON', v0: 1450, vmon: 1450.1, imon: 0.82, ilim: 12.0, ramp: 50, type: 'calo' },
    { id: 'calo-3', slot: '00', ch: '03', name: 'CALO_PMT_3', sub: 'Calorimeter', on: true, status: 'ON', v0: 1450, vmon: 1449.9, imon: 0.79, ilim: 12.0, ramp: 50, type: 'calo' },
    { id: 'scint-1', slot: '01', ch: '00', name: 'SCINT_S1', sub: 'Trigger S1', on: true, status: 'ON', v0: 1200, vmon: 1200.2, imon: 1.1, ilim: 15.0, ramp: 100, type: 'scint' },
    { id: 'scint-2', slot: '01', ch: '01', name: 'SCINT_S2', sub: 'Trigger S2', on: true, status: 'ON', v0: 1200, vmon: 1199.8, imon: 1.05, ilim: 15.0, ramp: 100, type: 'scint' },
    { id: 'cherenkov', slot: '02', ch: '00', name: 'CHERENKOV_PMT', sub: 'Gas PID', on: false, status: 'OFF', v0: 1800, vmon: 0.0, imon: 0.0, ilim: 20.0, ramp: 25, type: 'tracking' }
];

function generateHvChannelRows() {
    return hvChannelData.map(ch => {
        let statusBadge = '';
        if (ch.status === 'ON') statusBadge = '<span class="hv-stat ok">ON</span>';
        else if (ch.status === 'OFF') statusBadge = '<span class="hv-stat off">OFF</span>';
        else if (ch.status === 'RAMP_UP') statusBadge = '<span class="hv-stat ramp">RAMP UP</span>';
        else if (ch.status === 'TRIP') statusBadge = '<span class="hv-stat err">TRIPPED</span>';
        else statusBadge = '<span class="hv-stat off">'+ch.status+'</span>';

        return `
            <tr data-type="${ch.type}">
                <td>${ch.slot}.${ch.ch}</td>
                <td style="font-weight:600; color:#e2e8f0;">${ch.name}</td>
                <td style="color:#94a3b8;">${ch.sub}</td>
                <td>
                    <label class="hv-switch">
                        <input type="checkbox" ${ch.on ? 'checked' : ''} onchange="toggleHvChannel('${ch.id}', this.checked)">
                        <span class="hv-slider"></span>
                    </label>
                </td>
                <td>${statusBadge}</td>
                <td style="text-align:right; font-family:'JetBrains Mono',monospace; color:#38bdf8;">${ch.v0.toFixed(1)}</td>
                <td style="text-align:right; font-family:'JetBrains Mono',monospace;" id="vmon-${ch.id}">${ch.vmon.toFixed(1)} V</td>
                <td style="text-align:right; font-family:'JetBrains Mono',monospace; color:#10b981;" id="imon-${ch.id}">${ch.imon.toFixed(1)} µA</td>
                <td style="text-align:right; font-family:'JetBrains Mono',monospace; color:#94a3b8;">${ch.ilim.toFixed(1)}</td>
                <td style="text-align:right; font-family:'JetBrains Mono',monospace; color:#94a3b8;">${ch.ramp}</td>
            </tr>
        `;
    }).join('');
}

function filterHvTable(type) {
    document.querySelectorAll('.modern-hv-tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    
    document.querySelectorAll('#hvChannelsTable tbody tr').forEach(row => {
        if (type === 'all' || row.dataset.type === type) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}
function toggleHvChannel(id, isOn) {
    const ch = hvChannelData.find(c => c.id === id);
    if(ch) ch.on = isOn;
    fetch('/api/hv/control', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ action: 'set_power', channel_id: id, power: isOn })
    }).catch(e => console.error(e));
}
function setAllHvChannels(isOn) {
    hvChannelData.forEach(ch => {
        ch.on = isOn;
    });
    // Re-render table
    const tbody = document.getElementById('hvTableBody');
    if (tbody) tbody.innerHTML = generateHvChannelRows();
}
function resetAllHvAlarms() {
    hvChannelData.forEach(ch => {
        if (ch.status === 'TRIP') ch.status = 'OFF';
    });
    const tbody = document.getElementById('hvTableBody');
    if (tbody) tbody.innerHTML = generateHvChannelRows();
}
"""

if "function generateHvChannelRows" not in html:
    html = html.replace("// ===== LIVE TELEMETRY & DFP SPARKLINE LOOP =====", hv_data_script + "\n// ===== LIVE TELEMETRY & DFP SPARKLINE LOOP =====")

# 2. Fix the corrupted `openPanel` block where `bodyContent` is duplicated.
# Find the start of the duplication (line 2961)
start_idx = html.find("} else if (chartType === 'ml_pid') {", html.find("chart = initThree3D("))
if start_idx != -1:
    end_idx = html.find("chart = new Chart(document.getElementById(`chart-${viewId}`).getContext('2d')", start_idx)
    if end_idx == -1:
        # If not found, find the end of openPanel function
        end_idx = html.find("function closePanel", start_idx)
        # backtrack to the closing brace of openPanel
        end_idx = html.rfind("}", start_idx, end_idx) + 1
    
    replacement = """
    } else if (chartType === 'dfp_panel') {
        initDfpChart(viewId);
    } else if (chartType === 'ohp_view') {
        // Init OHP
    } else if (chartType === 'dqm_view') {
        // Init DQM
    }
    """
    
    html = html[:start_idx] + replacement + html[end_idx:]

with open('bl4s_event_explorer.html', 'w') as f:
    f.write(html)

print("Fixed!")
