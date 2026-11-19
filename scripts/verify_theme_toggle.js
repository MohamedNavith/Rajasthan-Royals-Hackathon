const { chromium } = require('playwright');
const path = require('path');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  
  const fileUrl = 'file:///' + path.resolve('index.html').replace(/\\/g, '/');
  console.log('Opening:', fileUrl);
  
  await page.goto(fileUrl, { waitUntil: 'networkidle' });
  
  // 1. Initial Mode (Dark by default or light)
  await page.screenshot({ path: 'assets/mode_1_initial.png', fullPage: false });
  console.log('Saved assets/mode_1_initial.png');
  
  // 2. Click Theme Toggle Button
  const toggleBtn = await page.$('#themeToggleBtn');
  if (toggleBtn) {
    await toggleBtn.click();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'assets/mode_2_toggled.png', fullPage: false });
    console.log('Saved assets/mode_2_toggled.png');
  } else {
    console.error('themeToggleBtn not found!');
  }
  
  // 3. Scroll to Connect Section
  const connectSec = await page.$('#connect-analyst-section');
  if (connectSec) {
    await connectSec.scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);
    await page.screenshot({ path: 'assets/connect_section.png', fullPage: false });
    console.log('Saved assets/connect_section.png');
  } else {
    console.error('connect-analyst-section not found!');
  }
  
  await browser.close();
  console.log('Verification script completed!');
})();
