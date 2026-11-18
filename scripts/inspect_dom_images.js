const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  await page.goto('https://www.iplt20.com/teams/rajasthan-royals/squad', { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);

  const images = await page.evaluate(() => {
    const anchors = Array.from(document.querySelectorAll('a[href*="/players/"]'));
    return anchors.slice(0, 3).map(a => {
      const allImgs = Array.from(a.querySelectorAll('img')).map(i => ({ src: i.src, alt: i.alt, className: i.className }));
      return {
        text: a.innerText.replace(/\s+/g, ' ').trim(),
        href: a.href,
        imgs: allImgs
      };
    });
  });

  console.log(JSON.stringify(images, null, 2));

  // Also check visiting one profile page directly
  const profileUrl = 'https://www.iplt20.com/players/786de32e-4a28-48d0-af87-775b1e4ce987/yashasvi-jaiswal';
  console.log('Visiting profile:', profileUrl);
  await page.goto(profileUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
  await page.waitForTimeout(3000);

  const profileImgs = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('img')).map(i => ({ src: i.src, alt: i.alt, className: i.className })).filter(i => i.src.includes('player') || i.src.includes('team-assets') || i.src.includes('content') || i.src.includes('headshot'));
  });

  console.log('Profile images:', JSON.stringify(profileImgs, null, 2));

  await browser.close();
})();
