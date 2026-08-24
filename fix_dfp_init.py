import re

with open('bl4s_event_explorer.html', 'r') as f:
    content = f.read()

# 1. Remove dfp_panel from the skip list so echarts.init is called
content = content.replace("} else if (chartType === 'dfp_panel' || chartType === 'live_event_feed' || chartType === 'geco_panel') {", "} else if (chartType === 'live_event_feed' || chartType === 'geco_panel') {")

# 2. Add dfp_panel to the else block (initialization)
init_target = "if (chartType === 'bar') {"
init_dfp = """if (chartType === 'dfp_panel') {
                // Initial setup for DFP rate chart
                chart.setOption({
                    grid: { top: 10, right: 10, bottom: 20, left: 40 },
                    tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,23,42,0.9)' },
                    xAxis: { type: 'category', data: [], show: false },
                    yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
                    series: [{
                        data: [],
                        type: 'line',
                        smooth: true,
                        symbol: 'none',
                        lineStyle: { width: 2, color: '#10b981' },
                        areaStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                                { offset: 0, color: 'rgba(16,185,129,0.3)' },
                                { offset: 1, color: 'rgba(16,185,129,0.01)' }
                            ])
                        }
                    }]
                });
            } else """
content = content.replace(init_target, init_dfp + init_target)

# 3. Simplify the update logic in updateAllPanels since we init it above
update_bad = """if (chartType === 'dfp_panel') {
            const points = dataBuffers.trigger_rate;
            const rates = points.map(p => p.v);
            const times = points.map(p => new Date(p.t).toLocaleTimeString());
            
            chart.setOption({
                grid: { top: 10, right: 10, bottom: 20, left: 40 },
                tooltip: { trigger: 'axis', backgroundColor: 'rgba(15,23,42,0.9)' },
                xAxis: { type: 'category', data: times, show: false },
                yAxis: { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
                series: [{
                    data: rates,
                    type: 'line',
                    smooth: true,
                    symbol: 'none',
                    lineStyle: { width: 2, color: '#10b981' },
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(16,185,129,0.3)' },
                            { offset: 1, color: 'rgba(16,185,129,0.01)' }
                        ])
                    }
                }]
            });
            const last = points.length > 0 ? points[points.length - 1].v : 0;
            updateFooter(viewId, `Live Throughput: ${last} ev/s`);
        }
        else """
update_good = """if (chartType === 'dfp_panel') {
            const points = dataBuffers.trigger_rate;
            chart.setOption({
                xAxis: { data: points.map(p => new Date(p.t).toLocaleTimeString()) },
                series: [{ data: points.map(p => p.v) }]
            });
            const last = points.length > 0 ? points[points.length - 1].v : 0;
            updateFooter(viewId, `Live Throughput: ${last} ev/s`);
        }
        else """
content = content.replace(update_bad, update_good)

with open('bl4s_event_explorer.html', 'w') as f:
    f.write(content)

