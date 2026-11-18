const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
  });
  const page = await context.newPage();

  // Prime the context by visiting iplt20
  await page.goto('https://www.iplt20.com/teams/rajasthan-royals/squad', { waitUntil: 'domcontentloaded', timeout: 30000 });

  const outputDir = path.join(__dirname, '..', 'assets', 'images', 'players');
  if (!fs.existsSync(outputDir)) fs.mkdirSync(outputDir, { recursive: true });

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

  for (const [filename, url] of Object.entries(playerUrls)) {
    const dest = path.join(outputDir, filename);
    console.log(`Downloading ${filename} via context.request...`);
    try {
      const res = await context.request.get(url);
      if (res.ok()) {
        const body = await res.body();
        fs.writeFileSync(dest, body);
        console.log(`Successfully saved ${filename} (${body.length} bytes)`);
      } else {
        console.error(`Failed ${filename}: status ${res.status()}`);
      }
    } catch (e) {
      console.error(`Error saving ${filename}:`, e.message);
    }
  }

  await browser.close();
}

main().catch(console.error);
