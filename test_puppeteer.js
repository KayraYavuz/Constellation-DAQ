const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: 'new' });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.error('PAGE ERROR:', err));
  
  await page.goto('http://localhost:5050');
  await page.waitForTimeout(1000);
  
  console.log("Clicking DFP panel...");
  await page.evaluate(() => {
    document.querySelector('.tree-view-item[data-view="dfp_panel"]').click();
  });
  
  await page.waitForTimeout(1000);
  console.log("Active panels:", await page.evaluate(() => Object.keys(activePanels)));
  
  await browser.close();
})();
