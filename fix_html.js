const fs = require('fs');
let code = fs.readFileSync('bl4s_event_explorer.html', 'utf8');
const lines = code.split('\n');

// 1. Delete lines 2817 to 3173 (inclusive, 0-indexed: 2816 to 3172)
lines.splice(2816, 3173 - 2817 + 1);

code = lines.join('\n');

// 2. Fix createHistogramChart missing brace
code = code.replace(
`            animationDurationUpdate: 80
        }]
    });
let tdaqRateHistory`,
`            animationDurationUpdate: 80
        }]
    });
}

let tdaqRateHistory`
);

fs.writeFileSync('bl4s_event_explorer.html', code);
