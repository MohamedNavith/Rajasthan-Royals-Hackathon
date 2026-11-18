const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const https = require('https');

async function downloadUrl(url, dest) {
  return new Promise((resolve, reject) => {
    https.get(url, (res) => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        return downloadUrl(res.headers.location, dest).then(resolve).catch(reject);
      }
      if (res.statusCode !== 200) {
        return reject(new Error(`Status ${res.statusCode}`));
      }
      const stream = fs.createWriteStream(dest);
      res.pipe(stream);
      stream.on('finish', () => {
        stream.close();
        resolve(true);
      });
      stream.on('error', reject);
    }).on('error', reject);
  });
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const outputDir = path.join(__dirname, '..', 'assets', 'images', 'players');
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

  // Exact known IPL CDN URLs for RR players
  const playerUrls = {
    'jaiswal.png': 'https://www.iplt20.com/_next/image?url=%2Fapi%2Fteam-assets%3Fpathname%3Dplayer%252F8903%252F1558%252F68314.png%26brand%3Dipl&w=750&q=75',
    'sooryavanshi.png': 'https://www.iplt20.com/_next/image?url=%2Fapi%2Fteam-assets%3Fpathname%3Dplayer%252F8903%252F1558%252F83313.png%26brand%3Dipl&w=750&q=75',
    'parag.png': 'https://www.iplt20.com/_next/image?url=%2Fapi%2Fteam-assets%3Fpathname%3Dplayer%252F8903%252F1558%252F65476.png%26brand%3Dipl&w=750&q=75',
    'jurel.png': 'https://www.iplt20.com/_next/image?url=%2Fapi%2Fteam-assets%3Fpathname%3Dplayer%252F8903%252F1558%252F71456.png%26brand%3Dipl&w=750&q=75',
    'ferreira.png': 'https://www.iplt20.com/_next/image?url=%2Fapi%2Fteam-assets%3Fpathname%3Dplayer%252F8903%252F1558%252F68473.png%26brand%3Dipl&w=750&q=75',
    'jadeja.png': 'https://www.iplt20.com/_next/image?url=%2Fapi%2Fteam-assets%3Fpathname%3Dplayer%252F8903%252F1558%252F13143.png%26brand%3Dipl&w=750&q=75',
    'archer.png': 'https://www.iplt20.com/_next/image?url=%2Fapi%2Fteam-assets%3Fpathname%3Dplayer%252F8903%252F1558%252F28503.png%26brand%3Dipl&w=750&q=75',
    'bishnoi.png': 'https://www.iplt20.com/_next/image?url=%2Fapi%2Fteam-assets%3Fpathname%3Dplayer%252F8903%252F1558%252F70430.png%26brand%3Dipl&w=750&q=75',
    'burger.png': 'https://www.iplt20.com/_next/image?url=%2Fapi%2Fteam-assets%3Fpathname%3Dplayer%252F8903%252F1558%252F52827.png%26brand%3Dipl&w=750&q=75',
    'sandeep.png': 'https://www.iplt20.com/_next/image?url=%2Fapi%2Fteam-assets%3Fpathname%3Dplayer%252F8903%252F1558%252F15660.png%26brand%3Dipl&w=750&q=75'
  };

  // Now search for Shami, Pathirana, Coetzee, Karun Nair
  const otherSearches = [
    { key: 'shami.png', teamUrl: 'https://www.iplt20.com/teams/lucknow-super-giants/squad', target: 'shami' },
    { key: 'pathirana.png', teamUrl: 'https://www.iplt20.com/teams/chennai-super-kings/squad', target: 'pathirana' },
    { key: 'coetzee.png', teamUrl: 'https://www.iplt20.com/teams/mumbai-indians/squad', target: 'coetzee' },
    { key: 'karun.png', teamUrl: 'https://www.iplt20.com/teams/lucknow-super-giants/squad', target: 'karun' }
  ];

  for (const item of otherSearches) {
    try {
      console.log(`Searching for ${item.target} on ${item.teamUrl}...`);
      await page.goto(item.teamUrl, { waitUntil: 'domcontentloaded', timeout: 25000 });
      await page.waitForTimeout(2000);
      const imgUrl = await page.evaluate((target) => {
        const anchors = Array.from(document.querySelectorAll('a[href*="/players/"]'));
        for (const a of anchors) {
          if (a.innerText.toLowerCase().includes(target)) {
            const img = a.querySelector('img[alt]');
            if (img && img.src && !img.src.includes('svg')) return img.src;
            const all = Array.from(a.querySelectorAll('img')).map(i => i.src);
            const found = all.find(s => s.includes('.png') || s.includes('player'));
            if (found) return found;
          }
        }
        return null;
      }, item.target);

      if (imgUrl) {
        console.log(`Found image for ${item.key}: ${imgUrl}`);
        playerUrls[item.key] = imgUrl;
      } else {
        console.log(`Could not find ${item.target} on ${item.teamUrl}`);
      }
    } catch (e) {
      console.error(`Error searching ${item.target}:`, e.message);
    }
  }

  // Also check Gujarat Titans squad for Shami if not found on LSG
  if (!playerUrls['shami.png']) {
    try {
      console.log('Checking Gujarat Titans for Shami...');
      await page.goto('https://www.iplt20.com/teams/gujarat-titans/squad', { waitUntil: 'domcontentloaded', timeout: 25000 });
      await page.waitForTimeout(2000);
      const shamiImg = await page.evaluate(() => {
        const anchors = Array.from(document.querySelectorAll('a[href*="/players/"]'));
        for (const a of anchors) {
          if (a.innerText.toLowerCase().includes('shami')) {
            const imgs = Array.from(a.querySelectorAll('img')).map(i => i.src);
            return imgs.find(s => s.includes('.png') || s.includes('player'));
          }
        }
        return null;
      });
      if (shamiImg) playerUrls['shami.png'] = shamiImg;
    } catch (e) {}
  }

  // Download all through Playwright page requests to retain session headers
  for (const [filename, imgUrl] of Object.entries(playerUrls)) {
    const dest = path.join(outputDir, filename);
    console.log(`Fetching ${filename} via page.goto...`);
    try {
      const resp = await page.goto(imgUrl, { timeout: 20000 });
      if (resp && resp.ok()) {
        const buf = await resp.body();
        fs.writeFileSync(dest, buf);
        console.log(`Successfully saved ${filename} (${buf.length} bytes)`);
      } else {
        console.warn(`Failed response for ${filename}: ${resp ? resp.status() : 'null'}`);
      }
    } catch (err) {
      console.error(`Error fetching ${filename}:`, err.message);
    }
  }

  await browser.close();
  console.log('All image downloads completed.');
})();
