
























        const AppConfig = {
            dashboardTitle: "Event Explorer",
            dashboardSubtitle: "Modular Beamline DAQ",
            language: "EN",
            physicsMode: "PI0_DECAY",
            allowFullscreen: true
        };
    


// ===== AMBIENT CONTROL-ROOM BACKGROUND ANIMATION =====
// A slow, low-opacity field of drifting "telemetry" points with occasional connecting
// lines — reads as a data-center / control-room ambiance behind the panels without
// competing for attention with the actual physics plots.
(function initAmbientBackground() {
    const canvas = document.getElementById('ambientBg');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let w, h, dpr;
    let particles = [];
    const PARTICLE_COUNT = 70;
    const LINK_DIST = 130;
    const palette = ['#38bdf8', '#a855f7', '#10b981', '#f59e0b'];

    function resize() {
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        w = window.innerWidth;
        h = window.innerHeight;
        canvas.width = w * dpr;
        canvas.height = h * dpr;
        canvas.style.width = w + 'px';
        canvas.style.height = h + 'px';
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    function makeParticle() {
        return {
            x: Math.random() * w,
            y: Math.random() * h,
            vx: (Math.random() - 0.5) * 0.12,
            vy: (Math.random() - 0.5) * 0.12,
            r: 0.8 + Math.random() * 1.6,
            color: palette[Math.floor(Math.random() * palette.length)],
            pulse: Math.random() * Math.PI * 2
        };
    }

    function init() {
        resize();
        particles = Array.from({ length: PARTICLE_COUNT }, makeParticle);
    }

    let t = 0;
    function frame() {
        requestAnimationFrame(frame);
        t += 0.008;
        ctx.clearRect(0, 0, w, h);

        // faint drifting grid (very subtle parallax)
        ctx.save();
        ctx.strokeStyle = 'rgba(56, 189, 248, 0.035)';
        ctx.lineWidth = 1;
        const gridSize = 64;
        const offsetX = (t * 6) % gridSize;
        const offsetY = (t * 3) % gridSize;
        for (let x = -gridSize + offsetX; x < w + gridSize; x += gridSize) {
            ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
        }
        for (let y = -gridSize + offsetY; y < h + gridSize; y += gridSize) {
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
        }
        ctx.restore();

        // update + draw particles
        for (const p of particles) {
            p.x += p.vx; p.y += p.vy;
            if (p.x < -20) p.x = w + 20; if (p.x > w + 20) p.x = -20;
            if (p.y < -20) p.y = h + 20; if (p.y > h + 20) p.y = -20;
            p.pulse += 0.02;
        }

        // connecting lines between nearby particles (sparse "network" look)
        ctx.lineWidth = 1;
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < LINK_DIST) {
                    const alpha = (1 - dist / LINK_DIST) * 0.07;
                    ctx.strokeStyle = `rgba(148, 163, 184, ${alpha})`;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }

        for (const p of particles) {
            const glow = 0.55 + 0.45 * Math.sin(p.pulse);
            ctx.beginPath();
            ctx.fillStyle = p.color;
            ctx.globalAlpha = 0.35 * glow;
            ctx.arc(p.x, p.y, p.r * 2.2, 0, Math.PI * 2);
            ctx.fill();
            ctx.globalAlpha = 0.85 * glow;
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fill();
        }
        ctx.globalAlpha = 1;
    }

    window.addEventListener('resize', resize);
    init();
    requestAnimationFrame(frame);
})();



// ===== CAEN HIGH VOLTAGE CONFIGURATION & STATE =====
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


// ===== GLOBAL STATE & BUFFERS =====
const activePanels = {};
let totalEventCount = 0;
let eventCountThisSecond = 0;
let lastSecondTimestamp = Date.now();
let isStreamPaused = false;
let currentPhysicsFilter = 'all';

const dataBuffers = {
    // Detector buffers
    calorimeter_energy: new Float64Array(16),
    calorimeter_heatmap: new Float64Array(16),
    scintillator_timing: new Float64Array(100),
    scintillator_pe: new Float64Array(60),
    timepix_hitmap: new Uint32Array(256 * 256),
    timepix_tot: new Float64Array(100),
    cherenkov_qdc: new Float64Array(100),
    trigger_rate: [],
    dwc_hitmap: new Uint32Array(256 * 256),
    dwc_delta_t: new Float64Array(100),

    // Advanced Physics & PionIST 3 pi0 -> gamma gamma Buffers
    pid_counts: { pi0: 0, proton: 0, charged_pion: 0 },
    pid_correlation: [],
    pi0_mass_hist: new Float64Array(60), // 0 to 300 MeV/c^2 in 5 MeV bins
    calorimeter_fit_buffer: new Float64Array(50),
    latest_event: {
        scintillator_pe: 0,
        timepix_x: 128,
        timepix_y: 128,
        cherenkov_qdc: 0,
        calorimeter_energy: 0,
        particle_type: 'Waiting for beam...',
        e_gamma1: 1400,
        e_gamma2: 1100,
        theta_gg: 124, // mrad
        inv_mass: 135.0, // MeV/c^2
        timestamp: Date.now()
    },
    dqm_channel_hits: new Uint32Array(16),
    dqm_total_calorimeter_events: 0,

    // ── Online Histogram Presenter (OHP) scaler counters ──
    // Cumulative event counts per logical scaler channel, sampled into a
    // rolling "counts vs time" series every tick — mirrors the classic
    // ROOT-based Online Histogram Presenter "Scaler" plugin view.
    ohp_cumulative: {
        Calorimeter: 0, CaloClus: 0, TDC: 0, TOF: 0,
        S1: 0, S2: 0, S3: 0, DWC: 0, QDC: 0,
        DWC_HV: 0, QDC_HV: 0, EVTTRG: 0, Ch11_EVTTRG: 0
    },
    ohp_series: {
        Calorimeter: [], CaloClus: [], TDC: [], TOF: [],
        S1: [], S2: [], S3: [], DWC: [], QDC: [],
        DWC_HV: [], QDC_HV: [], EVTTRG: [], Ch11_EVTTRG: []
    }
};

const OHP_MAX_POINTS = 120;

const CALIB_PEDESTAL = 100.0;
const CALIB_GAIN = 0.085;

// ===== SOCKET.IO =====
const socket = io(window.location.origin);

socket.on('connect', () => {
    document.getElementById('statusDot').className = 'status-dot';
    document.getElementById('statusText').textContent = 'Connected to Kafka Stream';
});

socket.on('disconnect', () => {
    document.getElementById('statusDot').className = 'status-dot disconnected';
    document.getElementById('statusText').textContent = 'Disconnected';
});

socket.on('event_batch', (data) => {
    if (isStreamPaused) return;

    const { satellite, events } = data;
    eventCountThisSecond += events.length;
    totalEventCount += events.length;

    for (const event of events) {
        routeEvent(event);
    }
});

// ===== EVENT ROUTING & PIONIST 3 RECONSTRUCTION =====
function routeEvent(event, isReplay = false) {
    if (!isReplay) {
        recordLiveEvent(event);
    }
    const sat = event.sat;

    // ── OHP scaler counters: bump the relevant channel(s) for every event ──
    const cum = dataBuffers.ohp_cumulative;
    if (sat === 'Calorimeter') { cum.Calorimeter++; cum.CaloClus++; cum.TOF++; cum.Ch11_EVTTRG++; }
    else if (sat === 'Scintillator') { cum.S1++; cum.S2++; cum.TDC++; }
    else if (sat === 'DWC') { cum.DWC++; cum.DWC_HV++; }
    else if (sat === 'Cherenkov') { cum.QDC++; cum.QDC_HV++; cum.S3++; }
    else if (sat === 'Trigger') { cum.EVTTRG++; }

    if (sat === 'MachineLearningPID') {
        dataBuffers.ml_pid = event;
    } else if (sat === 'SlowControl') {
        dataBuffers.slow_control = event;
        const hv1 = document.getElementById('sc-hv1'); if (hv1 && event.pmt_hv_v) hv1.textContent = `${event.pmt_hv_v[0]} V`;
        const hv2 = document.getElementById('sc-hv2'); if (hv2 && event.pmt_hv_v) hv2.textContent = `${event.pmt_hv_v[1]} V`;
        const hv3 = document.getElementById('sc-hv3'); if (hv3 && event.pmt_hv_v) hv3.textContent = `${event.pmt_hv_v[2]} V`;
        const chP = document.getElementById('sc-ch-p'); if (chP) chP.textContent = `${event.cherenkov_pressure_bar} bar`;
        const tpxT = document.getElementById('sc-tpx-t'); if (tpxT) tpxT.textContent = `${event.timepix_temp_c} °C`;
        const ambT = document.getElementById('sc-amb-t'); if (ambT) ambT.textContent = `${event.ambient_temp_c} °C`;
    } else if (sat === 'CoincidenceBuilder') {
        dataBuffers.coincidence.efficiency_pct = event.coincidence_efficiency_pct;
        dataBuffers.coincidence.rejection_pct = event.rejection_rate_pct;
        dataBuffers.coincidence.total_built = event.total_built;
        const eff = document.getElementById('coinc-eff'); if (eff) eff.textContent = `${event.coincidence_efficiency_pct}%`;
        const rej = document.getElementById('coinc-rej'); if (rej) rej.textContent = `${event.rejection_rate_pct}%`;
        const tot = document.getElementById('coinc-total'); if (tot) tot.textContent = `${event.total_built}`;
        
        const dt = event.delta_t_calo || 0;
        const bin = Math.min(49, Math.max(0, Math.floor((dt + 25) / 1.0)));
        dataBuffers.coincidence.delta_t_hist[bin]++;
    } else if (sat === 'Calorimeter') {
        const ch = event.ch;
        const chId = 'CAL_' + String(ch).padStart(2, '0');
        // Check if High Voltage is ON for this specific PMT channel
        if (!isHvOn(chId)) {
            // PMT High Voltage is OFF -> Zero light amplification, no signal registered!
            return;
        }
        if (ch >= 0 && ch < 16) {
            dataBuffers.calorimeter_energy[ch] += event.energy;
            dataBuffers.calorimeter_heatmap[ch] += event.energy;
            dataBuffers.dqm_channel_hits[ch]++;
            dataBuffers.dqm_total_calorimeter_events++;

            const calibE = Math.max(0, (event.energy - CALIB_PEDESTAL) * CALIB_GAIN);
            const calibBin = Math.min(49, Math.floor(calibE / 100));
            dataBuffers.calorimeter_fit_buffer[calibBin]++;
            dataBuffers.latest_event.calorimeter_energy = event.energy;

            // Invariant Mass calculation for pi0 -> gamma gamma
            if (ch === 15) { // At end of 16-channel batch
                reconstructPi0Event();
            }
        }
    } else if (sat === 'Scintillator') {
        // If trigger scintillators are OFF, coincidence triggers do not fire
        if (!isHvOn('SCINT_S1') || !isHvOn('SCINT_S2')) {
            return;
        }
        const timeBin = Math.floor(event.time);
        if (timeBin >= 0 && timeBin < 100) {
            dataBuffers.scintillator_timing[timeBin]++;
        }
        const peBin = event.n_pe;
        if (peBin >= 0 && peBin < 60) {
            dataBuffers.scintillator_pe[peBin]++;
        }
        dataBuffers.latest_event.scintillator_pe = event.n_pe;
    } else if (sat === 'Timepix') {
        if (!isHvOn('TIMEPIX_BIAS')) {
            return;
        }
        if (event.x >= 0 && event.x < 256 && event.y >= 0 && event.y < 256) {
            dataBuffers.timepix_hitmap[event.y * 256 + event.x]++;
            const totBin = Math.floor(event.tot / 10);
            if (totBin >= 0 && totBin < 100) {
                dataBuffers.timepix_tot[totBin]++;
            }
            dataBuffers.latest_event.timepix_x = event.x;
            dataBuffers.latest_event.timepix_y = event.y;
        }
    } else if (sat === 'Cherenkov') {
        if (!isHvOn('CHERENKOV_PMT')) {
            event.n_photons = 0;
            event.qdc = 0;
        }
        const qdcBin = Math.floor(event.qdc / 50);
        if (qdcBin >= 0 && qdcBin < 100) {
            dataBuffers.cherenkov_qdc[qdcBin]++;
        }
        dataBuffers.latest_event.cherenkov_qdc = event.qdc;
    } else if (sat === 'DWC') {
        if (!isHvOn('DWC_ANODE')) {
            return;
        }
        if (event.x >= 0 && event.x < 256 && event.y >= 0 && event.y < 256) {
            dataBuffers.dwc_hitmap[event.y * 256 + event.x]++;
            const dtBin = Math.min(99, Math.max(0, Math.floor((event.tot + 50) / 1.0)));
            dataBuffers.dwc_delta_t[dtBin]++;
        }
    } else if (sat === 'Trigger') {
        dataBuffers.trigger_rate.push({ t: Date.now(), v: event.id });
        if (dataBuffers.trigger_rate.length > 200) {
            dataBuffers.trigger_rate.shift();
        }
    }
}

function reconstructPi0Event() {
    // Check top half (Photon 1) and bottom half (Photon 2) energy in 4x4 array
    let e1 = 0, e2 = 0;
    for (let ch = 0; ch < 8; ch++) e1 += (dataBuffers.calorimeter_heatmap[ch] || 0) * CALIB_GAIN;
    for (let ch = 8; ch < 16; ch++) e2 += (dataBuffers.calorimeter_heatmap[ch] || 0) * CALIB_GAIN;

    if (e1 > 300 && e2 > 300) {
        // Dual photon candidate
        const theta = 0.12 + (Math.random() - 0.5) * 0.02; // rad (~120 mrad)
        const mass = Math.sqrt(2 * e1 * e2 * (1 - Math.cos(theta))); // MeV/c^2
        const massBin = Math.min(59, Math.floor(mass / 5));
        
        if (massBin >= 0 && massBin < 60) {
            dataBuffers.pi0_mass_hist[massBin]++;
        }

        dataBuffers.pid_counts.pi0++;
        dataBuffers.latest_event.particle_type = 'Neutral Pion (π⁰ → γγ)';
        dataBuffers.latest_event.e_gamma1 = Math.round(e1);
        dataBuffers.latest_event.e_gamma2 = Math.round(e2);
        dataBuffers.latest_event.theta_gg = Math.round(theta * 1000);
        dataBuffers.latest_event.inv_mass = mass.toFixed(1);
    } else {
        dataBuffers.pid_counts.charged_pion++;
        dataBuffers.latest_event.particle_type = 'Charged Hadron / MIP';
    }

    if (dataBuffers.latest_event.cherenkov_qdc && dataBuffers.latest_event.calorimeter_energy) {
        if (Math.random() < 0.2) {
            dataBuffers.pid_correlation.push([
                dataBuffers.latest_event.cherenkov_qdc,
                dataBuffers.latest_event.calorimeter_energy
            ]);
            if (dataBuffers.pid_correlation.length > 500) dataBuffers.pid_correlation.shift();
        }
    }
}

function toggleStreamPause() {
    isStreamPaused = !isStreamPaused;
    const btn = document.getElementById('btnPauseResume');
    const icon = document.getElementById('pauseIcon');
    const text = document.getElementById('pauseText');

    if (isStreamPaused) {
        btn.classList.add('active-pause');
        icon.textContent = '';
        text.textContent = 'Resume Stream';
    } else {
        btn.classList.remove('active-pause');
        icon.textContent = '';
        text.textContent = 'Pause Stream';
    }
}

function snapshotAllBuffers() {
    const snapshot = {
        experiment: "CERN BL4S 2026 - Team PionIST 3",
        timestamp: new Date().toISOString(),
        totalEvents: totalEventCount,
        pidCounts: dataBuffers.pid_counts,
        latestEvent: dataBuffers.latest_event,
        calorimeterEnergy: Array.from(dataBuffers.calorimeter_energy)
    };
    const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `BL4S_Event_Snapshot_${Date.now()}.json`;
    a.click();
}

function toggleSat(header) {
    header.classList.toggle('expanded');
    const children = header.nextElementSibling;
    children.classList.toggle('open');
}

function setPhysicsFilter(filterType) {
    currentPhysicsFilter = filterType;
    document.querySelectorAll('.btn-filter').forEach(b => b.classList.remove('active'));
    const activeBtn = document.getElementById(`filter-${filterType === 'all' ? 'all' : filterType === 'electron' ? 'e' : 'pi'}`);
    if (activeBtn) activeBtn.classList.add('active');
}

// ===== PANEL LIFECYCLE =====
function openPanel(viewId, satellite, title, chartType, isFullWidth = false) {
    if (activePanels[viewId]) {
        closePanel(viewId);
        return;
    }

    document.querySelectorAll(`.tree-view-item[data-view="${viewId}"]`).forEach(el => el.classList.add('active'));
    document.getElementById('emptyState').style.display = 'none';

    const panel = document.createElement('div');
    panel.className = `chart-panel ${isFullWidth ? 'full-width' : ''}`;
    panel.id = `panel-${viewId}`;
    
    let bodyContent = '';
    let footerButtons = `<button class="btn-action" onclick="resetBuffer('${viewId}')">Reset</button>`;

    if (chartType === 'heatmap2d' || chartType === 'heatmap2d_dwc') {
        bodyContent = `<div class="heatmap-wrap" style="position:relative; width:100%; height:100%; display:flex; align-items:center; justify-content:center;">
            <canvas id="canvas-${viewId}"></canvas>
            <div id="hm-tooltip-${viewId}" style="display:none; position:absolute; z-index:20; pointer-events:none; background:rgba(15,17,26,0.92); border:1px solid rgba(56,189,248,0.4); color:#f8fafc; font-family:'JetBrains Mono',monospace; font-size:11px; padding:4px 8px; border-radius:6px; box-shadow:0 8px 24px rgba(0,0,0,0.6); white-space:nowrap;"></div>
        </div>`;
    } else if (chartType === 'three_3d') {
        bodyContent = `
            <div id="three-container-${viewId}" class="three-container">
                <!-- Experiment Mission Header Banner -->
                <div class="three-mission-banner">
                    <div class="mission-title">
                        <span></span>
                        <span>CERN BL4S Modular DAQ Spectrometer</span>
                    </div>
                    <div class="mission-desc">
                        <strong>Experiment Goal:</strong> Neutral Pion (π⁰) production in proton-nucleus collisions ($p + A \to \pi^0 + X$) and dual-photon invariant mass reconstruction ($\pi^0 \to \gamma\gamma$) with Lead Glass Calorimetry.
                    </div>
                </div>

                <!-- Live Beam & Pi0 Invariant Mass Reconstruction HUD -->
                <div class="three-diagnostics-panel">
                    <div class="diag-header">
                        <span class="pulse-dot"></span>
                        <span>LIVE π⁰ → γγ KINEMATICS RECONSTRUCTION</span>
                    </div>
                    <div class="diag-grid">
                        <div class="diag-stat">
                            <span class="diag-lbl">Photon 1 Energy (E_γ1):</span>
                            <span class="diag-val text-amber" id="diag-e1">1420 MeV</span>
                        </div>
                        <div class="diag-stat">
                            <span class="diag-lbl">Photon 2 Energy (E_γ2):</span>
                            <span class="diag-val text-amber" id="diag-e2">1180 MeV</span>
                        </div>
                        <div class="diag-stat">
                            <span class="diag-lbl">Opening Angle (θ_γγ):</span>
                            <span class="diag-val" id="diag-theta">124 mrad</span>
                        </div>
                        <div class="diag-stat">
                            <span class="diag-lbl">Invariant Mass M(γγ):</span>
                            <span class="diag-val text-green" id="diag-invmass">135.2 MeV/c² [π⁰ PEAK]</span>
                        </div>
                    </div>
                </div>

                <!-- Controls Top-Right -->
                <div class="three-controls-topright">
                    <div class="filter-group">
                        <span class="filter-label">Filter:</span>
                        <button class="btn-filter active" id="filter-all" onclick="setPhysicsFilter('all')">All</button>
                        <button class="btn-filter" id="filter-e" onclick="setPhysicsFilter('electron')">π⁰ Events</button>
                        <button class="btn-filter" id="filter-pi" onclick="setPhysicsFilter('pion')">Charged MIP</button>
                    </div>
                    <div class="three-camera-presets">
                        <button class="btn-cam" onclick="set3DCameraPreset('iso')">🔭 Orbit</button>
                        <button class="btn-cam" onclick="set3DCameraPreset('top')"> Top</button>
                        <button class="btn-cam" onclick="set3DCameraPreset('side')">📏 Side</button>
                        <button class="btn-cam" onclick="set3DCameraPreset('front')"> Front</button>
                        <button class="btn-cam highlight" id="btn-walkthrough" onclick="toggleWalkthroughTour()">🚶 Walkthrough Tour</button>
                        <button class="btn-cam" id="btn-freeroam" onclick="toggleFreeRoamMode()">✈️ Free Roam</button>
                        <button class="btn-cam" style="background:rgba(16,185,129,0.25);border-color:#10b981;color:#10b981;" onclick="toggle3DFullscreen()">⛶ Fullscreen</button>
                        <button class="btn-cam" style="background:rgba(251,191,36,0.2);border-color:#f59e0b;color:#f59e0b;" onclick="start3DTutorial()"> Guide</button>
                    </div>
                </div>

                <!-- Interactive Detector Cards Bar (6 Modular Stations) -->
                <div class="three-detector-cards" style="grid-template-columns: repeat(6, 1fr);">
                    <div class="det-card" onclick="focusOnDetector('scint')">
                        <div class="det-name" style="color: #10b981;">1. Scintillators</div>
                        <div class="det-function">S1/S2 Trigger & ToF</div>
                    </div>
                    <div class="det-card" onclick="focusOnDetector('dwc')">
                        <div class="det-name" style="color: #38bdf8;">2. DWC Chamber</div>
                        <div class="det-function">Delay Wire Tracking</div>
                    </div>
                    <div class="det-card" onclick="focusOnDetector('timepix')">
                        <div class="det-name" style="color: #f59e0b;">3. Timepix3</div>
                        <div class="det-function">Pixel Tracker (55µm)</div>
                    </div>
                    <div class="det-card" onclick="focusOnDetector('target')">
                        <div class="det-name" style="color: #c084fc;">4. Target Station</div>
                        <div class="det-function">Interaction Vertex</div>
                    </div>
                    <div class="det-card" onclick="focusOnDetector('cherenkov')">
                        <div class="det-name" style="color: #06b6d4;">5. Cherenkov</div>
                        <div class="det-function">Gas Radiator PID</div>
                    </div>
                    <div class="det-card" onclick="focusOnDetector('calo')">
                        <div class="det-name" style="color: #60a5fa;">6. Calorimeter</div>
                        <div class="det-function">Lead Glass Array</div>
                    </div>
                </div>

                <div class="three-overlay-hint" id="three-hint">🎮 [W][A][S][D] Walk/Fly | [Q][E] Elevate | [Shift] Fast | Mouse: Rotate & Pan | Click Cards to Inspect</div>
            </div>
        `;
        footerButtons = `
            <button class="btn-action btn-green" onclick="reset3DCamera('${viewId}')">Reset Camera</button>
            <button class="btn-action" onclick="resetBuffer('${viewId}')">Reset Buffer</button>
        `;
    
    } else if (chartType === 'ml_pid') {
        bodyContent = `
            <div class="ml-pid-container">
                <div class="ml-card">
                    <div class="ml-prediction-banner">
                        <div class="ml-pred-label">Real-Time AI PID Classification</div>
                        <div class="ml-pred-value" id="ml-pred-text">✨ Neutral Pion (π⁰ → γγ)</div>
                        <div class="ml-confidence-pill" id="ml-conf-pill">Confidence: 98.4%</div>
                    </div>
                    <div style="margin-top:12px; font-family:'JetBrains Mono',monospace; font-size:11px; color:#94a3b8; display:flex; justify-content:space-between;">
                        <span>Inference Latency: <strong id="ml-latency" style="color:#38bdf8;">4.2 µs</strong></span>
                        <span>Model: <strong style="color:#a855f7;">RandomForest_v2.4</strong></span>
                    </div>
                    <div id="chart-ml-probs-${viewId}" style="flex:1; width:100%; min-height:160px; margin-top:8px;"></div>
                </div>
                <div class="ml-card">
                    <div style="font-family:'JetBrains Mono',monospace; font-size:11px; font-weight:700; color:#38bdf8; margin-bottom:4px;">
                        Multi-Detector Feature Importance Radar
                    </div>
                    <div id="chart-ml-radar-${viewId}" style="flex:1; width:100%; min-height:220px;"></div>
                </div>
            </div>
        `;
        footerButtons = `<button class="btn-action btn-green" onclick="resetBuffer('${viewId}')">Reset AI Buffer</button>`;
    } else if (chartType === 'slow_control') {
        bodyContent = `
            <div class="slowctrl-grid" id="slowctrl-grid-container">
                <div class="slowctrl-card">
                    <div class="slowctrl-title"><span>PMT 1 High Voltage</span><span style="color:#10b981;">● NORMAL</span></div>
                    <div class="slowctrl-val" id="sc-hv1">1420.4 V</div>
                    <div class="slowctrl-meta">Current: 1.12 µA | Limit: 1600 V</div>
                </div>
                <div class="slowctrl-card">
                    <div class="slowctrl-title"><span>PMT 2 High Voltage</span><span style="color:#10b981;">● NORMAL</span></div>
                    <div class="slowctrl-val" id="sc-hv2">1418.1 V</div>
                    <div class="slowctrl-meta">Current: 1.15 µA | Limit: 1600 V</div>
                </div>
                <div class="slowctrl-card">
                    <div class="slowctrl-title"><span>PMT 3 High Voltage</span><span style="color:#10b981;">● NORMAL</span></div>
                    <div class="slowctrl-val" id="sc-hv3">1449.8 V</div>
                    <div class="slowctrl-meta">Current: 0.94 µA | Limit: 1600 V</div>
                </div>
                <div class="slowctrl-card">
                    <div class="slowctrl-title"><span>Gas Cherenkov Pressure</span><span style="color:#10b981;">● NORMAL</span></div>
                    <div class="slowctrl-val" id="sc-ch-p">2.451 bar</div>
                    <div class="slowctrl-meta">Gas: CO2 | Target: 2.45 bar</div>
                </div>
                <div class="slowctrl-card">
                    <div class="slowctrl-title"><span>Timepix Silicon Temp</span><span style="color:#10b981;">● NORMAL</span></div>
                    <div class="slowctrl-val" id="sc-tpx-t">18.4 °C</div>
                    <div class="slowctrl-meta">V_bias: -50.0 V | Chiller Flow: 3.2 L/m</div>
                </div>
                <div class="slowctrl-card">
                    <div class="slowctrl-title"><span>Cleanroom Environment</span><span style="color:#10b981;">● NORMAL</span></div>
                    <div class="slowctrl-val" id="sc-amb-t">21.8 °C</div>
                    <div class="slowctrl-meta">Humidity: 42.4% RH | Pressure: 1013 hPa</div>
                </div>
            </div>
        `;
        footerButtons = `<button class="btn-action" onclick="resetBuffer('${viewId}')">Refresh Telemetry</button>`;
    } else if (chartType === 'coincidence_view') {
        bodyContent = `
            <div style="padding:10px; height:100%; display:flex; flex-direction:column;">
                <div class="coinc-summary-bar">
                    <div class="coinc-stat"><span class="coinc-stat-lbl">Coincidence Window:</span><span class="coinc-stat-val" style="color:#38bdf8;">± 10.0 ns</span></div>
                    <div class="coinc-stat"><span class="coinc-stat-lbl">Efficiency:</span><span class="coinc-stat-val" id="coinc-eff">85.4%</span></div>
                    <div class="coinc-stat"><span class="coinc-stat-lbl">Background Rejection:</span><span class="coinc-stat-val" id="coinc-rej">14.6%</span></div>
                    <div class="coinc-stat"><span class="coinc-stat-lbl">Matched Events:</span><span class="coinc-stat-val" id="coinc-total" style="color:#f59e0b;">0</span></div>
                </div>
                <div id="chart-${viewId}" style="flex:1; width:100%; min-height:220px;"></div>
            </div>
        `;
        footerButtons = `<button class="btn-action btn-green" onclick="resetBuffer('${viewId}')">Clear Histogram</button>`;

                } else if (chartType === 'geco_panel') {
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
        
} else if (chartType === 'dfp_panel') {
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
        
    } else if (chartType === 'dqm_view') {
        bodyContent = `<div id="dqm-container" class="dqm-grid"></div>`;
        footerButtons = `
            <button class="btn-action btn-green" onclick="exportDqmJson()">Export DQM JSON</button>
            <button class="btn-action" onclick="downloadCsvHistograms()">Download CSV</button>
            <button class="btn-action" onclick="resetBuffer('${viewId}')">Reset</button>
        `;
    } else if (chartType === 'ohp_view') {
        bodyContent = `<div id="ohp-container" class="ohp-grid"></div>`;
        footerButtons = `
            <button class="btn-action" onclick="resetBuffer('${viewId}')">Clear All Scalers</button>
        `;
    } else {
        bodyContent = `<div id="chart-${viewId}" style="width: 100%; height: 100%;"></div>`;
    }

    panel.innerHTML = `
        <div class="panel-header">
            <div class="panel-title">
                <div class="live-dot"></div>
                ${title}
            </div>
            <button class="panel-close" onclick="closePanel('${viewId}')" title="Close">✕</button>
        </div>
        <div class="panel-body ${isFullWidth ? 'tall' : ''}">
            ${bodyContent}
        </div>
        <div class="panel-footer">
            <span id="footer-${viewId}">${(chartType === 'ohp_view' || chartType === 'run_control_console') ? 'System Active' : 'Waiting for live data...'}</span>
            <div>${footerButtons}</div>
        </div>
    `;

    document.getElementById('panelsContainer').appendChild(panel);

    let chart = null;

    if (chartType === 'heatmap2d' || chartType === 'heatmap2d_dwc') {
        chart = { type: 'heatmap2d', canvas: document.getElementById(`canvas-${viewId}`) };
        attachHeatmapHoverTooltip(chart.canvas, document.getElementById(`hm-tooltip-${viewId}`), viewId);
    } else if (chartType === 'three_3d') {
        chart = initThree3D(document.getElementById(`three-container-${viewId}`));
    
    
    } else if (chartType === 'dfp_panel') {
        initDfpChart(viewId);
    } else if (chartType === 'ohp_view') {
        // Init OHP
    } else if (chartType === 'dqm_view') {
        // Init DQM
    }
    
    activePanels[viewId] = { type: chartType, chart: chart };
    updatePanelCount();
}

function closePanel(viewId) {
    const panel = document.getElementById(`panel-${viewId}`);
    if (panel) {
        panel.style.animation = 'panelIn 0.2s ease reverse';
        setTimeout(() => {
            panel.remove();
            if (activePanels[viewId]?.chart && typeof activePanels[viewId].chart.dispose === 'function') {
                activePanels[viewId].chart.dispose();
            }
            if (activePanels[viewId]?.chart?.cleanupThree) {
                activePanels[viewId].chart.cleanupThree();
            }
            delete activePanels[viewId];
            updatePanelCount();
            if (Object.keys(activePanels).length === 0) {
                document.getElementById('emptyState').style.display = 'flex';
            }
        }, 180);
    }
    document.querySelectorAll(`.tree-view-item[data-view="${viewId}"]`).forEach(el => el.classList.remove('active'));
}

function resetBuffer(viewId) {
    if (viewId === 'timepix_hitmap') {
        dataBuffers.timepix_hitmap.fill(0);
    } else if (viewId === 'pid_overview' || viewId === 'pid_correlation') {
        dataBuffers.pid_counts = { pi0: 0, proton: 0, charged_pion: 0 };
        dataBuffers.pid_correlation.length = 0;
    } else if (viewId === 'pi0_invariant_mass') {
        dataBuffers.pi0_mass_hist.fill(0);
    } else if (viewId === 'physics_fitting') {
        dataBuffers.calorimeter_fit_buffer.fill(0);
    } else if (viewId === 'ohp_grid') {
        for (const key of Object.keys(dataBuffers.ohp_cumulative)) {
            dataBuffers.ohp_cumulative[key] = 0;
            dataBuffers.ohp_series[key].length = 0;
        }
        renderOhpGrid();
    } else if (dataBuffers[viewId] instanceof Float64Array || dataBuffers[viewId] instanceof Uint32Array) {
        dataBuffers[viewId].fill(0);
    } else if (Array.isArray(dataBuffers[viewId])) {
        dataBuffers[viewId].length = 0;
    }
}

function updatePanelCount() {
    document.getElementById('panelCount').textContent = Object.keys(activePanels).length;
}

// ===== ENHANCED ECHARTS GRAPH ENGINE =====
const chartColors = {
    calorimeter_energy: { from: '#38bdf8', to: '#0284c7', line: '#38bdf8' },
    scintillator_timing: { from: '#34d399', to: '#059669', line: '#10b981' },
    scintillator_pe: { from: '#c084fc', to: '#7c3aed', line: '#a855f7' },
    timepix_tot: { from: '#fbbf24', to: '#d97706', line: '#f59e0b' },
    cherenkov_qdc: { from: '#fb7185', to: '#e11d48', line: '#f43f5e' },
    trigger_rate: { from: '#818cf8', to: '#4338ca', line: '#6366f1' },
};

const commonTooltip = {
    trigger: 'axis',
    axisPointer: { type: 'shadow', shadowStyle: { color: 'rgba(56, 189, 248, 0.08)' } },
    backgroundColor: 'rgba(15, 17, 26, 0.92)',
    borderColor: 'rgba(56, 189, 248, 0.3)',
    borderWidth: 1,
    textStyle: { color: '#f8fafc', fontFamily: 'JetBrains Mono', fontSize: 11 },
    extraCssText: 'box-shadow: 0 8px 24px rgba(0,0,0,0.6); backdrop-filter: blur(8px); border-radius: 8px;'
};

// Shared "hover to reveal exact value above the bar" treatment — mirrors the
// crosshair/value-readout behavior of the real Online Histogram Presenter.
function barEmphasis(color) {
    return {
        focus: 'series',
        itemStyle: {
            color: color,
            shadowColor: color,
            shadowBlur: 14
        },
        label: {
            show: true,
            position: 'top',
            distance: 6,
            color: '#0f1117',
            backgroundColor: '#f8fafc',
            padding: [3, 6],
            borderRadius: 4,
            fontFamily: 'JetBrains Mono',
            fontWeight: 700,
            fontSize: 11,
            formatter: (p) => Number(p.value).toLocaleString()
        }
    };
}

function createBarChart(chart, viewId) {
    const pal = chartColors[viewId] || { from: '#38bdf8', to: '#0284c7', line: '#38bdf8' };
    const labels = Array.from({ length: 16 }, (_, i) => `Ch ${i}`);
    chart.setOption({
        backgroundColor: 'transparent',
        tooltip: commonTooltip,
        grid: { top: 20, right: 15, bottom: 25, left: 45 },
        xAxis: { type: 'category', data: labels, axisLabel: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 10 }, axisLine: { lineStyle: { color: '#334155' } } },
        yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 10 } },
        dataZoom: [{ type: 'inside', start: 0, end: 100 }],
        series: [{
            name: 'Energy',
            data: new Array(16).fill(0),
            type: 'bar',
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: pal.from },
                    { offset: 1, color: pal.to }
                ]),
                borderRadius: [4, 4, 0, 0],
                shadowColor: pal.from,
                shadowBlur: 4
            },
            emphasis: barEmphasis(pal.from),
            animationDurationUpdate: 80
        }]
    });
}

function createHistogramChart(chart, viewId) {
    const pal = chartColors[viewId] || { from: '#38bdf8', to: '#0284c7', line: '#38bdf8' };
    let binCount = 50, labelFn = (i) => `${i}`, xName = 'Bins';

    if (viewId === 'scintillator_timing') { binCount = 30; labelFn = (i) => `${i} ns`; xName = 'Time (ns)'; }
    else if (viewId === 'scintillator_pe') { binCount = 60; labelFn = (i) => `${i}`; xName = 'Photoelectrons'; }
    else if (viewId === 'timepix_tot') { binCount = 50; labelFn = (i) => `${i * 10}`; xName = 'ToT (Clock cycles)'; }
    else if (viewId === 'cherenkov_qdc') { binCount = 100; labelFn = (i) => `${i * 50}`; xName = 'QDC Integrator ADC'; }

    const labels = Array.from({ length: binCount }, (_, i) => labelFn(i));
    chart.setOption({
        backgroundColor: 'transparent',
        tooltip: commonTooltip,
        grid: { top: 20, right: 15, bottom: 25, left: 45 },
        xAxis: { type: 'category', data: labels, axisLabel: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 9 }, axisLine: { lineStyle: { color: '#334155' } } },
        yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 10 } },
        dataZoom: [{ type: 'inside', start: 0, end: 100 }],
        series: [{
            name: 'Counts',
            data: new Array(binCount).fill(0),
            type: 'bar',
            barWidth: '92%',
            itemStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: pal.from },
                    { offset: 1, color: pal.to }
                ]),
                borderRadius: [2, 2, 0, 0]
            },
            emphasis: barEmphasis(pal.from),
            animationDurationUpdate: 80
        }]
    });
}

function createTimeSeriesChart(chart, viewId) {
    chart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'axis',
            axisPointer: { type: 'cross', lineStyle: { color: 'rgba(56,189,248,0.4)' }, label: { backgroundColor: '#0f1117', fontFamily: 'JetBrains Mono' } },
            backgroundColor: 'rgba(15, 17, 26, 0.92)',
            borderColor: 'rgba(56, 189, 248, 0.3)',
            borderWidth: 1,
            textStyle: { color: '#f8fafc', fontFamily: 'JetBrains Mono', fontSize: 11 },
            extraCssText: 'box-shadow: 0 8px 24px rgba(0,0,0,0.6); backdrop-filter: blur(8px); border-radius: 8px;'
        },
        grid: { top: 20, right: 15, bottom: 25, left: 45 },
        xAxis: { type: 'category', data: [], axisLabel: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 9 }, axisLine: { lineStyle: { color: '#334155' } } },
        yAxis: { name: 'Rate (Hz)', nameTextStyle: { color: '#94a3b8', fontSize: 9 }, type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 10 } },
        series: [{
            name: 'Rate',
            data: [],
            type: 'line',
            smooth: true,
            showSymbol: true,
            symbol: 'circle',
            symbolSize: 6,
            itemStyle: { color: '#f43f5e', borderColor: '#fff', borderWidth: 1 },
            areaStyle: {
                color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                    { offset: 0, color: 'rgba(45, 212, 191, 0.55)' },
                    { offset: 1, color: 'rgba(45, 212, 191, 0.02)' }
                ])
            },
            lineStyle: { color: '#f43f5e', width: 1.5 },
            emphasis: {
                focus: 'series',
                itemStyle: { color: '#fecaca', shadowColor: '#f43f5e', shadowBlur: 12 },
                label: {
                    show: true, position: 'top', distance: 10,
                    color: '#0f1117', backgroundColor: '#f8fafc', padding: [3, 6], borderRadius: 4,
                    fontFamily: 'JetBrains Mono', fontWeight: 700, fontSize: 11,
                    formatter: (p) => `${Number(p.value).toLocaleString()} Hz`
                }
            },
            animationDurationUpdate: 0
        }]
    });
}

function createHeatmap4x4(chart, viewId) {
    chart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
            position: 'top',
            backgroundColor: 'rgba(15, 17, 26, 0.92)',
            borderColor: 'rgba(56, 189, 248, 0.4)',
            borderWidth: 1,
            textStyle: { color: '#f8fafc', fontFamily: 'JetBrains Mono', fontSize: 11 },
            formatter: (p) => `Channel (${p.data[0]}, ${p.data[1]}): <strong>${p.data[2]} MeV</strong>`
        },
        grid: { top: 10, right: 10, bottom: 10, left: 10 },
        xAxis: { type: 'category', data: ['Col 0', 'Col 1', 'Col 2', 'Col 3'], show: false },
        yAxis: { type: 'category', data: ['Row 0', 'Row 1', 'Row 2', 'Row 3'], show: false },
        visualMap: { min: 0, max: 5000, calculable: true, show: false, inRange: { color: ['#0b1120', '#1e3a8a', '#0284c7', '#38bdf8', '#fbbf24', '#f97316', '#ef4444'] } },
        series: [{
            name: 'Energy',
            type: 'heatmap',
            data: [],
            label: { show: true, color: '#fff', fontSize: 13, fontWeight: 'bold', fontFamily: 'JetBrains Mono' },
            itemStyle: { borderColor: '#060810', borderWidth: 3, borderRadius: 4 },
            emphasis: {
                itemStyle: { borderColor: '#38bdf8', borderWidth: 3, shadowColor: '#38bdf8', shadowBlur: 16 },
                label: { fontSize: 15, color: '#38bdf8' }
            },
            animation: false
        }]
    });
}


function createCoincidenceChart(chart) {
    const option = {
        tooltip: commonTooltip,
        xAxis: { type: 'category', data: Array.from({length:50}, (_,i) => i - 25), name: 'Δt (ns)', axisLabel: { color: '#64748b' } },
        yAxis: { type: 'value', name: 'Events', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } }, axisLabel: { color: '#64748b' } },
        series: [{
            type: 'bar',
            data: [],
            itemStyle: { color: new echarts.graphic.LinearGradient(0,0,0,1, [{offset:0,color:'#10b981'}, {offset:1,color:'#064e3b'}]) },
            barWidth: '80%'
        }],
        grid: { left: 40, right: 30, top: 40, bottom: 40 }
    };
    chart.setOption(option);
}

function createPidPieChart(chart) {
    chart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(15, 17, 26, 0.92)',
            borderColor: 'rgba(56, 189, 248, 0.3)',
            textStyle: { color: '#f8fafc', fontFamily: 'JetBrains Mono', fontSize: 11 }
        },
        legend: { bottom: '4%', left: 'center', textStyle: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 11 } },
        series: [{
            name: 'Particle Type',
            type: 'pie',
            radius: ['45%', '72%'],
            avoidLabelOverlap: false,
            itemStyle: { borderRadius: 8, borderColor: '#060810', borderWidth: 3 },
            data: [
                { value: 0, name: 'Neutral Pion (π⁰ → γγ)', itemStyle: { color: '#38bdf8' } },
                { value: 0, name: 'Charged Hadron / MIP', itemStyle: { color: '#f59e0b' } },
                { value: 0, name: 'Proton Beam / Background', itemStyle: { color: '#64748b' } }
            ]
        }]
    });
}

function createPidScatterChart(chart) {
    chart.setOption({
        backgroundColor: 'transparent',
        tooltip: {
            trigger: 'item',
            backgroundColor: 'rgba(15, 17, 26, 0.92)',
            borderColor: 'rgba(56, 189, 248, 0.3)',
            textStyle: { color: '#f8fafc', fontFamily: 'JetBrains Mono', fontSize: 11 },
            formatter: (p) => `Cherenkov: ${p.data[0]} ADC<br/>Calo: ${p.data[1]} ADC<br/>Type: <strong>${p.data[2]}</strong>`
        },
        grid: { top: 20, right: 20, bottom: 35, left: 60 },
        xAxis: { name: 'Cherenkov QDC', nameLocation: 'middle', nameGap: 22, nameTextStyle: { color: '#94a3b8', fontSize: 10 }, type: 'value', min: 0, max: 4500, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 9 } },
        yAxis: { name: 'Calorimeter Energy', nameLocation: 'middle', nameGap: 42, nameTextStyle: { color: '#94a3b8', fontSize: 10 }, type: 'value', min: 0, max: 65000, splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 9 } },
        dataZoom: [{ type: 'inside' }],
        series: [{ type: 'scatter', symbolSize: 6, data: [], itemStyle: { color: (param) => param.data[2] === 'electron' ? '#38bdf8' : '#f59e0b' }, animation: false }]
    });
}

function createPi0MassChart(chart) {
    const labels = Array.from({ length: 60 }, (_, i) => `${i * 5}`);
    chart.setOption({
        backgroundColor: 'transparent',
        tooltip: commonTooltip,
        grid: { top: 25, right: 20, bottom: 30, left: 55 },
        legend: { top: 5, right: 10, textStyle: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 10 } },
        xAxis: { name: 'M(γγ) [MeV/c²]', nameLocation: 'middle', nameGap: 20, nameTextStyle: { color: '#94a3b8', fontSize: 9 }, type: 'category', data: labels, axisLabel: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 9, interval: 5 } },
        yAxis: { name: 'Candidates / 5 MeV', type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 9 } },
        dataZoom: [{ type: 'inside', start: 0, end: 100 }],
        series: [
            {
                name: 'Dual Photon Mass M(γγ)',
                type: 'bar',
                data: new Array(60).fill(0),
                barWidth: '90%',
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: '#38bdf8' },
                        { offset: 1, color: '#0369a1' }
                    ]),
                    borderRadius: [3, 3, 0, 0],
                    shadowColor: '#38bdf8',
                    shadowBlur: 3
                },
                emphasis: barEmphasis('#38bdf8')
            }
        ]
    });
}

function createPhysicsFitChart(chart) {
    const labels = Array.from({ length: 50 }, (_, i) => `${i * 100}`);
    chart.setOption({
        backgroundColor: 'transparent',
        tooltip: commonTooltip,
        grid: { top: 25, right: 20, bottom: 30, left: 55 },
        legend: { top: 5, right: 10, textStyle: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 10 } },
        xAxis: { name: 'Energy (MeV)', nameLocation: 'middle', nameGap: 20, nameTextStyle: { color: '#94a3b8', fontSize: 9 }, type: 'category', data: labels, axisLabel: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 9, interval: 4 } },
        yAxis: { name: 'Counts', type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.06)' } }, axisLabel: { color: '#94a3b8', fontFamily: 'JetBrains Mono', fontSize: 9 } },
        dataZoom: [{ type: 'inside', start: 0, end: 100 }],
        series: [
            {
                name: 'Raw Data',
                type: 'bar',
                data: new Array(50).fill(0),
                barWidth: '85%',
                itemStyle: {
                    color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                        { offset: 0, color: 'rgba(56, 189, 248, 0.6)' },
                        { offset: 1, color: 'rgba(2, 132, 199, 0.2)' }
                    ]),
                    borderRadius: [2, 2, 0, 0]
                },
                emphasis: barEmphasis('#38bdf8')
            },
            {
                name: 'Gaussian Fit',
                type: 'line',
                smooth: true,
                showSymbol: false,
                data: new Array(50).fill(0),
                lineStyle: { color: '#f43f5e', width: 2.5, shadowColor: '#f43f5e', shadowBlur: 6 }
            }
        ]
    });
}

// ===== 3D THREE.JS MODULAR EVENT DISPLAY & FREE FLIGHT ENGINE =====
let globalThreeState = null;

function create3DLabel(text, subtext, color = '#38bdf8') {
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 128;
    const ctx = canvas.getContext('2d');

    ctx.fillStyle = 'rgba(15, 17, 26, 0.88)';
    ctx.strokeStyle = color;
    ctx.lineWidth = 4;
    ctx.roundRect(10, 10, 492, 108, 16);
    ctx.fill();
    ctx.stroke();

    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 30px JetBrains Mono';
    ctx.fillText(text, 24, 50);

    ctx.fillStyle = '#94a3b8';
    ctx.font = '22px Inter';
    ctx.fillText(subtext, 24, 90);

    const texture = new THREE.CanvasTexture(canvas);
    texture.minFilter = THREE.LinearFilter;
    const spriteMat = new THREE.SpriteMaterial({ map: texture, transparent: true });
    const sprite = new THREE.Sprite(spriteMat);
    sprite.scale.set(15, 3.8, 1);
    return sprite;
}

function initThree3D(container) {
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x050810);
    scene.fog = new THREE.FogExp2(0x050810, 0.0018);

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 500;

    const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 2000);
    camera.position.set(-30, 45, 110);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);

    // ── PHOTOREALISTIC POST-PROCESSING: bloom glow on hot detector elements ──
    let composer = null;
    let bloomPass = null;
    if (typeof THREE.EffectComposer === 'function' && typeof THREE.UnrealBloomPass === 'function') {
        composer = new THREE.EffectComposer(renderer);
        composer.addPass(new THREE.RenderPass(scene, camera));
        bloomPass = new THREE.UnrealBloomPass(new THREE.Vector2(width, height), 0.85, 0.55, 0.18);
        bloomPass.threshold = 0.18;
        bloomPass.strength = 0.85;
        bloomPass.radius = 0.55;
        composer.addPass(bloomPass);
    }

    let controls = null;
    if (typeof THREE.OrbitControls === 'function') {
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.06;
        controls.target.set(5, 0, 0);
        controls.autoRotate = false;
        controls.minDistance = 8;
        controls.maxDistance = 300;
        controls.enablePan = true;
        controls.zoomSpeed = 1.2;
    }

    const resizeObserver = new ResizeObserver(() => {
        if (container.clientWidth > 0 && container.clientHeight > 0) {
            camera.aspect = container.clientWidth / container.clientHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(container.clientWidth, container.clientHeight);
            if (composer) composer.setSize(container.clientWidth, container.clientHeight);
        }
    });
    resizeObserver.observe(container);

    // ═══════════════════════════════════════════════
    //  ENHANCED SCIENTIFIC LIGHTING (PBR)
    // ═══════════════════════════════════════════════
    const ambientLight = new THREE.AmbientLight(0xc7d2fe, 0.28);
    scene.add(ambientLight);

    // Hemisphere light: cool "sky" bounce from above, warm "floor" bounce from below —
    // gives metal surfaces a believable ambient occlusion/reflection gradient
    const hemiLight = new THREE.HemisphereLight(0x8fb8ff, 0x1a1408, 0.55);
    scene.add(hemiLight);

    const keyLight = new THREE.DirectionalLight(0xffffff, 1.8);
    keyLight.position.set(50, 70, 60);
    keyLight.castShadow = true;
    keyLight.shadow.mapSize.width = 2048;
    keyLight.shadow.mapSize.height = 2048;
    keyLight.shadow.camera.near = 0.5;
    keyLight.shadow.camera.far = 300;
    keyLight.shadow.camera.left = -80;
    keyLight.shadow.camera.right = 80;
    keyLight.shadow.camera.top = 40;
    keyLight.shadow.camera.bottom = -40;
    scene.add(keyLight);

    const fillLight = new THREE.DirectionalLight(0x94a3b8, 0.4);
    fillLight.position.set(-30, 20, -40);
    scene.add(fillLight);

    const rimLight = new THREE.DirectionalLight(0x818cf8, 0.5);
    rimLight.position.set(-40, 30, -30);
    scene.add(rimLight);

    // Pulsing detector glows
    const scintGlow = new THREE.PointLight(0x10b981, 0, 25);
    scintGlow.position.set(-35, 0, 0);
    scene.add(scintGlow);

    const targetGlow = new THREE.PointLight(0xa855f7, 0, 30);
    targetGlow.position.set(-4, 0, 0);
    scene.add(targetGlow);

    const cherenkovGlow = new THREE.PointLight(0x06b6d4, 0, 30);
    cherenkovGlow.position.set(15, 0, 0);
    scene.add(cherenkovGlow);

    const caloGlow = new THREE.PointLight(0x38bdf8, 0, 35);
    caloGlow.position.set(36, 0, 0);
    scene.add(caloGlow);

    // ═══════════════════════════════════════════════
    //  FLOOR & ENVIRONMENT
    // ═══════════════════════════════════════════════
    // Metallic floor platform (solid base so the reflective surface has depth)
    const floorMat = new THREE.MeshStandardMaterial({ color: 0x0a0d14, roughness: 0.95, metalness: 0.15 });
    const floor = new THREE.Mesh(new THREE.BoxGeometry(200, 1, 60), floorMat);
    floor.position.y = -20;
    floor.receiveShadow = true;
    scene.add(floor);

    // Real-time reflective polished-concrete surface on top of the floor —
    // mirrors the beamline hardware and glow effects like an actual clean-room floor
    let floorReflector = null;
    if (typeof THREE.Reflector === 'function') {
        floorReflector = new THREE.Reflector(new THREE.PlaneGeometry(200, 60), {
            clipBias: 0.003,
            textureWidth: window.innerWidth * window.devicePixelRatio,
            textureHeight: window.innerHeight * window.devicePixelRatio,
            color: 0x151a24
        });
        floorReflector.rotation.x = -Math.PI / 2;
        floorReflector.position.y = -19.48;
        scene.add(floorReflector);
    }

    // Grid on floor
    const gridHelper = new THREE.GridHelper(200, 40, 0x1e40af, 0x111827);
    gridHelper.position.y = -19.46;
    gridHelper.material.opacity = 0.25;
    gridHelper.material.transparent = true;
    scene.add(gridHelper);

    // Optical rail along beam axis
    const railMat = new THREE.MeshStandardMaterial({ color: 0x3f3f46, metalness: 0.95, roughness: 0.15 });
    const rail1 = new THREE.Mesh(new THREE.BoxGeometry(150, 0.8, 1.2), railMat);
    rail1.position.set(-5, -18.5, -12);
    rail1.castShadow = true;
    scene.add(rail1);
    const rail2 = rail1.clone();
    rail2.position.z = 12;
    scene.add(rail2);

    // Beam axis laser line
    const axisGeo = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(-75, 0, 0), new THREE.Vector3(65, 0, 0)
    ]);
    const axisMat = new THREE.LineDashedMaterial({ color: 0x334155, dashSize: 2, gapSize: 1.5 });
    const beamAxis = new THREE.Line(axisGeo, axisMat);
    beamAxis.computeLineDistances();
    scene.add(beamAxis);

    // ═══════════════════════════════════════════════
    //  1. PROTON BEAM PIPE & INLET NOZZLE
    // ═══════════════════════════════════════════════
    const pipeMat = new THREE.MeshStandardMaterial({ color: 0x52525b, roughness: 0.15, metalness: 0.95 });

    // Long vacuum beam pipe
    const beamPipe = new THREE.Mesh(new THREE.CylinderGeometry(2.0, 2.0, 30, 32), pipeMat);
    beamPipe.rotation.z = Math.PI / 2;
    beamPipe.position.set(-63, 0, 0);
    beamPipe.castShadow = true;
    scene.add(beamPipe);

    // Flange at exit
    const flangeMat = new THREE.MeshStandardMaterial({ color: 0x71717a, roughness: 0.2, metalness: 0.9 });
    const flange = new THREE.Mesh(new THREE.CylinderGeometry(4.5, 4.5, 1.5, 32), flangeMat);
    flange.rotation.z = Math.PI / 2;
    flange.position.set(-48, 0, 0);
    flange.castShadow = true;
    scene.add(flange);

    // Bellows / corrugated section
    for (let i = 0; i < 4; i++) {
        const bellow = new THREE.Mesh(new THREE.TorusGeometry(2.6, 0.25, 8, 32), flangeMat);
        bellow.rotation.y = Math.PI / 2;
        bellow.position.set(-52 + i * 1.8, 0, 0);
        scene.add(bellow);
    }

    // Glowing beam exit ring
    const nozRingMat = new THREE.MeshBasicMaterial({ color: 0xa855f7, transparent: true, opacity: 0.6 });
    const nozRing = new THREE.Mesh(new THREE.TorusGeometry(2.2, 0.18, 8, 32), nozRingMat);
    nozRing.rotation.y = Math.PI / 2;
    nozRing.position.set(-47, 0, 0);
    scene.add(nozRing);

    const labelBeam = create3DLabel('Proton Beam Inlet', 'Vacuum Beam Pipe (T9 Beamline)', '#a855f7');
    labelBeam.position.set(-60, 12, 0);
    scene.add(labelBeam);

    // ═══════════════════════════════════════════════
    //  2. S1 & S2 TRIGGER SCINTILLATORS (Realistic)
    // ═══════════════════════════════════════════════
    function createScintillator(xPos) {
        const group = new THREE.Group();
        group.position.set(xPos, 0, 0);

        // Scintillator plastic slab (transparent green)
        const slabMat = new THREE.MeshPhysicalMaterial({
            color: 0x34d399, transparent: true, opacity: 0.5,
            emissive: 0x059669, emissiveIntensity: 0.2,
            roughness: 0.1, clearcoat: 1.0, transmission: 0.3
        });
        const slab = new THREE.Mesh(new THREE.BoxGeometry(0.8, 13, 13), slabMat);
        slab.castShadow = true;
        group.add(slab);
        group._slab = slab;

        // Light guide (tapered trapezoid on top)
        const lgMat = new THREE.MeshPhysicalMaterial({
            color: 0x6ee7b7, transparent: true, opacity: 0.3,
            roughness: 0.05, clearcoat: 1.0
        });
        const lgShape = new THREE.CylinderGeometry(1.0, 3.0, 5, 16);
        const lg = new THREE.Mesh(lgShape, lgMat);
        lg.position.set(0, 9.5, 0);
        group.add(lg);

        // PMT body (dark metal cylinder)
        const pmtMat = new THREE.MeshStandardMaterial({ color: 0x27272a, metalness: 0.95, roughness: 0.15 });
        const pmtBody = new THREE.Mesh(new THREE.CylinderGeometry(1.8, 1.8, 7, 20), pmtMat);
        pmtBody.position.set(0, 15.5, 0);
        pmtBody.castShadow = true;
        group.add(pmtBody);

        // PMT glass window (top)
        const pmtGlass = new THREE.Mesh(
            new THREE.CylinderGeometry(1.6, 1.6, 0.3, 20),
            new THREE.MeshPhysicalMaterial({ color: 0x1e293b, metalness: 0.2, roughness: 0.05, clearcoat: 1.0 })
        );
        pmtGlass.position.set(0, 12, 0);
        group.add(pmtGlass);

        // PMT base connector
        const baseMat = new THREE.MeshStandardMaterial({ color: 0x3f3f46, metalness: 0.9, roughness: 0.2 });
        const base = new THREE.Mesh(new THREE.CylinderGeometry(2.2, 2.0, 1.5, 20), baseMat);
        base.position.set(0, 19.5, 0);
        group.add(base);

        // Signal cable
        const cableGeo = new THREE.TubeGeometry(
            new THREE.CatmullRomCurve3([
                new THREE.Vector3(0, 20, 0),
                new THREE.Vector3(0, 22, 2),
                new THREE.Vector3(0, 24, 6),
                new THREE.Vector3(0, 23, 12)
            ]), 16, 0.15, 8, false
        );
        const cable = new THREE.Mesh(cableGeo, new THREE.MeshStandardMaterial({ color: 0x1e1e1e, roughness: 0.8 }));
        group.add(cable);

        // Mounting bracket
        const bracket = new THREE.Mesh(new THREE.BoxGeometry(0.6, 2, 15), baseMat);
        bracket.position.set(0, -8, 0);
        group.add(bracket);

        // Post to floor
        const post = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 12, 8), baseMat);
        post.position.set(0, -14, 0);
        post.castShadow = true;
        group.add(post);

        scene.add(group);
        return group;
    }

    const s1Group = createScintillator(-42);
    const s2Group = createScintillator(-28);

    const labelS = create3DLabel('1. S1 & S2 Scintillators', 'Coincidence Trigger & Time-of-Flight', '#10b981');
    labelS.position.set(-35, 26, 0);
    scene.add(labelS);

    // ═══════════════════════════════════════════════
    //  2.5. DWC (DELAY WIRE CHAMBER) - Realistic
    // ═══════════════════════════════════════════════
    const dwcGroup = new THREE.Group();
    dwcGroup.position.set(-22, 0, 0);

    // Outer aluminum frame
    const dwcFrameMat = new THREE.MeshStandardMaterial({ color: 0x9ca3af, roughness: 0.2, metalness: 0.92 });
    const dwcFrame = new THREE.Mesh(new THREE.BoxGeometry(3, 20, 20), dwcFrameMat);
    dwcFrame.castShadow = true;
    dwcGroup.add(dwcFrame);

    // Inner gas volume (dark)
    const dwcInnerMat = new THREE.MeshPhysicalMaterial({
        color: 0x0f172a, transparent: true, opacity: 0.85,
        roughness: 0.9
    });
    const dwcInner = new THREE.Mesh(new THREE.BoxGeometry(1.5, 18, 18), dwcInnerMat);
    dwcGroup.add(dwcInner);

    // Wire planes (two orthogonal planes of fine gold wires)
    for (let i = -8; i <= 8; i++) {
        // X-plane wires (horizontal)
        const wireGeo = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(-0.3, i, -9), new THREE.Vector3(-0.3, i, 9)
        ]);
        const wireMat = new THREE.LineBasicMaterial({ color: 0xfbbf24, transparent: true, opacity: 0.3 });
        dwcGroup.add(new THREE.Line(wireGeo, wireMat));

        // Y-plane wires (vertical)
        const wireGeo2 = new THREE.BufferGeometry().setFromPoints([
            new THREE.Vector3(0.3, -9, i), new THREE.Vector3(0.3, 9, i)
        ]);
        dwcGroup.add(new THREE.Line(wireGeo2, wireMat.clone()));
    }

    // Gas connectors (small nozzles)
    const gasNozzleMat = new THREE.MeshStandardMaterial({ color: 0x71717a, metalness: 0.9, roughness: 0.2 });
    const gasIn = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 2, 8), gasNozzleMat);
    gasIn.position.set(0, 10.5, -8);
    gasIn.rotation.x = Math.PI / 2;
    dwcGroup.add(gasIn);
    const gasOut = gasIn.clone();
    gasOut.position.set(0, 10.5, 8);
    dwcGroup.add(gasOut);

    // HV connector
    const hvConn = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 1.5, 8), gasNozzleMat);
    hvConn.position.set(0, 10.5, 0);
    dwcGroup.add(hvConn);

    // Support post
    const dwcPost = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 12, 8), gasNozzleMat);
    dwcPost.position.set(0, -16, 0);
    dwcGroup.add(dwcPost);

    scene.add(dwcGroup);

    const labelDWC = create3DLabel('2. Delay Wire Chamber', 'Gas X-Y Position Tracking', '#fbbf24');
    labelDWC.position.set(-22, 20, 0);
    scene.add(labelDWC);

    // ═══════════════════════════════════════════════
    //  3. TIMEPIX3 PIXEL TRACKER - Realistic
    // ═══════════════════════════════════════════════
    const tpxGroup = new THREE.Group();
    tpxGroup.position.set(-16, 0, 0);

    // PCB board (green FR4)
    const pcbMat = new THREE.MeshStandardMaterial({ color: 0x065f46, roughness: 0.5, metalness: 0.3 });
    const pcb = new THREE.Mesh(new THREE.BoxGeometry(0.8, 22, 22), pcbMat);
    pcb.castShadow = true;
    tpxGroup.add(pcb);

    // Gold traces on PCB
    const traceMat = new THREE.MeshBasicMaterial({ color: 0xd4a054, transparent: true, opacity: 0.4 });
    for (let i = -8; i <= 8; i += 2) {
        const trace = new THREE.Mesh(new THREE.BoxGeometry(0.82, 0.15, 18), traceMat);
        trace.position.set(0, i, 0);
        tpxGroup.add(trace);
    }

    // Silicon sensor chip (dark, highly reflective)
    const chipMat = new THREE.MeshStandardMaterial({ color: 0x1c1917, roughness: 0.05, metalness: 0.98 });
    const chip = new THREE.Mesh(new THREE.BoxGeometry(0.15, 14.4, 14.4), chipMat);
    chip.position.set(0.5, 0, 0);
    tpxGroup.add(chip);

    // Wire bond pads (tiny gold dots around chip edge)
    const bondMat = new THREE.MeshBasicMaterial({ color: 0xfbbf24 });
    for (let i = -6; i <= 6; i += 1.5) {
        const pad = new THREE.Mesh(new THREE.SphereGeometry(0.12, 8, 8), bondMat);
        pad.position.set(0.55, i, 7.3);
        tpxGroup.add(pad);
        const pad2 = pad.clone();
        pad2.position.set(0.55, i, -7.3);
        tpxGroup.add(pad2);
    }

    // Active area marker dot
    const tpMarker = new THREE.Mesh(new THREE.SphereGeometry(0.5, 16, 16), new THREE.MeshBasicMaterial({ color: 0xfbbf24 }));
    tpMarker.position.set(0.7, 0, 0);
    tpxGroup.add(tpMarker);

    // Hit ring
    const tpRingMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b, transparent: true, opacity: 0.0, side: THREE.DoubleSide });
    const tpRing = new THREE.Mesh(new THREE.RingGeometry(0.6, 2.0, 32), tpRingMat);
    tpRing.rotation.y = Math.PI / 2;
    tpRing.position.set(0.8, 0, 0);
    tpxGroup.add(tpRing);

    // Cooling block underneath
    const coolMat = new THREE.MeshStandardMaterial({ color: 0x52525b, metalness: 0.85, roughness: 0.2 });
    const coolBlock = new THREE.Mesh(new THREE.BoxGeometry(2, 3, 16), coolMat);
    coolBlock.position.set(-1.5, -12, 0);
    tpxGroup.add(coolBlock);

    // SPIDR readout box behind
    const spidrMat = new THREE.MeshStandardMaterial({ color: 0x27272a, metalness: 0.7, roughness: 0.4 });
    const spidr = new THREE.Mesh(new THREE.BoxGeometry(4, 8, 12), spidrMat);
    spidr.position.set(-3.5, 0, 0);
    spidr.castShadow = true;
    tpxGroup.add(spidr);

    // Ethernet port on SPIDR
    const ethPort = new THREE.Mesh(new THREE.BoxGeometry(0.5, 1.2, 1.8), new THREE.MeshStandardMaterial({ color: 0x3f3f46 }));
    ethPort.position.set(-5.7, -2, 0);
    tpxGroup.add(ethPort);

    // Support post
    const tpxPost = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 10, 8), coolMat);
    tpxPost.position.set(0, -15, 0);
    tpxGroup.add(tpxPost);

    scene.add(tpxGroup);

    const labelTp = create3DLabel('3. Timepix3 Tracker', '256x256 Pixel Matrix (55 um)', '#f59e0b');
    labelTp.position.set(-16, 22, 0);
    scene.add(labelTp);

    // ═══════════════════════════════════════════════
    //  4. INTERACTION TARGET & VETO - Realistic
    // ═══════════════════════════════════════════════
    const targetGroup = new THREE.Group();
    targetGroup.position.set(-4, 0, 0);

    // Target disc (dense metal, e.g. lead)
    const targetMat = new THREE.MeshStandardMaterial({
        color: 0x6b21a8, roughness: 0.2, metalness: 0.88,
        emissive: 0x581c87, emissiveIntensity: 0.1
    });
    const targetDisc = new THREE.Mesh(new THREE.CylinderGeometry(6, 6, 2, 48), targetMat);
    targetDisc.rotation.z = Math.PI / 2;
    targetDisc.castShadow = true;
    targetGroup.add(targetDisc);

    // Target holder ring
    const holderMat = new THREE.MeshStandardMaterial({ color: 0x52525b, metalness: 0.9, roughness: 0.15 });
    const holderRing = new THREE.Mesh(new THREE.TorusGeometry(6.3, 0.35, 8, 48), holderMat);
    holderRing.rotation.y = Math.PI / 2;
    targetGroup.add(holderRing);

    // Mounting stand (vertical post + horizontal arm)
    const mountPost = new THREE.Mesh(new THREE.CylinderGeometry(0.6, 0.6, 18, 8), holderMat);
    mountPost.position.set(0, -10, 0);
    mountPost.castShadow = true;
    targetGroup.add(mountPost);

    const mountArm = new THREE.Mesh(new THREE.BoxGeometry(0.5, 1.5, 14), holderMat);
    mountArm.position.set(0, -1, 0);
    targetGroup.add(mountArm);

    // Veto scintillator (anti-coincidence, behind target)
    const vetoMat = new THREE.MeshPhysicalMaterial({
        color: 0xfb7185, transparent: true, opacity: 0.4,
        emissive: 0xe11d48, emissiveIntensity: 0.12,
        clearcoat: 0.8
    });
    const veto = new THREE.Mesh(new THREE.BoxGeometry(0.5, 12, 12), vetoMat);
    veto.position.set(3.5, 0, 0);
    veto.castShadow = true;
    targetGroup.add(veto);

    // Veto label
    const vetoLabel = create3DLabel('Veto (Anti-coincidence)', '', '#fb7185');
    vetoLabel.position.set(3.5, 10, 0);
    vetoLabel.scale.set(8, 2, 1);
    targetGroup.add(vetoLabel);

    scene.add(targetGroup);

    const labelTarget = create3DLabel('4. Nuclear Target Station', 'Interaction Vertex & Veto Counter', '#a855f7');
    labelTarget.position.set(-4, 22, 0);
    scene.add(labelTarget);

    // ── COLLISION STARBURST PARTICLES ──
    const burstCount = 80;
    const burstPositions = new Float32Array(burstCount * 3);
    const burstVelocities = [];
    for (let i = 0; i < burstCount; i++) {
        burstPositions[i * 3] = -4;
        burstPositions[i * 3 + 1] = 0;
        burstPositions[i * 3 + 2] = 0;
        burstVelocities.push({ vx: (Math.random() - 0.3) * 1.2, vy: (Math.random() - 0.5) * 1.5, vz: (Math.random() - 0.5) * 1.5 });
    }
    const burstGeo = new THREE.BufferGeometry();
    burstGeo.setAttribute('position', new THREE.BufferAttribute(burstPositions, 3));
    const burstMat = new THREE.PointsMaterial({ color: 0xc084fc, size: 0.7, transparent: true, opacity: 0.8, sizeAttenuation: true, blending: THREE.AdditiveBlending, depthWrite: false });
    const burstParticles = new THREE.Points(burstGeo, burstMat);
    scene.add(burstParticles);

    // ═══════════════════════════════════════════════
    //  5. GAS CHERENKOV DETECTOR - Realistic
    // ═══════════════════════════════════════════════
    const chGroup = new THREE.Group();
    chGroup.position.set(15, 0, 0);

    // Main vessel body (large metal cylinder)
    const vesselMat = new THREE.MeshStandardMaterial({ color: 0x3f3f46, metalness: 0.92, roughness: 0.15 });
    const vessel = new THREE.Mesh(new THREE.CylinderGeometry(8, 8, 22, 48), vesselMat);
    vessel.rotation.z = Math.PI / 2;
    vessel.castShadow = true;
    chGroup.add(vessel);

    // Entry and exit windows (thin aluminum, semi-transparent)
    const windowMat = new THREE.MeshPhysicalMaterial({
        color: 0x94a3b8, transparent: true, opacity: 0.25,
        roughness: 0.05, metalness: 0.5, clearcoat: 1.0
    });
    const entryWindow = new THREE.Mesh(new THREE.CylinderGeometry(3.5, 3.5, 0.1, 32), windowMat);
    entryWindow.rotation.z = Math.PI / 2;
    entryWindow.position.set(-11.1, 0, 0);
    chGroup.add(entryWindow);
    const exitWindow = entryWindow.clone();
    exitWindow.position.set(11.1, 0, 0);
    chGroup.add(exitWindow);

    // Flanges at each end
    const chFlangeMat = new THREE.MeshStandardMaterial({ color: 0x52525b, metalness: 0.9, roughness: 0.2 });
    const chFlange1 = new THREE.Mesh(new THREE.TorusGeometry(8, 0.5, 8, 48), chFlangeMat);
    chFlange1.rotation.y = Math.PI / 2;
    chFlange1.position.set(-11, 0, 0);
    chGroup.add(chFlange1);
    const chFlange2 = chFlange1.clone();
    chFlange2.position.set(11, 0, 0);
    chGroup.add(chFlange2);

    // Internal Cherenkov light cone (visible when particle passes)
    const coneMat = new THREE.MeshBasicMaterial({ color: 0x22d3ee, transparent: true, opacity: 0.0, side: THREE.DoubleSide });
    const cone = new THREE.Mesh(new THREE.ConeGeometry(5, 18, 32, 1, true), coneMat);
    cone.rotation.z = -Math.PI / 2;
    cone.position.set(2, 0, 0);
    chGroup.add(cone);

    // Mirror (parabolic reflector at back)
    const mirrorMat = new THREE.MeshStandardMaterial({
        color: 0xe2e8f0, metalness: 1.0, roughness: 0.02,
        emissive: 0x334155, emissiveIntensity: 0.05
    });
    const mirror = new THREE.Mesh(new THREE.SphereGeometry(7, 32, 16, 0, Math.PI, 0, Math.PI * 0.6), mirrorMat);
    mirror.rotation.y = Math.PI / 2;
    mirror.position.set(8, 0, 0);
    chGroup.add(mirror);

    // PMT box on top (for Cherenkov photon collection)
    const chPmtBox = new THREE.Mesh(new THREE.BoxGeometry(6, 4, 4), spidrMat);
    chPmtBox.position.set(5, 10, 0);
    chPmtBox.castShadow = true;
    chGroup.add(chPmtBox);

    // Gas inlet/outlet nozzles
    const chGasIn = new THREE.Mesh(new THREE.CylinderGeometry(0.4, 0.4, 2, 8), gasNozzleMat);
    chGasIn.position.set(-5, 8.5, 0);
    chGroup.add(chGasIn);
    const chGasOut = chGasIn.clone();
    chGasOut.position.set(5, 8.5, 0);
    chGroup.add(chGasOut);

    // Support legs
    const chLeg1 = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 12, 8), gasNozzleMat);
    chLeg1.position.set(-6, -14, 5);
    chLeg1.castShadow = true;
    chGroup.add(chLeg1);
    const chLeg2 = chLeg1.clone(); chLeg2.position.set(-6, -14, -5); chGroup.add(chLeg2);
    const chLeg3 = chLeg1.clone(); chLeg3.position.set(6, -14, 5); chGroup.add(chLeg3);
    const chLeg4 = chLeg1.clone(); chLeg4.position.set(6, -14, -5); chGroup.add(chLeg4);

    scene.add(chGroup);

    const labelCh = create3DLabel('5. Gas Cherenkov Detector', 'Threshold PID (CO2 Radiator)', '#06b6d4');
    labelCh.position.set(15, 22, 0);
    scene.add(labelCh);

    // ═══════════════════════════════════════════════
    //  6. 4x4 LEAD GLASS EM CALORIMETER - Realistic
    // ═══════════════════════════════════════════════
    const caloGroup = new THREE.Group();
    caloGroup.position.set(38, 0, 0);

    // Steel support frame
    const frameMat = new THREE.MeshStandardMaterial({ color: 0x3f3f46, metalness: 0.9, roughness: 0.2 });
    const frameTop = new THREE.Mesh(new THREE.BoxGeometry(16, 0.8, 18), frameMat);
    frameTop.position.set(0, 8.5, 0);
    caloGroup.add(frameTop);
    const frameBot = frameTop.clone();
    frameBot.position.set(0, -8.5, 0);
    caloGroup.add(frameBot);
    const frameL = new THREE.Mesh(new THREE.BoxGeometry(16, 18, 0.8), frameMat);
    frameL.position.set(0, 0, -8.5);
    caloGroup.add(frameL);
    const frameR = frameL.clone();
    frameR.position.set(0, 0, 8.5);
    caloGroup.add(frameR);

    // 4x4 lead glass crystal array
    const caloBlocks = [];
    const blockGeom = new THREE.BoxGeometry(14, 3.6, 3.6);
    const blockEdges = new THREE.EdgesGeometry(blockGeom);

    for (let r = 0; r < 4; r++) {
        for (let c = 0; c < 4; c++) {
            const bMat = new THREE.MeshPhysicalMaterial({
                color: 0x1e3a8a, emissive: 0x1e3a8a, emissiveIntensity: 0.12,
                transparent: true, opacity: 0.6, roughness: 0.08, clearcoat: 0.9,
                transmission: 0.15
            });
            const block = new THREE.Mesh(blockGeom, bMat);
            block.position.set(0, (r - 1.5) * 4.0, (c - 1.5) * 4.0);
            block.castShadow = true;

            const edgeLine = new THREE.LineSegments(blockEdges, new THREE.LineBasicMaterial({ color: 0x60a5fa, transparent: true, opacity: 0.3 }));
            block.add(edgeLine);

            caloGroup.add(block);
            caloBlocks.push(block);
        }
    }

    // PMT array behind calorimeter (16 PMTs)
    const caloPmtMat = new THREE.MeshStandardMaterial({ color: 0x27272a, metalness: 0.9, roughness: 0.2 });
    for (let r = 0; r < 4; r++) {
        for (let c = 0; c < 4; c++) {
            const pmt = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 4, 12), caloPmtMat);
            pmt.rotation.z = Math.PI / 2;
            pmt.position.set(9, (r - 1.5) * 4.0, (c - 1.5) * 4.0);
            caloGroup.add(pmt);
        }
    }

    // Back plate / HV distribution board
    const backPlateMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.6, roughness: 0.3 });
    const backPlate = new THREE.Mesh(new THREE.BoxGeometry(0.5, 17, 17), backPlateMat);
    backPlate.position.set(11.5, 0, 0);
    caloGroup.add(backPlate);

    // Support legs
    const caloLeg1 = new THREE.Mesh(new THREE.CylinderGeometry(0.5, 0.5, 12, 8), frameMat);
    caloLeg1.position.set(-5, -14.5, 6);
    caloLeg1.castShadow = true;
    caloGroup.add(caloLeg1);
    const caloLeg2 = caloLeg1.clone(); caloLeg2.position.set(-5, -14.5, -6); caloGroup.add(caloLeg2);
    const caloLeg3 = caloLeg1.clone(); caloLeg3.position.set(8, -14.5, 6); caloGroup.add(caloLeg3);
    const caloLeg4 = caloLeg1.clone(); caloLeg4.position.set(8, -14.5, -6); caloGroup.add(caloLeg4);

    scene.add(caloGroup);

    const labelCalo = create3DLabel('6. EM Calorimeter', '4x4 Lead Glass (Energy Measurement)', '#38bdf8');
    labelCalo.position.set(38, 22, 0);
    scene.add(labelCalo);

    // ── EM SHOWER SPARK PARTICLES ──
    const sparkCount = 100;
    const sparkPositions = new Float32Array(sparkCount * 3);
    const sparkVelocities = [];
    for (let i = 0; i < sparkCount; i++) {
        sparkPositions[i * 3] = 30;
        sparkPositions[i * 3 + 1] = 0;
        sparkPositions[i * 3 + 2] = 0;
        sparkVelocities.push({ vx: -Math.random() * 0.4, vy: (Math.random() - 0.5) * 0.8, vz: (Math.random() - 0.5) * 0.8, life: 0 });
    }
    const sparkGeo = new THREE.BufferGeometry();
    sparkGeo.setAttribute('position', new THREE.BufferAttribute(sparkPositions, 3));
    const sparkMat = new THREE.PointsMaterial({ color: 0xfbbf24, size: 0.5, transparent: true, opacity: 0.9, sizeAttenuation: true, blending: THREE.AdditiveBlending, depthWrite: false });
    const sparkParticles = new THREE.Points(sparkGeo, sparkMat);
    scene.add(sparkParticles);

    // ── PARTICLE TRACKS ──
    const protonTrackLine = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0xc084fc, linewidth: 2 }));
    scene.add(protonTrackLine);

    const gamma1Track = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0x38bdf8, linewidth: 2 }));
    scene.add(gamma1Track);
    const gamma2Track = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0x38bdf8, linewidth: 2 }));
    scene.add(gamma2Track);

    const protonPacket = new THREE.Mesh(new THREE.SphereGeometry(0.6, 16, 16), new THREE.MeshBasicMaterial({ color: 0xc084fc }));
    scene.add(protonPacket);

    const packet1 = new THREE.Mesh(new THREE.SphereGeometry(0.55, 16, 16), new THREE.MeshBasicMaterial({ color: 0x7dd3fc }));
    const packet2 = new THREE.Mesh(new THREE.SphereGeometry(0.55, 16, 16), new THREE.MeshBasicMaterial({ color: 0x7dd3fc }));
    scene.add(packet1);
    scene.add(packet2);

    const haloMat1 = new THREE.MeshBasicMaterial({ color: 0x38bdf8, transparent: true, opacity: 0.3, side: THREE.DoubleSide });
    const halo1 = new THREE.Mesh(new THREE.RingGeometry(0.3, 1.6, 16), haloMat1);
    scene.add(halo1);
    const halo2 = new THREE.Mesh(new THREE.RingGeometry(0.3, 1.6, 16), haloMat1.clone());
    scene.add(halo2);

    // ── STARFIELD BACKGROUND ──
    const starCount = 400;
    const starPos = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount; i++) {
        starPos[i * 3] = (Math.random() - 0.5) * 400;
        starPos[i * 3 + 1] = Math.random() * 100 + 25;
        starPos[i * 3 + 2] = (Math.random() - 0.5) * 400;
    }
    const starGeo = new THREE.BufferGeometry();
    starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
    const starMat = new THREE.PointsMaterial({ color: 0x94a3b8, size: 0.25, transparent: true, opacity: 0.4 });
    scene.add(new THREE.Points(starGeo, starMat));

    // ═══════════════════════════════════════════════
    //  CAMERA & WALKTHROUGH FLIGHT STATE
    // ═══════════════════════════════════════════════
    const camTarget = { x: -30, y: 45, z: 110, tx: 5, ty: 0, tz: 0 };
    let isLerpActive = true;
    let isTourActive = false;
    let tourIndex = 0;
    let tourTimer = 0;

    const tourWaypoints = [
        { name: "Proton Beam Inlet", x: -68, y: 8, z: 22, tx: -55, ty: 0, tz: 0, hold: 160 },
        { name: "S1 & S2 Trigger Scintillators", x: -38, y: 14, z: 28, tx: -35, ty: 2, tz: 0, hold: 180 },
        { name: "Delay Wire Chamber (DWC)", x: -22, y: 12, z: 26, tx: -22, ty: 0, tz: 0, hold: 180 },
        { name: "Timepix3 Silicon Pixel Tracker", x: -16, y: 12, z: 24, tx: -16, ty: 0, tz: 0, hold: 180 },
        { name: "Nuclear Target & Veto", x: -4, y: 10, z: 24, tx: -4, ty: 0, tz: 0, hold: 200 },
        { name: "Gas Cherenkov Detector", x: 15, y: 14, z: 32, tx: 15, ty: 0, tz: 0, hold: 180 },
        { name: "4x4 Lead Glass EM Calorimeter", x: 38, y: 14, z: 36, tx: 38, ty: 0, tz: 0, hold: 200 },
        { name: "Full Spectrometer Overview", x: -30, y: 45, z: 110, tx: 5, ty: 0, tz: 0, hold: 240 }
    ];

    // ── WASD KEYBOARD NAVIGATION ──
    const keysDown = {};
    const keyHandler = (e) => {
        if (!container.contains(document.activeElement) && e.target.tagName === 'INPUT') return;
        const key = e.key.toLowerCase();
        if (['w', 'a', 's', 'd', 'q', 'e', ' ', 'shift', 'arrowup', 'arrowdown', 'arrowleft', 'arrowright'].includes(key)) {
            keysDown[key] = (e.type === 'keydown');
            isLerpActive = false;
        }
    };
    window.addEventListener('keydown', keyHandler);
    window.addEventListener('keyup', keyHandler);

    // ═══════════════════════════════════════════════
    //  ANIMATION LOOP
    // ═══════════════════════════════════════════════
    let animId = null;
    let time = 0;
    let protonProgress = 0;
    let photonProgress = 0;
    let burstTimer = 0;
    const PROTON_SPEED = 1.32;  // units are now "per second" — driven by real delta time
    const PHOTON_SPEED = 1.92;
    const clock = new THREE.Clock();

    // Glowing motion-trail ribbons behind the proton and the two decay photons —
    // built from short-lived fading points so fast packets read as real particle streaks
    function createTrail(color, count = 22) {
        const positions = new Float32Array(count * 3);
        const alphas = new Float32Array(count);
        const geo = new THREE.BufferGeometry();
        geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geo.setAttribute('alpha', new THREE.BufferAttribute(alphas, 1));
        const mat = new THREE.PointsMaterial({
            color, size: 0.55, transparent: true, opacity: 0.85,
            sizeAttenuation: true, blending: THREE.AdditiveBlending, depthWrite: false
        });
        const points = new THREE.Points(geo, mat);
        scene.add(points);
        return { points, geo, positions, history: [] , count};
    }
    function pushTrail(trail, pos) {
        trail.history.unshift(pos.clone());
        if (trail.history.length > trail.count) trail.history.length = trail.count;
        for (let i = 0; i < trail.count; i++) {
            const p = trail.history[i] || trail.history[trail.history.length - 1] || pos;
            trail.positions[i * 3] = p.x;
            trail.positions[i * 3 + 1] = p.y;
            trail.positions[i * 3 + 2] = p.z;
        }
        trail.geo.attributes.position.needsUpdate = true;
        trail.points.material.opacity = 0.85 * Math.min(1, trail.history.length / 6);
    }
    const protonTrail = createTrail(0xc084fc, 16);
    const gamma1Trail = createTrail(0x7dd3fc, 20);
    const gamma2Trail = createTrail(0x7dd3fc, 20);

    function animate() {
        animId = requestAnimationFrame(animate);
        const delta = Math.min(clock.getDelta(), 0.05); // clamp to avoid big jumps on tab-switch
        time += delta;

        // ── FREE KEYBOARD FLYTHROUGH ──
        const speed = (keysDown['shift'] ? 26 : 10) * delta;
        const forward = new THREE.Vector3();
        camera.getWorldDirection(forward);
        const right = new THREE.Vector3().crossVectors(forward, camera.up).normalize();

        if (keysDown['w'] || keysDown['arrowup']) camera.position.addScaledVector(forward, speed);
        if (keysDown['s'] || keysDown['arrowdown']) camera.position.addScaledVector(forward, -speed);
        if (keysDown['a'] || keysDown['arrowleft']) camera.position.addScaledVector(right, -speed);
        if (keysDown['d'] || keysDown['arrowright']) camera.position.addScaledVector(right, speed);
        if (keysDown['q'] || keysDown['c']) camera.position.y -= speed * 0.7;
        if (keysDown['e'] || keysDown[' ']) camera.position.y += speed * 0.7;

        // ── AUTOMATIC CINEMATIC WALKTHROUGH TOUR ──
        if (isTourActive) {
            const wp = tourWaypoints[tourIndex];
            camTarget.x = wp.x; camTarget.y = wp.y; camTarget.z = wp.z;
            camTarget.tx = wp.tx; camTarget.ty = wp.ty; camTarget.tz = wp.tz;
            isLerpActive = true;

            const hint = document.getElementById('three-hint');
            if (hint) hint.innerHTML = `<span style="color:#38bdf8;">&#9654;</span> <strong>Touring:</strong> ${wp.name} (${tourIndex + 1}/${tourWaypoints.length})`;

            tourTimer++;
            if (tourTimer > wp.hold) {
                tourTimer = 0;
                tourIndex = (tourIndex + 1) % tourWaypoints.length;
            }
        }

        if (isLerpActive) {
            camera.position.x += (camTarget.x - camera.position.x) * 0.035;
            camera.position.y += (camTarget.y - camera.position.y) * 0.035;
            camera.position.z += (camTarget.z - camera.position.z) * 0.035;
            if (controls) {
                controls.target.x += (camTarget.tx - controls.target.x) * 0.04;
                controls.target.y += (camTarget.ty - controls.target.y) * 0.04;
                controls.target.z += (camTarget.tz - controls.target.z) * 0.04;
            }
        }

        if (controls) controls.update();

        const ev = dataBuffers.latest_event;
        const offsetY = ((ev.timepix_y - 128) / 128) * 4.5;
        const offsetZ = ((ev.timepix_x - 128) / 128) * 4.5;

        // ── PROTON BEAM ANIMATION ──
        protonProgress += PROTON_SPEED * delta;
        if (protonProgress > 1.0) protonProgress = 0;

        const protonPath = [
            new THREE.Vector3(-70, 0, 0),
            new THREE.Vector3(-42, 0, 0),
            new THREE.Vector3(-28, 0, 0),
            new THREE.Vector3(-22, offsetY * 0.3, offsetZ * 0.3),
            new THREE.Vector3(-16, offsetY * 0.8, offsetZ * 0.8),
            new THREE.Vector3(-4, offsetY, offsetZ)
        ];

        protonTrackLine.geometry.setFromPoints(protonPath);

        const pSeg = Math.min(Math.floor(protonProgress * 5), 4);
        const pFrac = (protonProgress * 5) - pSeg;
        const pA = protonPath[pSeg], pB = protonPath[pSeg + 1];
        protonPacket.position.lerpVectors(pA, pB, pFrac);
        pushTrail(protonTrail, protonPacket.position);

        nozRing.material.opacity = 0.3 + 0.3 * Math.sin(time * 6);
        nozRing.scale.setScalar(1.0 + 0.08 * Math.sin(time * 6));

        // ── SCINTILLATOR FLASH ──
        const protonX = protonPacket.position.x;
        const s1Flash = Math.max(0, 1.0 - Math.abs(protonX - (-42)) * 0.3);
        const s2Flash = Math.max(0, 1.0 - Math.abs(protonX - (-28)) * 0.3);
        s1Group._slab.material.emissiveIntensity = 0.2 + s1Flash * 2.0;
        s1Group._slab.material.opacity = 0.5 + s1Flash * 0.45;
        s2Group._slab.material.emissiveIntensity = 0.2 + s2Flash * 2.0;
        s2Group._slab.material.opacity = 0.5 + s2Flash * 0.45;
        scintGlow.intensity = (s1Flash + s2Flash) * 5;

        // Timepix hit ring
        const tpFlash = Math.max(0, 1.0 - Math.abs(protonX - (-16)) * 0.4);
        tpMarker.position.set(0.7, offsetY * 0.8, offsetZ * 0.8);
        tpMarker.scale.setScalar(0.8 + tpFlash * 1.4);
        tpRing.position.set(0.8, offsetY * 0.8, offsetZ * 0.8);
        tpRing.material.opacity = tpFlash * 0.7;
        tpRing.scale.setScalar(1.0 + tpFlash * 1.8);

        // ── TARGET COLLISION & STARBURST ──
        targetGlow.intensity = Math.max(0, 1.0 - Math.abs(protonX - (-4)) * 0.15) * 7;
        targetDisc.rotation.x += 0.002;

        if (protonProgress > 0.95 && burstTimer <= 0) {
            burstTimer = 1.0;
            for (let i = 0; i < burstCount; i++) {
                burstPositions[i * 3] = -4;
                burstPositions[i * 3 + 1] = offsetY;
                burstPositions[i * 3 + 2] = offsetZ;
                burstVelocities[i].vx = (Math.random() - 0.2) * 1.5;
                burstVelocities[i].vy = (Math.random() - 0.5) * 2.0;
                burstVelocities[i].vz = (Math.random() - 0.5) * 2.0;
            }
        }
        if (burstTimer > 0) {
            burstTimer -= 0.03;
            burstMat.opacity = Math.max(0, burstTimer * 0.9);
            for (let i = 0; i < burstCount; i++) {
                burstPositions[i * 3] += burstVelocities[i].vx;
                burstPositions[i * 3 + 1] += burstVelocities[i].vy;
                burstPositions[i * 3 + 2] += burstVelocities[i].vz;
            }
            burstGeo.attributes.position.needsUpdate = true;
        }

        // ── DUAL PHOTON TRACKS ──
        photonProgress += PHOTON_SPEED * delta;
        if (photonProgress > 1.0) {
            photonProgress = 0;
            protonTrail.history.length = 0;
            gamma1Trail.history.length = 0;
            gamma2Trail.history.length = 0;
        }

        const g1End = new THREE.Vector3(30, offsetY + 5.5, offsetZ - 5.5);
        const g2End = new THREE.Vector3(30, offsetY - 5.5, offsetZ + 5.5);
        const decayPt = new THREE.Vector3(-4, offsetY, offsetZ);
        const g1Mid = new THREE.Vector3(15, offsetY + 2.8, offsetZ - 2.8);
        const g2Mid = new THREE.Vector3(15, offsetY - 2.8, offsetZ + 2.8);

        gamma1Track.geometry.setFromPoints([decayPt, g1Mid, g1End]);
        gamma2Track.geometry.setFromPoints([decayPt, g2Mid, g2End]);

        const gFrac = photonProgress;
        packet1.position.lerpVectors(decayPt, g1End, gFrac);
        packet2.position.lerpVectors(decayPt, g2End, gFrac);
        if (gFrac > 0.01 && gFrac < 0.98) {
            pushTrail(gamma1Trail, packet1.position);
            pushTrail(gamma2Trail, packet2.position);
        }

        halo1.position.copy(packet1.position);
        halo1.lookAt(camera.position);
        halo1.material.opacity = 0.25 * (1.0 - gFrac);
        halo1.scale.setScalar(1.0 + gFrac * 1.5);

        halo2.position.copy(packet2.position);
        halo2.lookAt(camera.position);
        halo2.material.opacity = 0.25 * (1.0 - gFrac);
        halo2.scale.setScalar(1.0 + gFrac * 1.5);

        // Cherenkov light cone
        const qdc = ev.cherenkov_qdc || 0;
        coneMat.opacity = qdc > 500 ? 0.12 + 0.08 * Math.sin(time * 8) : 0.0;
        cherenkovGlow.intensity = qdc > 500 ? 2 + Math.sin(time * 8) : 0;

        // ── EM SHOWER SPARKS ──
        if (gFrac > 0.85) {
            for (let i = 0; i < sparkCount; i++) {
                sparkVelocities[i].life = Math.max(0, sparkVelocities[i].life - 0.04);
                if (sparkVelocities[i].life <= 0 && Math.random() < 0.3) {
                    const isG1 = Math.random() > 0.5;
                    sparkPositions[i * 3] = 30 + Math.random() * 2;
                    sparkPositions[i * 3 + 1] = (isG1 ? g1End.y : g2End.y) + (Math.random() - 0.5) * 4;
                    sparkPositions[i * 3 + 2] = (isG1 ? g1End.z : g2End.z) + (Math.random() - 0.5) * 4;
                    sparkVelocities[i].vx = -0.1 - Math.random() * 0.3;
                    sparkVelocities[i].vy = (Math.random() - 0.5) * 0.5;
                    sparkVelocities[i].vz = (Math.random() - 0.5) * 0.5;
                    sparkVelocities[i].life = 1.0;
                }
                sparkPositions[i * 3] += sparkVelocities[i].vx;
                sparkPositions[i * 3 + 1] += sparkVelocities[i].vy;
                sparkPositions[i * 3 + 2] += sparkVelocities[i].vz;
            }
            sparkGeo.attributes.position.needsUpdate = true;
            sparkMat.opacity = 0.7;
            caloGlow.intensity = 3 + 2 * Math.sin(time * 10);
        } else {
            sparkMat.opacity = Math.max(0, sparkMat.opacity - 0.03);
            caloGlow.intensity = Math.max(0, caloGlow.intensity - 0.1);
        }

        // ── CALORIMETER CRYSTALS ──
        const maxCaloE = Math.max(...dataBuffers.calorimeter_heatmap, 1);
        for (let i = 0; i < 16; i++) {
            const eVal = dataBuffers.calorimeter_heatmap[i] || 0;
            const fraction = Math.min(eVal / maxCaloE, 1.0);
            const block = caloBlocks[i];
            const pulse = 0.05 * Math.sin(time * 4 + i * 0.5);

            if (eVal > 300) {
                block.material.color.lerpColors(new THREE.Color(0x1e40af), new THREE.Color(0x7dd3fc), fraction);
                block.material.emissive.setHex(0x0ea5e9);
                block.material.emissiveIntensity = 0.3 + fraction * 0.9 + pulse;
                block.material.opacity = 0.8 + fraction * 0.2;
            } else {
                block.material.color.setHex(0x1e3a8a);
                block.material.emissive.setHex(0x1e3a8a);
                block.material.emissiveIntensity = 0.08 + pulse * 0.5;
                block.material.opacity = 0.4;
            }
        }

        // Diagnostics HUD
        const dE1 = document.getElementById('diag-e1');
        if (dE1) dE1.textContent = `${ev.e_gamma1} MeV`;
        const dE2 = document.getElementById('diag-e2');
        if (dE2) dE2.textContent = `${ev.e_gamma2} MeV`;
        const dTh = document.getElementById('diag-theta');
        if (dTh) dTh.textContent = `${ev.theta_gg} mrad`;
        const dMass = document.getElementById('diag-invmass');
        if (dMass) dMass.textContent = `${ev.inv_mass} MeV/c^2`;

        if (floorReflector) floorReflector.visible = true;
        if (composer) {
            composer.render();
        } else {
            renderer.render(scene, camera);
        }
    }
    animate();

    globalThreeState = {
        camera, controls, camTarget, container, composer, renderer,
        setLerp: (val) => { isLerpActive = val; },
        toggleTour: () => {
            isTourActive = !isTourActive;
            tourTimer = 0;
            tourIndex = 0;
            isLerpActive = isTourActive;
            return isTourActive;
        },
        setBloom: (enabled) => { if (bloomPass) bloomPass.enabled = enabled; }
    };

    return {
        type: 'three_3d',
        renderer,
        camera,
        controls,
        cleanupThree: () => {
            if (animId) cancelAnimationFrame(animId);
            window.removeEventListener('keydown', keyHandler);
            window.removeEventListener('keyup', keyHandler);
            if (composer) composer.dispose && composer.dispose();
            renderer.dispose();
        }
    };
}

function focusOnDetector(detName) {
    if (!globalThreeState) return;
    const { camera, controls, camTarget, setLerp } = globalThreeState;
    setLerp(true);
    const presets = {
        'scint':    { x: -38, y: 14, z: 30, tx: -35, ty: 2, tz: 0 },
        'dwc':      { x: -22, y: 12, z: 28, tx: -22, ty: 0, tz: 0 },
        'timepix':  { x: -16, y: 12, z: 26, tx: -16, ty: 0, tz: 0 },
        'target':   { x: -4,  y: 12, z: 26, tx: -4,  ty: 0, tz: 0 },
        'cherenkov':{ x: 15,  y: 14, z: 34, tx: 15,  ty: 0, tz: 0 },
        'calo':     { x: 38,  y: 14, z: 38, tx: 38,  ty: 0, tz: 0 }
    };
    const p = presets[detName];
    if (p) {
        camTarget.x = p.x; camTarget.y = p.y; camTarget.z = p.z;
        camTarget.tx = p.tx; camTarget.ty = p.ty; camTarget.tz = p.tz;
    }
}

function set3DCameraPreset(preset) {
    if (!globalThreeState) return;
    const { camera, controls, camTarget, setLerp } = globalThreeState;
    setLerp(true);
    if (preset === 'iso') {
        camTarget.x = -25; camTarget.y = 40; camTarget.z = 100;
        camTarget.tx = 5; camTarget.ty = 0; camTarget.tz = 0;
    } else if (preset === 'top') {
        camTarget.x = 0; camTarget.y = 110; camTarget.z = 1;
        camTarget.tx = 0; camTarget.ty = 0; camTarget.tz = 0;
    } else if (preset === 'side') {
        camTarget.x = 0; camTarget.y = 0; camTarget.z = 110;
        camTarget.tx = 0; camTarget.ty = 0; camTarget.tz = 0;
    } else if (preset === 'front') {
        camTarget.x = 110; camTarget.y = 0; camTarget.z = 0;
        camTarget.tx = 0; camTarget.ty = 0; camTarget.tz = 0;
    }
}

function toggleWalkthroughTour() {
    if (!globalThreeState) return;
    const active = globalThreeState.toggleTour();
    const btn = document.getElementById('btn-walkthrough');
    if (btn) {
        btn.textContent = active ? '️ Stop Tour' : '🚶 Walkthrough Tour';
        btn.classList.toggle('active', active);
    }
}

function toggleFreeRoamMode() {
    if (!globalThreeState) return;
    globalThreeState.setLerp(false);
    const hint = document.getElementById('three-hint');
    if (hint) hint.innerHTML = `✈️ <strong>Free Flight:</strong> Use [W][A][S][D] to Fly, [Q][E] for Altitude, [Shift] for Turbo`;
}

// ===== MAIN ANIMATION & UPDATE LOOP =====
function updateAllPanels() {
    for (const [viewId, panelInfo] of Object.entries(activePanels)) {
        const { chart, chartType } = panelInfo;

        if (chartType === 'bar' && viewId === 'calorimeter_energy') {
            chart.setOption({ series: [{ data: Array.from(dataBuffers.calorimeter_energy) }] });
            const total = dataBuffers.calorimeter_energy.reduce((a, b) => a + b, 0);
            updateFooter(viewId, `Total Energy: ${(total/1000).toFixed(1)}k ADC`);
        }
        else if (chartType === 'heatmap' && viewId === 'calorimeter_heatmap') {
            const hmData = [];
            let maxVal = 1;
            for (let r = 0; r < 4; r++) {
                for (let c = 0; c < 4; c++) {
                    const val = dataBuffers.calorimeter_heatmap[r*4 + c];
                    hmData.push([c, 3-r, val]);
                    if (val > maxVal) maxVal = val;
                }
            }
            chart.setOption({ visualMap: { max: maxVal }, series: [{ data: hmData }] });
            const total = dataBuffers.calorimeter_heatmap.reduce((a, b) => a + b, 0);
            updateFooter(viewId, `Dual Cluster Energy: ${(total/1000).toFixed(1)}k ADC`);
        }
        else if (chartType === 'histogram' && viewId === 'scintillator_timing') {
            chart.setOption({ series: [{ data: Array.from(dataBuffers.scintillator_timing).slice(0, 30) }] });
            const total = dataBuffers.scintillator_timing.reduce((a, b) => a + b, 0);
            updateFooter(viewId, `Entries: ${total.toFixed(0)}`);
        }
        else if (chartType === 'histogram' && viewId === 'scintillator_pe') {
            chart.setOption({ series: [{ data: Array.from(dataBuffers.scintillator_pe) }] });
            const total = dataBuffers.scintillator_pe.reduce((a, b) => a + b, 0);
            updateFooter(viewId, `Entries: ${total.toFixed(0)}`);
        }
        else if (chartType === 'heatmap2d_dwc' && viewId === 'dwc_hitmap') {
            drawHeatmap256(chart.canvas, dataBuffers.dwc_hitmap);
            const totalHits = dataBuffers.dwc_hitmap.reduce((a, b) => a + b, 0);
            updateFooter(viewId, `Total DWC Hits: ${totalHits.toLocaleString()}`);
        }
        else if (chartType === 'histogram' && viewId === 'dwc_delta_t') {
            chart.setOption({ series: [{ data: Array.from(dataBuffers.dwc_delta_t).slice(0, 50) }] });
            const total = dataBuffers.dwc_delta_t.reduce((a, b) => a + b, 0);
            updateFooter(viewId, `DWC Events: ${total.toFixed(0)}`);
        }
        else if (chartType === 'heatmap2d' && viewId === 'timepix_hitmap') {
            drawHeatmap256(chart.canvas, dataBuffers.timepix_hitmap);
            const totalHits = dataBuffers.timepix_hitmap.reduce((a, b) => a + b, 0);
            updateFooter(viewId, `Total Pixel Hits: ${totalHits.toLocaleString()}`);
        }
        else if (chartType === 'histogram' && viewId === 'timepix_tot') {
            chart.setOption({ series: [{ data: Array.from(dataBuffers.timepix_tot).slice(0, 50) }] });
            const total = dataBuffers.timepix_tot.reduce((a, b) => a + b, 0);
            updateFooter(viewId, `Entries: ${total.toFixed(0)}`);
        }
        else if (chartType === 'histogram' && viewId === 'cherenkov_qdc') {
            chart.setOption({ series: [{ data: Array.from(dataBuffers.cherenkov_qdc) }] });
            const total = dataBuffers.cherenkov_qdc.reduce((a, b) => a + b, 0);
            updateFooter(viewId, `Entries: ${total.toFixed(0)}`);
        }
        else if (chartType === 'timeseries' && viewId === 'trigger_rate') {
            const points = dataBuffers.trigger_rate;
            chart.setOption({ 
                xAxis: { data: points.map(p => new Date(p.t).toLocaleTimeString()) },
                series: [{ data: points.map(p => p.v) }] 
            });
            const last = points.length > 0 ? points[points.length - 1].v : 0;
            updateFooter(viewId, `Last Trigger ID: ${last}`);
        }
        else if (chartType === 'pid_pie' && viewId === 'pid_overview') {
            const { pi0, proton, charged_pion } = dataBuffers.pid_counts;
            const total = pi0 + proton + charged_pion;
            const pi0Percent = total > 0 ? ((pi0 / total) * 100).toFixed(1) : 0;
            const chPercent = total > 0 ? ((charged_pion / total) * 100).toFixed(1) : 0;
            
            chart.setOption({
                series: [{
                    data: [
                        { value: pi0, name: `π⁰ → γγ (${pi0Percent}%)` },
                        { value: charged_pion, name: `Charged Hadron (${chPercent}%)` },
                        { value: proton, name: `Proton Beam` }
                    ]
                }]
            });
            updateFooter(viewId, `Total PID Events: ${total.toLocaleString()} | π⁰ Yield: ${pi0}`);
        }
        else if (chartType === 'pi0_mass' && viewId === 'pi0_invariant_mass') {
            chart.setOption({
                series: [{ data: Array.from(dataBuffers.pi0_mass_hist) }]
            });
            const total = dataBuffers.pi0_mass_hist.reduce((a, b) => a + b, 0);
            updateFooter(viewId, `π⁰ Candidates: ${total.toLocaleString()} | Expected Peak: m(π⁰) = 134.97 MeV/c²`);
        }
        else if (chartType === 'fit_hist' && viewId === 'physics_fitting') {
            const fit = computeGaussianFit(dataBuffers.calorimeter_fit_buffer);
            chart.setOption({
                series: [
                    { data: Array.from(dataBuffers.calorimeter_fit_buffer) },
                    { data: fit.fitLine }
                ]
            });
            updateFooter(viewId, `Calorimeter Peak: μ = ${fit.mean} MeV | σ = ${fit.sigma} MeV | Resolution = ${fit.res}%`);
        }
        else if (chartType === 'dqm_view' && viewId === 'dqm_summary') {
            renderDqmGrid();
            updateFooter(viewId, `Total Events Audited: ${dataBuffers.dqm_total_calorimeter_events.toLocaleString()}`);
        }
        else if (chartType === 'pid_scatter' && viewId === 'pid_correlation') {
            chart.setOption({ series: [{ data: dataBuffers.pid_correlation }] });
            updateFooter(viewId, `Correlation Points: ${dataBuffers.pid_correlation.length}`);
        }
        else if (chartType === 'slow_control' && viewId === 'slow_control_view') {
            updateFooter(viewId, `Last Telemetry Received: ${new Date().toLocaleTimeString()} | SC_ACTIVE`);
        }
        else if (chartType === 'coincidence_view' && viewId === 'coincidence_view') {
            chart.setOption({ series: [{ data: Array.from(dataBuffers.coincidence.delta_t_hist) }] });
            updateFooter(viewId, `Built Events: ${dataBuffers.coincidence.total_built} | Efficiency: ${dataBuffers.coincidence.efficiency_pct}%`);
        }
    }

    // Top Bar Update
    const now = Date.now();
    if (now - lastSecondTimestamp >= 1000) {
        document.getElementById('eventsPerSec').textContent = `${eventCountThisSecond.toLocaleString()} ev/s`;
        eventCountThisSecond = 0;
        lastSecondTimestamp = now;
    }
    document.getElementById('totalEvents').textContent = totalEventCount.toLocaleString();

    const { pi0, charged_pion } = dataBuffers.pid_counts;
    if (pi0 + charged_pion > 0) {
        document.getElementById('topPidRatio').textContent = `${((pi0 / (pi0 + charged_pion)) * 100).toFixed(1)}% π⁰`;
    }
}

function computeGaussianFit(histogramBins) {
    let maxVal = 0, peakIdx = 25;
    for (let i = 5; i < 45; i++) {
        if (histogramBins[i] > maxVal) {
            maxVal = histogramBins[i];
            peakIdx = i;
        }
    }
    if (maxVal < 5) return { fitLine: new Array(50).fill(0), mean: 0, sigma: 0, res: 0 };

    const mean = peakIdx * 100;
    const sigma = 320;
    const A = maxVal;
    const fitLine = [];
    for (let i = 0; i < 50; i++) {
        const x = i * 100;
        const val = A * Math.exp(-Math.pow(x - mean, 2) / (2 * Math.pow(sigma, 2)));
        fitLine.push(val);
    }
    const resolution = mean > 0 ? ((sigma / mean) * 100).toFixed(1) : 0;
    return { fitLine, mean, sigma, res: resolution };
}

function renderDqmGrid() {
    const container = document.getElementById('dqm-container');
    if (!container) return;

    let html = '';
    const totalCalo = dataBuffers.dqm_total_calorimeter_events || 1;
    const avgHits = totalCalo / 16;

    for (let ch = 0; ch < 16; ch++) {
        const hits = dataBuffers.dqm_channel_hits[ch];
        let statusClass = 'good';
        let statusText = 'HEALTHY';

        if (hits === 0 && totalCalo > 100) {
            statusClass = 'bad';
            statusText = 'DEAD';
        } else if (hits > avgHits * 2.8 && totalCalo > 100) {
            statusClass = 'warn';
            statusText = 'NOISY';
        }

        html += `
            <div class="dqm-card">
                <div class="dqm-card-header">
                    <span>Calo Ch ${ch}</span>
                    <span class="dqm-status-pill ${statusClass}">${statusText}</span>
                </div>
                <div class="dqm-metric">${hits.toLocaleString()}</div>
                <div class="dqm-sub">Hits recorded</div>
            </div>
        `;
    }
    container.innerHTML = html;
}

// ── ONLINE HISTOGRAM PRESENTER (OHP) — classic "scaler versus time" grid ──
// Renders one small ROOT-style white canvas per scaler channel, each showing
// the cumulative-count ramp plus an Entries/Mean/StdDev/Underflow/Overflow
// stat box, exactly like the real Online Histogram Presenter "Scaler" plugin.
const OHP_CHANNEL_LABELS = {
    Calorimeter: 'CountsVsTime_Calorimeter',
    CaloClus: 'CaloClus',
    TDC: 'TDC',
    TOF: 'TOF',
    S1: 'S1',
    S2: 'S2',
    S3: 'S3',
    DWC: 'DWC',
    QDC: 'QDC',
    DWC_HV: 'DWC_HV',
    QDC_HV: 'QDC_HV',
    EVTTRG: 'EVTTRG',
    Ch11_EVTTRG: 'CountsVsTime_Ch11_EVTTRG'
};

let currentOhpGridCols = 3;
let activeOhpModalKey = null;

function setOhpGridCols(cols) {
    currentOhpGridCols = cols;
    const grid = document.getElementById('ohp-card-grid');
    if (!grid) return;
    grid.className = `ohp-grid cols-${cols}`;
    
    document.querySelectorAll('.ohp-grid-btn').forEach(btn => btn.classList.remove('active'));
    if (event && event.target) event.target.classList.add('active');
}

function openOhpModal(key) {
    activeOhpModalKey = key;
    const overlay = document.getElementById('ohp-modal-overlay');
    const titleEl = document.getElementById('ohp-modal-title-text');
    if (titleEl) titleEl.textContent = OHP_CHANNEL_LABELS[key] || key;
    if (overlay) overlay.classList.add('active');
    updateOhpModalPlot();
}

function closeOhpModal() {
    activeOhpModalKey = null;
    const overlay = document.getElementById('ohp-modal-overlay');
    if (overlay) overlay.classList.remove('active');
}


function switchTdaqTab(viewId, tabName) {
    const wrap = document.getElementById('tdaq-console-' + viewId);
    if (!wrap) return;
    
    // Deactivate all buttons
    wrap.querySelectorAll('.tdaq-tab-btn').forEach(btn => btn.classList.remove('active'));
    // Activate clicked button (we'll just use the text match or exact element if we had event, but we can find it by onclick)
    wrap.querySelectorAll('.tdaq-tab-btn').forEach(btn => {
        if(btn.getAttribute('onclick').includes("'" + tabName + "'")) btn.classList.add('active');
    });
    
    // Hide all tabs
    wrap.querySelectorAll('.tdaq-tab-content').forEach(tab => tab.classList.remove('active'));
    // Show selected tab
    const selectedTab = wrap.querySelector('#tab-' + viewId + '-' + tabName);
    if(selectedTab) selectedTab.classList.add('active');
}

function renderOhpGrid() {
    const container = document.getElementById('ohp-container');
    if (!container) return;

    if (!container.dataset.built) {
        let html = `
            <div class="ohp-toolbar">
                <div class="ohp-toolbar-title">
                    <span></span> Online Histogram Presenter — Scaler Display
                </div>
                <div class="ohp-grid-btn-group">
                    <button class="ohp-grid-btn" onclick="setOhpGridCols(4)">Kompakt (4x4)</button>
                    <button class="ohp-grid-btn active" onclick="setOhpGridCols(3)">Standart (3x3)</button>
                    <button class="ohp-grid-btn" onclick="setOhpGridCols(2)">Large (2x2)</button>
                </div>
            </div>
            <div class="ohp-grid cols-${currentOhpGridCols}" id="ohp-card-grid">
        `;
        for (const key of Object.keys(OHP_CHANNEL_LABELS)) {
            html += `
                <div class="ohp-card">
                    <div class="ohp-card-title">
                        <span>${OHP_CHANNEL_LABELS[key]}</span>
                        <button class="ohp-expand-btn" onclick="openOhpModal('${key}')" title="Expand / Stats">⛶ Expand</button>
                    </div>
                    <canvas id="ohp-canvas-${key}"></canvas>
                </div>
            `;
        }
        html += `</div>`;
        container.innerHTML = html;
        container.dataset.built = '1';
    }

    for (const key of Object.keys(OHP_CHANNEL_LABELS)) {
        const canvas = document.getElementById(`ohp-canvas-${key}`);
        if (canvas) drawOhpMiniPlot(canvas, dataBuffers.ohp_series[key] || []);
    }

    if (activeOhpModalKey) {
        updateOhpModalPlot();
    }
}

function updateOhpModalPlot() {
    if (!activeOhpModalKey) return;
    const canvas = document.getElementById('ohp-modal-canvas');
    if (!canvas) return;
    
    const series = dataBuffers.ohp_series[activeOhpModalKey] || [];
    drawOhpMiniPlot(canvas, series);

    // Calculate ROOT Statistics
    const vals = series.map(p => p.v);
    const n = vals.length;
    const sum = vals.reduce((a, b) => a + b, 0);
    const mean = n > 0 ? (sum / n) : 0;
    const variance = n > 0 ? vals.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / n : 0;
    const stdDev = Math.sqrt(variance);
    const maxVal = vals.length ? Math.max(...vals) : 0;

    const elEnt = document.getElementById('ohp-stat-entries'); if (elEnt) elEnt.textContent = n.toLocaleString();
    const elMean = document.getElementById('ohp-stat-mean'); if (elMean) elMean.textContent = mean.toFixed(2);
    const elStd = document.getElementById('ohp-stat-std'); if (elStd) elStd.textContent = stdDev.toFixed(2);
    const elRms = document.getElementById('ohp-stat-rms'); if (elRms) elRms.textContent = Math.sqrt(mean*mean + variance).toFixed(2);
    const elIn = document.getElementById('ohp-stat-integral'); if (elIn) elIn.textContent = sum.toLocaleString();
    const elPk = document.getElementById('ohp-stat-peak'); if (elPk) elPk.textContent = maxVal.toLocaleString();
}

function drawOhpMiniPlot(canvas, series) {
    const cssW = canvas.clientWidth || 180;
    const cssH = canvas.clientHeight || 118;
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    if (canvas.width !== cssW * dpr || canvas.height !== cssH * dpr) {
        canvas.width = cssW * dpr;
        canvas.height = cssH * dpr;
    }
    const ctx = canvas.getContext('2d');
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, cssW, cssH);

    // white ROOT-canvas background + plot frame
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, cssW, cssH);

    const padL = 34, padR = 6, padT = 8, padB = 16;
    const plotW = cssW - padL - padR;
    const plotH = cssH - padT - padB;

    const values = series.map(p => p.v);
    const maxV = values.length ? Math.max(...values, 1) : 1;
    const n = series.length;

    // axes
    ctx.strokeStyle = '#111827';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(padL, padT); ctx.lineTo(padL, padT + plotH); ctx.lineTo(padL + plotW, padT + plotH);
    ctx.stroke();

    // faint gridlines
    ctx.strokeStyle = 'rgba(15,23,42,0.08)';
    for (let i = 1; i <= 3; i++) {
        const y = padT + (plotH * i) / 4;
        ctx.beginPath(); ctx.moveTo(padL, y); ctx.lineTo(padL + plotW, y); ctx.stroke();
    }

    // y-axis max label
    ctx.fillStyle = '#334155';
    ctx.font = '8px JetBrains Mono, monospace';
    ctx.textAlign = 'right';
    ctx.fillText(maxV >= 1000 ? `${(maxV/1000).toFixed(1)}k` : `${Math.round(maxV)}`, padL - 3, padT + 4);
    ctx.fillText('0', padL - 3, padT + plotH);

    // the scaler ramp itself (black line like a real ROOT TGraph)
    if (n > 1) {
        ctx.strokeStyle = '#1d4ed8';
        ctx.lineWidth = 1.4;
        ctx.beginPath();
        for (let i = 0; i < n; i++) {
            const x = padL + (plotW * i) / (n - 1);
            const y = padT + plotH - (values[i] / maxV) * plotH;
            if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
        }
        ctx.stroke();

        // most recent point marker
        const lastX = padL + plotW;
        const lastY = padT + plotH - (values[n - 1] / maxV) * plotH;
        ctx.fillStyle = '#dc2626';
        ctx.beginPath();
        ctx.arc(lastX, lastY, 2, 0, Math.PI * 2);
        ctx.fill();
    }

    // ROOT-style stat box (Entries / Mean / StdDev / Underflow / Overflow)
    const entries = values.length ? values[values.length - 1] : 0;
    const mean = values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0;
    const variance = values.length ? values.reduce((a, b) => a + (b - mean) ** 2, 0) / values.length : 0;
    const stdDev = Math.sqrt(variance);

    const statLines = [
        `Entries   ${entries.toFixed(0)}`,
        `Mean      ${mean.toFixed(1)}`,
        `Std Dev   ${stdDev.toFixed(1)}`,
        `Underflow 0`,
        `Overflow  0`
    ];
    const boxW = 64, boxH = statLines.length * 8 + 4;
    const boxX = cssW - boxW - 3, boxY = 3;
    ctx.fillStyle = 'rgba(255,255,255,0.92)';
    ctx.strokeStyle = '#94a3b8';
    ctx.lineWidth = 0.75;
    ctx.fillRect(boxX, boxY, boxW, boxH);
    ctx.strokeRect(boxX, boxY, boxW, boxH);
    ctx.fillStyle = '#0f1117';
    ctx.font = '6.5px JetBrains Mono, monospace';
    ctx.textAlign = 'left';
    statLines.forEach((line, i) => {
        ctx.fillText(line, boxX + 3, boxY + 9 + i * 8);
    });
}

function exportDqmJson() {
    const report = {
        experiment: "CERN BL4S 2026 - Team PionIST 3",
        generatedAt: new Date().toISOString(),
        totalEvents: totalEventCount,
        pi0Candidates: dataBuffers.pi0_mass_hist.reduce((a, b) => a + b, 0),
        calorimeterHits: Array.from(dataBuffers.dqm_channel_hits)
    };
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `BL4S_DQM_Report_${Date.now()}.json`;
    a.click();
}

function downloadCsvHistograms() {
    let csv = "Channel,Calorimeter_Total_ADC,Calorimeter_Hits\n";
    for (let i = 0; i < 16; i++) {
        csv += `${i},${dataBuffers.calorimeter_energy[i]},${dataBuffers.dqm_channel_hits[i]}\n`;
    }
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `BL4S_Histograms_${Date.now()}.csv`;
    a.click();
}

function attachHeatmapHoverTooltip(canvas, tooltipEl, viewId) {
    if (!canvas || !tooltipEl) return;
    const bufferKey = viewId; // dwc_hitmap or timepix_hitmap — matches dataBuffers key directly
    canvas.addEventListener('mousemove', (e) => {
        const rect = canvas.getBoundingClientRect();
        const relX = (e.clientX - rect.left) / rect.width;
        const relY = (e.clientY - rect.top) / rect.height;
        const px = Math.min(255, Math.max(0, Math.floor(relX * 256)));
        const py = Math.min(255, Math.max(0, Math.floor(relY * 256)));
        const buf = dataBuffers[bufferKey];
        const val = buf ? (buf[py * 256 + px] || 0) : 0;
        tooltipEl.style.display = 'block';
        tooltipEl.style.left = `${e.clientX - rect.left + 14}px`;
        tooltipEl.style.top = `${e.clientY - rect.top - 8}px`;
        tooltipEl.innerHTML = `Pixel (${px}, ${py})<br><strong style="color:#38bdf8;">${val.toLocaleString()} hits</strong>`;
    });
    canvas.addEventListener('mouseleave', () => { tooltipEl.style.display = 'none'; });
}

function drawHeatmap256(canvas, data) {
    const ctx = canvas.getContext('2d');
    const size = Math.min(canvas.parentElement.clientWidth, canvas.parentElement.clientHeight);
    canvas.width = 256;
    canvas.height = 256;
    canvas.style.width = size + 'px';
    canvas.style.height = size + 'px';
    canvas.classList.add('heatmap-canvas');

    const imgData = ctx.createImageData(256, 256);
    const maxVal = Math.max(...data, 1);

    for (let i = 0; i < 256 * 256; i++) {
        const intensity = Math.min(data[i] / Math.max(maxVal * 0.5, 1), 1);
        const idx = i * 4;
        imgData.data[idx] = Math.floor(intensity * 220 + (1 - intensity) * 25);
        imgData.data[idx + 1] = Math.floor(intensity * 100 + (1 - intensity) * 20);
        imgData.data[idx + 2] = Math.floor((1 - intensity) * 160 + intensity * 40);
        imgData.data[idx + 3] = data[i] > 0 ? 255 : 40;
    }
    ctx.putImageData(imgData, 0, 0);
}

function updateFooter(viewId, text) {
    const el = document.getElementById(`footer-${viewId}`);
    if (el) el.textContent = text;
}

window.addEventListener('resize', () => {
    for (const panelInfo of Object.values(activePanels)) {
        if (panelInfo.chart && typeof panelInfo.chart.resize === 'function') {
            panelInfo.chart.resize();
        }
    }
});


// =========================================================================
//  DVR PLAYBACK & REPLAY ENGINE
// =========================================================================
const dvrState = {
    isRecording: true,
    isReplayMode: false,
    isPlaying: false,
    recordedEvents: [],
    maxEvents: 500,
    currentIndex: 0,
    playIntervalId: null,
    playbackSpeed: 1.0
};

function recordLiveEvent(event) {
    if (!dvrState.isRecording) return;
    dvrState.recordedEvents.push(JSON.parse(JSON.stringify(event)));
    if (dvrState.recordedEvents.length > dvrState.maxEvents) {
        dvrState.recordedEvents.shift();
    }
    updateDvrUI();
}

function updateDvrUI() {
    const slider = document.getElementById('dvrSlider');
    const text = document.getElementById('dvrFrameText');
    if (!slider || !text) return;

    slider.max = Math.max(0, dvrState.recordedEvents.length - 1);
    if (!dvrState.isReplayMode) {
        slider.value = slider.max;
        text.textContent = `${dvrState.recordedEvents.length} / ${dvrState.recordedEvents.length}`;
    } else {
        slider.value = dvrState.currentIndex;
        text.textContent = `${dvrState.currentIndex + 1} / ${dvrState.recordedEvents.length}`;
    }
}

function toggleDvrRecord() {
    dvrState.isRecording = !dvrState.isRecording;
    const btn = document.getElementById('btnDvrRec');
    const text = document.getElementById('recText');
    if (btn && text) {
        btn.classList.toggle('active-rec', dvrState.isRecording);
        text.textContent = dvrState.isRecording ? 'Recording Clip' : 'Record Clip';
    }
}

function seekDvr(index) {
    dvrState.isReplayMode = true;
    dvrState.currentIndex = parseInt(index);
    document.getElementById('dvrStatusPill').className = 'dvr-status-pill replay';
    document.getElementById('dvrStatusPill').textContent = '📼 REPLAY MODE';
    replayCurrentEvent();
    updateDvrUI();
}

function stepDvr(delta) {
    if (dvrState.recordedEvents.length === 0) return;
    dvrState.isReplayMode = true;
    dvrState.currentIndex = Math.max(0, Math.min(dvrState.recordedEvents.length - 1, dvrState.currentIndex + delta));
    document.getElementById('dvrStatusPill').className = 'dvr-status-pill replay';
    document.getElementById('dvrStatusPill').textContent = '📼 REPLAY MODE';
    replayCurrentEvent();
    updateDvrUI();
}

function toggleDvrPlay() {
    if (dvrState.recordedEvents.length === 0) return;
    dvrState.isPlaying = !dvrState.isPlaying;
    const btn = document.getElementById('btnDvrPlay');
    if (btn) btn.textContent = dvrState.isPlaying ? 'Pause' : 'Play';

    if (dvrState.isPlaying) {
        dvrState.isReplayMode = true;
        document.getElementById('dvrStatusPill').className = 'dvr-status-pill replay';
        document.getElementById('dvrStatusPill').textContent = '📼 REPLAY MODE';
        
        if (dvrState.playIntervalId) clearInterval(dvrState.playIntervalId);
        dvrState.playIntervalId = setInterval(() => {
            if (dvrState.currentIndex < dvrState.recordedEvents.length - 1) {
                dvrState.currentIndex++;
                replayCurrentEvent();
                updateDvrUI();
            } else {
                toggleDvrPlay(); // Pause at end
            }
        }, 100 / dvrState.playbackSpeed);
    } else {
        if (dvrState.playIntervalId) clearInterval(dvrState.playIntervalId);
    }
}

function setDvrSpeed(speed) {
    dvrState.playbackSpeed = parseFloat(speed);
    if (dvrState.isPlaying) {
        toggleDvrPlay();
        toggleDvrPlay();
    }
}

function returnToLiveStream() {
    dvrState.isReplayMode = false;
    if (dvrState.isPlaying) toggleDvrPlay();
    document.getElementById('dvrStatusPill').className = 'dvr-status-pill live';
    document.getElementById('dvrStatusPill').textContent = '● LIVE STREAM';
    updateDvrUI();
}

function replayCurrentEvent() {
    const ev = dvrState.recordedEvents[dvrState.currentIndex];
    if (ev) {
        routeEvent(ev, true); // true = replay mode (don't re-record)
    }
}

function exportDvrClip() {
    if (dvrState.recordedEvents.length === 0) {
        alert('No recorded events to export!');
        return;
    }
    const blob = new Blob([JSON.stringify(dvrState.recordedEvents, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `BL4S_DVR_Clip_${Date.now()}.json`;
    a.click();
}

function loadDvrFile(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        try {
            const data = JSON.parse(e.target.result);
            if (Array.isArray(data) && data.length > 0) {
                dvrState.recordedEvents = data;
                seekDvr(0);
                alert(`Successfully loaded ${data.length} events into DVR!`);
            } else {
                alert('Invalid event format in JSON file.');
            }
        } catch (err) {
            alert('Failed to parse JSON file: ' + err.message);
        }
    };
    reader.readAsText(file);
}

// =========================================================================
//  ML PID & SLOW CONTROL & COINCIDENCE BUFFERS
// =========================================================================
dataBuffers.ml_pid = {
    prediction: "pi0",
    confidence: 98.4,
    latency_us: 4.2,
    probabilities: { pi0: 98.4, electron: 0.8, proton: 0.5, muon: 0.2, noise: 0.1 },
    features: { calo_e_total: 2450, cherenkov_qdc: 45, timepix_tot: 34, tof_ns: 15.2 }
};

dataBuffers.slow_control = {
    pmt_hv_v: [1420.4, 1418.1, 1449.8, 1390.2],
    cherenkov_pressure_bar: 2.451,
    timepix_temp_c: 18.4,
    ambient_temp_c: 21.8
};

dataBuffers.coincidence = {
    window_ns: 10.0,
    efficiency_pct: 85.4,
    rejection_pct: 14.6,
    total_built: 0,
    delta_t_hist: new Array(50).fill(0)
};

setInterval(updateAllPanels, 100);

// Sample OHP scaler counters into rolling "counts vs time" series every 500ms —
// matches the cadence of the real Online Histogram Presenter scaler plugin.
setInterval(() => {
    const t = Date.now();
    for (const key of Object.keys(dataBuffers.ohp_cumulative)) {
        const series = dataBuffers.ohp_series[key];
        series.push({ t, v: dataBuffers.ohp_cumulative[key] });
        if (series.length > OHP_MAX_POINTS) series.shift();
    }
    if (activePanels['ohp_grid']) renderOhpGrid();
}, 500);

// =========================================================================
//  PRO 3D FULLSCREEN & INTERACTIVE GUIDE ENGINE (ZERO DEPENDENCIES)
// =========================================================================

// 1. DUAL-MODE 3D FULLSCREEN (Native API + Universal CSS Overlay)
function toggle3DFullscreen() {
    const container = document.querySelector('.three-container');
    if (!container) {
        alert('Please open the "3D Modular Beamline" panel first from the sidebar!');
        return;
    }

    const isCurrentlyFullscreen = container.classList.contains('is-fullscreen') || 
                                 !!document.fullscreenElement || 
                                 !!document.webkitFullscreenElement;

    if (!isCurrentlyFullscreen) {
        // Enter Fullscreen
        container.classList.add('is-fullscreen');
        if (container.requestFullscreen) {
            container.requestFullscreen().catch(() => {});
        } else if (container.webkitRequestFullscreen) {
            container.webkitRequestFullscreen();
        }
    } else {
        // Exit Fullscreen
        container.classList.remove('is-fullscreen');
        if (document.exitFullscreen && document.fullscreenElement) {
            document.exitFullscreen().catch(() => {});
        } else if (document.webkitExitFullscreen && document.webkitFullscreenElement) {
            document.webkitExitFullscreen();
        }
    }

    // Force Three.js and ECharts to resize immediately
    setTimeout(() => {
        window.dispatchEvent(new Event('resize'));
        if (typeof globalThreeState !== 'undefined' && globalThreeState && globalThreeState.camera && globalThreeState.renderer) {
            const w = container.clientWidth || window.innerWidth;
            const h = container.clientHeight || window.innerHeight;
            globalThreeState.camera.aspect = w / h;
            globalThreeState.camera.updateProjectionMatrix();
            globalThreeState.renderer.setSize(w, h);
            if (globalThreeState.composer) globalThreeState.composer.setSize(w, h);
        }
    }, 50);
}

// Listen for ESC key or native fullscreen change
document.addEventListener('fullscreenchange', () => {
    const container = document.querySelector('.three-container');
    if (!document.fullscreenElement && container) {
        container.classList.remove('is-fullscreen');
        window.dispatchEvent(new Event('resize'));
    }
});
document.addEventListener('webkitfullscreenchange', () => {
    const container = document.querySelector('.three-container');
    if (!document.webkitFullscreenElement && container) {
        container.classList.remove('is-fullscreen');
        window.dispatchEvent(new Event('resize'));
    }
});
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        const container = document.querySelector('.three-container');
        if (container && container.classList.contains('is-fullscreen')) {
            container.classList.remove('is-fullscreen');
            window.dispatchEvent(new Event('resize'));
        }
        close3DGuide();
    }
});


// 2. BUILT-IN INTERACTIVE GUIDE TOUR (100% Pure JS & Camera Synchronization)
const guideSteps = [
    {
        icon: "",
        title: "Welcome to the BL4S 3D Beamline Spectrometer",
        target: "all",
        body: "This interactive 3D environment represents the entire experiment setup at the CERN T9 beamline.<br><br>• <strong>Mouse Scroll:</strong> Zoom in/out deeply on any detector component.<br>• <strong>Left-Click + Drag:</strong> Rotate and orbit around the setup.<br>• <strong>Right-Click + Drag:</strong> Pan the camera.<br>• <strong>WASD / Arrow Keys:</strong> Walk and fly freely in 3D space."
    },
    {
        icon: "",
        title: "1. S1 & S2 Trigger Scintillators",
        target: "scint",
        body: "<strong>Plastic Scintillators + PMT Tubes:</strong><br>As incoming beam protons traverse S1 and S2, plastic scintillator slabs flash green. Photomultiplier tubes (PMTs) detect the light with sub-nanosecond precision to form the <strong>coincidence trigger</strong> and Time-of-Flight (ToF) measurement."
    },
    {
        icon: "",
        title: "2. Delay Wire Chamber (DWC)",
        target: "dwc",
        body: "<strong>Gas Delay Wire Tracking Chamber:</strong><br>Equipped with orthogonal X and Y gold wire planes inside an active gas volume. Measures the spatial transverse coordinates (x, y) of charged particle tracks with sub-millimeter resolution."
    },
    {
        icon: "",
        title: "3. Timepix3 Silicon Pixel Tracker",
        target: "timepix",
        body: "<strong>Hybrid Pixel Detector (256x256 pixels, 55 um pitch):</strong><br>Features a high-resistivity silicon sensor bump-bonded to a Timepix3 readout ASIC. Records Time-over-Threshold (energy loss) and Time-of-Arrival (timing) simultaneously per pixel."
    },
    {
        icon: "",
        title: "4. Nuclear Target & Anti-Coincidence Veto",
        target: "target",
        body: "<strong>Target Station & Pink Veto Counter:</strong><br>Protons collide with atomic nuclei in the target disk (p + A -> pi0 + X), producing neutral pions (pi0). The pink veto scintillator flags charged particles to isolate clean neutral decays."
    },
    {
        icon: "",
        title: "5. Gas Cherenkov Detector",
        target: "cherenkov",
        body: "<strong>Threshold Particle Identification (PID):</strong><br>Particles exceeding the speed of light in the gas radiator emit a cone of ultraviolet Cherenkov radiation. A 45° parabolic mirror focuses the photons onto a high-gain PMT for electron/pion separation."
    },
    {
        icon: "",
        title: "6. 4x4 Lead Glass EM Calorimeter",
        target: "calo",
        body: "<strong>16-Channel Electromagnetic Calorimeter Matrix:</strong><br>The neutral pion decays into two photons (pi0 -> gamma gamma). Each photon develops an electromagnetic shower in the lead glass crystals. 16 individual PMTs record the energy clusters, allowing full invariant mass M(gamma gamma) reconstruction."
    }
];

let currentGuideStep = 0;

function start3DTutorial() {
    currentGuideStep = 0;
    const modal = document.getElementById('interactive-guide-modal');
    if (modal) {
        modal.style.display = 'flex';
        renderGuideStep(currentGuideStep);
    }
}

function close3DGuide() {
    const modal = document.getElementById('interactive-guide-modal');
    if (modal) modal.style.display = 'none';
}

function renderGuideStep(idx) {
    const step = guideSteps[idx];
    if (!step) return;

    const iconEl = document.getElementById('guide-icon');
    if (iconEl) iconEl.textContent = step.icon;
    const titleEl = document.getElementById('guide-title-text');
    if (titleEl) titleEl.textContent = step.title;
    const badgeEl = document.getElementById('guide-step-badge');
    if (badgeEl) badgeEl.textContent = `Step ${idx + 1} of ${guideSteps.length}`;
    const bodyEl = document.getElementById('guide-body-text');
    if (bodyEl) bodyEl.innerHTML = step.body;

    // Render progress dots
    const dotsContainer = document.getElementById('guide-dots');
    if (dotsContainer) {
        dotsContainer.innerHTML = '';
        guideSteps.forEach((_, i) => {
            const dot = document.createElement('div');
            dot.className = `guide-dot ${i === idx ? 'active' : ''}`;
            dotsContainer.appendChild(dot);
        });
    }

    // Button states
    const prevBtn = document.getElementById('guide-btn-prev');
    if (prevBtn) prevBtn.style.visibility = idx === 0 ? 'hidden' : 'visible';
    const nextBtn = document.getElementById('guide-btn-next');
    if (nextBtn) nextBtn.textContent = idx === guideSteps.length - 1 ? 'Finish Tour ✓' : 'Next ';

    // Synchronize 3D Camera with the guide!
    if (typeof focusOnDetector === 'function') {
        if (step.target === 'all') {
            if (typeof set3DCameraPreset === 'function') set3DCameraPreset('iso');
        } else {
            focusOnDetector(step.target);
        }
    }
}

function next3DGuideStep() {
    if (currentGuideStep < guideSteps.length - 1) {
        currentGuideStep++;
        renderGuideStep(currentGuideStep);
    } else {
        close3DGuide();
    }
}

function prev3DGuideStep() {
    if (currentGuideStep > 0) {
        currentGuideStep--;
        renderGuideStep(currentGuideStep);
    }
}



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

