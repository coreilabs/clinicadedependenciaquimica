const {chromium} = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch({executablePath:'C:/Program Files/Google/Chrome/Application/chrome.exe'});
  const page = await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
  await page.goto('http://127.0.0.1:8765/',{waitUntil:'networkidle'});
  await page.evaluate(async () => {for(const i of document.images) i.loading='eager'; await Promise.all([...document.images].map(i=>i.decode().catch(()=>{})));});
  await page.screenshot({path:path.join(__dirname,'validation/mobile-top.png')});
  await page.locator('#unidades').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(__dirname,'validation/mobile-units.png')});
  await page.locator('#contato').scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(__dirname,'validation/mobile-contact.png')});
  await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:path.join(__dirname,'validation/mobile.png'),fullPage:true});
  console.log(await page.locator('main > section').count(), 'seções na página inicial');
  await browser.close();
})();
