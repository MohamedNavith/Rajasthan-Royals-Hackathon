const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function main() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const outputDir = path.join(__dirname, '..', 'assets', 'images', 'players');
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

  const squadUrls = [
    { team: 'RR', url: 'https://www.iplt20.com/teams/rajasthan-royals/squad' },
    { team: 'CSK', url: 'https://www.iplt20.com/teams/chennai-super-kings/squad' },
    { team: 'LSG', url: 'https://www.iplt20.com/teams/lucknow-super-giants/squad' },
    { team: 'MI', url: 'https://www.iplt20.com/teams/mumbai-indians/squad' },
    { team: 'GT', url: 'https://www.iplt20.com/teams/gujarat-titans/squad' }
  ];

  const targetMap = {
    'yashasvi jaiswal': 'jaiswal.png',
    'vaibhav sooryavanshi': 'sooryavanshi.png',
    'riyan parag': 'parag.png',
    'dhruv jurel': 'jurel.png',
    'donovan ferreira': 'ferreira.png',
    'ravindra jadeja': 'jadeja.png',
    'ravi bishnoi': 'bishnoi.png',
    'gerald coetzee': 'coetzee.png',
    'matheesha pathirana': 'pathirana.png',
    'mohammad shami': 'shami.png',
    'mohammed shami': 'shami.png',
    'jofra archer': 'archer.png',
    'sandeep sharma': 'sandeep.png',
    'karun nair': 'karun.png',
    'nandre burger': 'burger.png'
  };

  const found = {};

  for (const item of squadUrls) {
    console.log(`Checking ${item.team}: ${item.url}`);
    try {
      await page.goto(item.url, { waitUntil: 'domcontentloaded', timeout: 25000 });
      await page.waitForTimeout(3000);

      // Extract all player elements
      const players = await page.evaluate(() => {
        const anchors = Array.from(document.querySelectorAll('a[href*="/players/"]'));
        return anchors.map(a => {
          const img = a.querySelector('img');
          return {
            name: a.innerText.replace(/\s+/g, ' ').trim().toLowerCase(),
            href: a.href,
            imgSrc: img ? img.src : null
          };
        });
      });

      console.log(`Found ${players.length} player anchors on ${item.team}`);

      for (const p of players) {
        for (const [key, filename] of Object.entries(targetMap)) {
          if (!found[filename] && p.name.includes(key)) {
            console.log(`Matched ${key} -> ${p.name} (img: ${p.imgSrc ? 'yes' : 'no'})`);
            if (p.imgSrc) {
              found[filename] = { name: p.name, imgSrc: p.imgSrc, href: p.href };
            }
          }
        }
      }
    } catch (e) {
      console.error(`Error loading ${item.team}:`, e.message);
    }
  }

  console.log('Summary of matched players:');
  console.log(JSON.stringify(found, null, 2));

  // Now for each matched player, download the image or take a screenshot of the player's card
  for (const [filename, info] of Object.entries(found)) {
    const dest = path.join(outputDir, filename);
    if (fs.existsSync(dest) && fs.statSync(dest).size > 1000) {
      console.log(`Already exists: ${filename}`);
      continue;
    }
    console.log(`Downloading ${filename} from ${info.imgSrc}...`);
    try {
      const response = await page.goto(info.imgSrc, { timeout: 15000 });
      if (response && response.ok()) {
        const buffer = await response.body();
        fs.writeFileSync(dest, buffer);
        console.log(`Saved ${filename} (${buffer.length} bytes)`);
      } else {
        console.warn(`Failed to download ${filename}, status: ${response ? response.status() : 'none'}`);
      }
    } catch (err) {
      console.error(`Error saving ${filename}:`, err.message);
    }
  }

  await browser.close();
}

main().catch(console.error);
