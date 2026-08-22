with open("bl4s_event_explorer.html", "r") as f:
    html = f.read()

# 1. Remove const hvChannelData from the bottom (around line 5600)
bottom_hv_start = html.find("// ===== MODERN CAEN HV & DFP ENGINE =====")
if bottom_hv_start == -1:
    print("Could not find bottom hv start")

# Extract the functions from bottom
bottom_part = html[bottom_hv_start:]
# Cut out const hvChannelData from bottom
hv_data_def = """const hvChannelData = [
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

function isHvOn(channelId) {
    const ch = hvChannelData.find(c => c.id === channelId);
    return ch ? ch.on : true;
}
"""

# Put hv_data_def right before activePanels
global_state_marker = "// ===== GLOBAL STATE & BUFFERS ====="
html = html.replace(global_state_marker, hv_data_def + "\n" + global_state_marker)

# In the bottom part, remove the duplicate declaration of hvChannelData
html = html.replace("""const hvChannelData = [
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
];""", "")

# 2. Update routeEvent to strictly check isHvOn for each detector subsystem
old_calo_route = """    } else if (sat === 'Calorimeter') {
        const ch = event.ch;
        if (ch >= 0 && ch < 16) {"""

new_calo_route = """    } else if (sat === 'Calorimeter') {
        const ch = event.ch;
        const chId = 'CAL_' + String(ch).padStart(2, '0');
        // Check if High Voltage is ON for this specific PMT channel
        if (!isHvOn(chId)) {
            // PMT High Voltage is OFF -> Zero light amplification, no signal registered!
            return;
        }
        if (ch >= 0 && ch < 16) {"""

html = html.replace(old_calo_route, new_calo_route)

# Update Scintillator check
old_scint_route = """    } else if (sat === 'Scintillator') {"""
new_scint_route = """    } else if (sat === 'Scintillator') {
        // If trigger scintillators are OFF, coincidence triggers do not fire
        if (!isHvOn('SCINT_S1') || !isHvOn('SCINT_S2')) {
            return;
        }"""
html = html.replace(old_scint_route, new_scint_route)

# Update Cherenkov check
old_ch_route = """    } else if (sat === 'Cherenkov') {"""
new_ch_route = """    } else if (sat === 'Cherenkov') {
        if (!isHvOn('CHERENKOV_PMT')) {
            event.n_photons = 0;
            event.qdc = 0;
        }"""
html = html.replace(old_ch_route, new_ch_route)

# Update DWC check
old_dwc_route = """    } else if (sat === 'DWC') {"""
new_dwc_route = """    } else if (sat === 'DWC') {
        if (!isHvOn('DWC_ANODE')) {
            return;
        }"""
html = html.replace(old_dwc_route, new_dwc_route)

# Update Timepix check
old_tpx_route = """    } else if (sat === 'Timepix') {"""
new_tpx_route = """    } else if (sat === 'Timepix') {
        if (!isHvOn('TIMEPIX_BIAS')) {
            return;
        }"""
html = html.replace(old_tpx_route, new_tpx_route)

with open("bl4s_event_explorer.html", "w") as f:
    f.write(html)

print("HV Physics Integration complete!")
