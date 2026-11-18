const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const queries = [
    { key: 'shami', url: 'https://www.iplt20.com/players/0170bba0-ca72-4022-9351-3556801aed49/mohammed-shami', file: 'shami.png' },
    { key: 'pathirana', url: 'https://www.iplt20.com/players/d193d56a-12e0-40c2-9d32-2fcb4395066a/matheesha-pathirana', file: 'pathirana.png' },
    { key: 'coetzee', url: 'https://www.iplt20.com/players/a1f592fc-c7ae-4f76-880c-7b8c2ecda1e3/gerald-coetzee', file: 'coetzee.png' }
  ];

  const outputDir = path.join(__dirname, '..', 'assets', 'images', 'players');

  for (const q of queries) {
    try {
      console.log(`Checking profile for ${q.key}: ${q.url}`);
      await page.goto(q.url, { waitUntil: 'domcontentloaded', timeout: 25000 });
      await page.waitForTimeout(2500);

      const imgUrl = await page.evaluate(() => {
        const imgs = Array.from(document.querySelectorAll('img')).map(i => i.src);
        return imgs.find(s => s.includes('/api/team-assets?pathname=player') || (s.includes('team-assets') && s.includes('.png')) || s.includes('_next/image?url='));
      });

      if (imgUrl) {
        console.log(`Found image URL for ${q.key}: ${imgUrl}`);
        const res = await context.request.get(imgUrl);
        if (res.ok()) {
          const body = await res.body();
          fs.writeFileSync(path.join(outputDir, q.file), body);
          console.log(`Saved ${q.file} (${body.length} bytes)`);
        }
      } else {
        console.log(`No image URL found on page for ${q.key}`);
      }
    } catch (e) {
      console.error(`Error on ${q.key}:`, e.message);
    }
  }

  await browser.close();
}

main().catch(console.error);
