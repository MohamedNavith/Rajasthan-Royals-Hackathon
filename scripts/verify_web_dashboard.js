const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 1080 } });

  const errors = [];
  page.on('console', msg => {
    if (msg.type() === 'error') errors.push(msg.text());
  });
  page.on('pageerror', err => errors.push(err.message));

  const indexPath = 'file:///' + path.resolve(__dirname, '..', 'index.html').replace(/\\/g, '/');
  console.log(`Navigating to ${indexPath}...`);
  await page.goto(indexPath, { waitUntil: 'load' });
  await page.waitForTimeout(2000);

  // Take screenshot of overview tab
  await page.screenshot({ path: path.join(__dirname, '..', 'assets', 'dashboard_overview.png'), fullPage: false });
  console.log('Saved dashboard_overview.png');

  // Click on Playing XI tab
  await page.click('#tab-btn-lineup');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(__dirname, '..', 'assets', 'dashboard_lineup.png'), fullPage: false });
  console.log('Saved dashboard_lineup.png');

  // Click on 20-Over Bowling Matrix tab
  await page.click('#tab-btn-bowling');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(__dirname, '..', 'assets', 'dashboard_bowling.png'), fullPage: false });
  console.log('Saved dashboard_bowling.png');

  // Click on Auction Purse & Simulator tab
  await page.click('#tab-btn-budget');
  await page.waitForTimeout(1000);
  await page.screenshot({ path: path.join(__dirname, '..', 'assets', 'dashboard_budget.png'), fullPage: false });
  console.log('Saved dashboard_budget.png');

  console.log(`Verification complete. Console errors count: ${errors.length}`);
  if (errors.length > 0) {
    console.error('Errors found:', errors);
  }

  await browser.close();
})();
