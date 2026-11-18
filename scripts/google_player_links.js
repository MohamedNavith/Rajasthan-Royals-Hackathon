const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  // Search on iplt20
  const targets = ['shami', 'pathirana', 'coetzee', 'nissanka', 'karun nair'];

  for (const t of targets) {
    console.log(`Searching for ${t}...`);
    await page.goto(`https://www.google.com/search?q=site:iplt20.com/players+${encodeURIComponent(t)}`, { timeout: 20000 });
    const links = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('a[href*="iplt20.com/players/"]')).map(a => a.href);
    });
    console.log(`Links for ${t}:`, links.slice(0, 3));
  }

  await browser.close();
}

main().catch(console.error);
