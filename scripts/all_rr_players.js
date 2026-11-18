const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://www.iplt20.com/teams/rajasthan-royals/squad', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);

  const players = await page.evaluate(() => {
    const anchors = Array.from(document.querySelectorAll('a[href*="/players/"]'));
    return anchors.map(a => {
      const name = a.innerText.replace(/\s+/g, ' ').trim();
      const imgs = Array.from(a.querySelectorAll('img')).map(i => i.src);
      return { name, href: a.href, imgs };
    });
  });

  console.log(JSON.stringify(players, null, 2));
  await browser.close();
})();
