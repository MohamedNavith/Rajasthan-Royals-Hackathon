const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const teams = [
    'https://www.iplt20.com/teams/sunrisers-hyderabad/squad',
    'https://www.iplt20.com/teams/punjab-kings/squad',
    'https://www.iplt20.com/teams/kolkata-knight-riders/squad',
    'https://www.iplt20.com/teams/delhi-capitals/squad',
    'https://www.iplt20.com/teams/royal-challengers-bengaluru/squad'
  ];

  const outputDir = path.join(__dirname, '..', 'assets', 'images', 'players');
  const found = {};

  for (const url of teams) {
    try {
      console.log(`Checking ${url}...`);
      await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 25000 });
      await page.waitForTimeout(2000);

      const players = await page.evaluate(() => {
        const anchors = Array.from(document.querySelectorAll('a[href*="/players/"]'));
        return anchors.map(a => {
          const name = a.innerText.replace(/\s+/g, ' ').trim();
          const imgs = Array.from(a.querySelectorAll('img')).map(i => i.src);
          const cutout = imgs.find(s => s.includes('.png') && !s.includes('svg'));
          return { name, cutout };
        });
      });

      for (const p of players) {
        const lower = p.name.toLowerCase();
        if (lower.includes('shami') && p.cutout) found['shami.png'] = p.cutout;
        if (lower.includes('pathirana') && p.cutout) found['pathirana.png'] = p.cutout;
        if (lower.includes('coetzee') && p.cutout) found['coetzee.png'] = p.cutout;
        if (lower.includes('karun') && p.cutout) found['karun.png'] = p.cutout;
        if (lower.includes('nair') && p.cutout) found['karun.png'] = p.cutout;
      }
    } catch (e) {
      console.error(e.message);
    }
  }

  console.log('Matches:', JSON.stringify(found, null, 2));

  for (const [filename, imgUrl] of Object.entries(found)) {
    const res = await context.request.get(imgUrl);
    if (res.ok()) {
      const b = await res.body();
      fs.writeFileSync(path.join(outputDir, filename), b);
      console.log(`Saved ${filename} (${b.length} bytes)`);
    }
  }

  await browser.close();
}

main().catch(console.error);
