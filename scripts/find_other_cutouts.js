const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const squads = [
    { name: 'LSG', url: 'https://www.iplt20.com/teams/lucknow-super-giants/squad' },
    { name: 'CSK', url: 'https://www.iplt20.com/teams/chennai-super-kings/squad' },
    { name: 'MI', url: 'https://www.iplt20.com/teams/mumbai-indians/squad' },
    { name: 'GT', url: 'https://www.iplt20.com/teams/gujarat-titans/squad' }
  ];

  const results = {};

  for (const s of squads) {
    console.log(`Loading ${s.name}...`);
    await page.goto(s.url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(2500);

    const data = await page.evaluate(() => {
      const anchors = Array.from(document.querySelectorAll('a[href*="/players/"]'));
      return anchors.map(a => {
        const text = a.innerText.replace(/\s+/g, ' ').trim();
        const imgs = Array.from(a.querySelectorAll('img')).map(i => ({ src: i.src, alt: i.alt }));
        return { text, href: a.href, imgs };
      });
    });

    for (const d of data) {
      const lower = d.text.toLowerCase();
      if (lower.includes('shami') || lower.includes('pathirana') || lower.includes('coetzee') || lower.includes('nair') || lower.includes('nissanka') || lower.includes('rickelton')) {
        console.log(`FOUND: ${d.text}`);
        const cutout = d.imgs.find(i => i.src && i.src.includes('.png') && !i.src.includes('svg'));
        if (cutout) {
          results[d.text] = cutout.src;
          console.log(` -> URL: ${cutout.src}`);
        }
      }
    }
  }

  console.log('Final results:', JSON.stringify(results, null, 2));

  const outputDir = path.join(__dirname, '..', 'assets', 'images', 'players');
  for (const [name, url] of Object.entries(results)) {
    let filename = '';
    const lower = name.toLowerCase();
    if (lower.includes('shami')) filename = 'shami.png';
    else if (lower.includes('pathirana')) filename = 'pathirana.png';
    else if (lower.includes('coetzee')) filename = 'coetzee.png';
    else if (lower.includes('nair')) filename = 'karun.png';
    
    if (filename) {
      const res = await context.request.get(url);
      if (res.ok()) {
        const b = await res.body();
        fs.writeFileSync(path.join(outputDir, filename), b);
        console.log(`Saved ${filename} (${b.length} bytes)`);
      }
    }
  }

  await browser.close();
}

main().catch(console.error);
