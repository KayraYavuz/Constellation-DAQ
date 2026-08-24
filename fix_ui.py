import re

with open('bl4s_event_explorer.html', 'r') as f:
    content = f.read()

# 1. Fix OHP Grid min-height so it scrolls
content = content.replace('min-height:140px;', 'min-height:220px;')

# 2. Add DFP Chart Div back
dfp_end_tag = '</div>\n                </div>\n            </div>\n        `;'
dfp_with_chart = '''</div>
                </div>
                <!-- Live Rate Chart for DFP -->
                <div style="flex:1; width:100%; min-height:180px; margin-top:10px;" id="chart-${viewId}"></div>
            </div>
        `;'''
content = content.replace(dfp_end_tag, dfp_with_chart)

# 3. Add update logic for DFP Panel
update_target = "if (chartType === 'bar' && viewId === 'calorimeter_energy') {"
update_dfp = """if (chartType === 'dfp_panel') {
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
content = content.replace(update_target, update_dfp + update_target)

with open('bl4s_event_explorer.html', 'w') as f:
    f.write(content)

