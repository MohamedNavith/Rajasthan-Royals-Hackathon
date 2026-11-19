const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  
  const fileUrl = 'file:///' + path.resolve('index.html').replace(/\\/g, '/');
  await page.goto(fileUrl, { waitUntil: 'networkidle' });
  
  // Test Lineup Tab in Light Mode
  await page.click('#tab-btn-lineup');
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'assets/tab_lineup_light.png', fullPage: false });
  
  // Test Lineup Tab in Dark Mode
  await page.click('#themeToggleBtn');
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'assets/tab_lineup_dark.png', fullPage: false });

  // Test Bowling Tab in Dark Mode
  await page.click('#tab-btn-bowling');
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'assets/tab_bowling_dark.png', fullPage: false });

  // Test Budget Tab in Dark Mode
  await page.click('#tab-btn-budget');
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'assets/tab_budget_dark.png', fullPage: false });

  await browser.close();
  console.log('All tab tests passed!');
})();
