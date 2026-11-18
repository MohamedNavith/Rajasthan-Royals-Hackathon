const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.goto('https://en.wikipedia.org/wiki/Pathum_Nissanka', { waitUntil: 'domcontentloaded', timeout: 25000 });
  const imgs = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('img')).map(i => ({ src: i.src, width: i.naturalWidth || i.width, height: i.naturalHeight || i.height }));
  });
  console.log('Nissanka wiki images:', imgs);

  // If Wikipedia doesn't have a large headshot of Nissanka, let's search ESPNcricinfo
  await page.goto('https://www.espncricinfo.com/cricketers/pathum-nissanka-1028655', { waitUntil: 'domcontentloaded', timeout: 25000 });
  await page.waitForTimeout(3000);
  const cricinfoImgs = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('img')).map(i => ({ src: i.src, alt: i.alt, width: i.width, height: i.height })).filter(i => (i.alt && i.alt.toLowerCase().includes('nissanka')) || (i.src && i.src.toLowerCase().includes('player')));
  });
  console.log('Cricinfo images:', cricinfoImgs);

  if (cricinfoImgs.length > 0) {
    const res = await context.request.get(cricinfoImgs[0].src);
    if (res.ok()) {
      const b = await res.body();
      fs.writeFileSync(path.join(__dirname, '..', 'assets', 'images', 'players', 'nissanka.png'), b);
      console.log('Saved nissanka.png from cricinfo:', b.length);
    }
  }

  await browser.close();
}

main().catch(console.error);
