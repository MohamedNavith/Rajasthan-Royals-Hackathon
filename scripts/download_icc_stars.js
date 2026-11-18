const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

async function main() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const outputDir = path.join(__dirname, '..', 'assets', 'images', 'players');

  const targets = [
    {
      file: 'nissanka.png',
      url: 'https://images.icc-cricket.com/image/upload/t_player-headshot-portrait-lg-webp/prd/assets/players/13203/66368.png'
    },
    {
      file: 'coetzee.png',
      url: 'https://images.icc-cricket.com/image/upload/t_player-headshot-portrait-lg-webp/prd/assets/players/6122/67443.png'
    }
  ];

  for (const t of targets) {
    console.log(`Downloading ${t.file} from ${t.url}...`);
    try {
      const res = await context.request.get(t.url);
      if (res.ok()) {
        const body = await res.body();
        fs.writeFileSync(path.join(outputDir, t.file), body);
        console.log(`Saved ${t.file} (${body.length} bytes)`);
      } else {
        console.error(`Failed ${t.file}: status ${res.status()}`);
      }
    } catch (e) {
      console.error(`Error saving ${t.file}:`, e.message);
    }
  }

  await browser.close();
}

main().catch(console.error);
