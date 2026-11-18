const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://www.iplt20.com/players/0170bba0-ca72-4022-9351-3556801aed49/mohammed-shami', { waitUntil: 'networkidle', timeout: 30000 });

  const imgs = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('img')).map(i => ({ src: i.src, alt: i.alt, className: i.className, width: i.width, height: i.height }));
  });

  console.log('All images on Shami profile:');
  console.log(JSON.stringify(imgs, null, 2));

  // Let's also check if we can take a screenshot of the player's hero section
  const hero = await page.$('.player-hero, [class*="hero"], [class*="profile"]');
  if (hero) {
    console.log('Hero section found!');
  }

  await browser.close();
})();
