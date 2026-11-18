const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();
  const outputDir = path.join(__dirname, '..', 'assets', 'images', 'players');

  // 1. Test Shami on GT CDN
  console.log('Testing GT Shami CDN...');
  try {
    const res = await context.request.get('https://www.gujarattitansipl.com/static-assets/images/players/28994.png');
    if (res.ok()) {
      const b = await res.body();
      fs.writeFileSync(path.join(outputDir, 'shami.png'), b);
      console.log(`Saved shami.png from GT (${b.length} bytes)`);
    } else {
      console.log('GT Shami status:', res.status());
    }
  } catch (e) {
    console.error('Error fetching Shami from GT:', e.message);
  }

  // 2. Search for Coetzee on Mumbai Indians squad / archive
  console.log('Searching for Coetzee on Mumbai Indians...');
  try {
    await page.goto('https://www.mumbaiindians.com/players', { waitUntil: 'domcontentloaded', timeout: 25000 });
    await page.waitForTimeout(2000);
    const coetzeeImg = await page.evaluate(() => {
      const imgs = Array.from(document.querySelectorAll('img'));
      const c = imgs.find(i => (i.alt && i.alt.toLowerCase().includes('coetzee')) || (i.src && i.src.toLowerCase().includes('coetzee')));
      return c ? c.src : null;
    });
    if (coetzeeImg) {
      console.log('Found Coetzee image on MI site:', coetzeeImg);
      const res = await context.request.get(coetzeeImg);
      if (res.ok()) {
        const b = await res.body();
        fs.writeFileSync(path.join(outputDir, 'coetzee.png'), b);
        console.log(`Saved coetzee.png (${b.length} bytes)`);
      }
    } else {
      console.log('Coetzee not found on MI players page.');
    }
  } catch (e) {
    console.error('MI Coetzee search:', e.message);
  }

  // 3. Search for Nissanka and Coetzee across cricket APIs / wikimedia / cricinfo
  console.log('Searching for Nissanka...');
  try {
    await page.goto('https://en.wikipedia.org/wiki/Pathum_Nissanka', { waitUntil: 'domcontentloaded', timeout: 25000 });
    const imgUrl = await page.evaluate(() => {
      const infobox = document.querySelector('.infobox');
      if (infobox) {
        const img = infobox.querySelector('img');
        if (img) return img.src;
      }
      return null;
    });
    if (imgUrl) {
      console.log('Found Nissanka wikipedia img:', imgUrl);
      const res = await context.request.get(imgUrl);
      if (res.ok()) {
        const b = await res.body();
        fs.writeFileSync(path.join(outputDir, 'nissanka.png'), b);
        console.log(`Saved nissanka.png (${b.length} bytes)`);
      }
    }
  } catch (e) {
    console.error('Nissanka wiki:', e.message);
  }

  // Check if Coetzee is on wikipedia if not found on MI
  if (!fs.existsSync(path.join(outputDir, 'coetzee.png')) || fs.statSync(path.join(outputDir, 'coetzee.png')).size < 5000) {
    try {
      console.log('Searching Coetzee on wikipedia...');
      await page.goto('https://en.wikipedia.org/wiki/Gerald_Coetzee', { waitUntil: 'domcontentloaded', timeout: 25000 });
      const imgUrl = await page.evaluate(() => {
        const infobox = document.querySelector('.infobox');
        if (infobox) {
          const img = infobox.querySelector('img');
          if (img) return img.src;
        }
        return null;
      });
      if (imgUrl) {
        console.log('Found Coetzee wiki img:', imgUrl);
        const res = await context.request.get(imgUrl);
        if (res.ok()) {
          const b = await res.body();
          fs.writeFileSync(path.join(outputDir, 'coetzee.png'), b);
          console.log(`Saved coetzee.png (${b.length} bytes)`);
        }
      }
    } catch (e) {
      console.error('Coetzee wiki:', e.message);
    }
  }

  // Check if Shami is on wikipedia if GT CDN didn't work
  if (!fs.existsSync(path.join(outputDir, 'shami.png')) || fs.statSync(path.join(outputDir, 'shami.png')).size < 5000) {
    try {
      console.log('Searching Shami on wikipedia...');
      await page.goto('https://en.wikipedia.org/wiki/Mohammed_Shami', { waitUntil: 'domcontentloaded', timeout: 25000 });
      const imgUrl = await page.evaluate(() => {
        const infobox = document.querySelector('.infobox');
        if (infobox) {
          const img = infobox.querySelector('img');
          if (img) return img.src;
        }
        return null;
      });
      if (imgUrl) {
        console.log('Found Shami wiki img:', imgUrl);
        const res = await context.request.get(imgUrl);
        if (res.ok()) {
          const b = await res.body();
          fs.writeFileSync(path.join(outputDir, 'shami.png'), b);
          console.log(`Saved shami.png (${b.length} bytes)`);
        }
      }
    } catch (e) {
      console.error('Shami wiki:', e.message);
    }
  }

  await browser.close();
}

main().catch(console.error);
