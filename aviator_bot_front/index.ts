import playwright from "playwright";
import fs from "fs";


(async () => {
    const browser = await playwright.chromium.launch({headless:false});
    const context = await browser.newContext();
    const page = await context.newPage();
    //page.on('domcontentloaded', (p) => console.log(`Loaded ${p.url()}`));
    await page.goto('https://betplay.com.co/slots');
    await page.waitForURL("**/slots/launchGame?gameCode=SPB_aviator**", {timeout: 50000})
    console.log("estamos en aviator")
    try {
        await page.locator('.game-logo').waitFor({
            timeout: 50000
        });
        //await page.waitForFunction(() => document.title === 'Aviator')
        console.log("encontramos el logo")
      } catch (e) {
        if (e instanceof playwright.errors.TimeoutError) {
          console.log("error timeout")
        }
      }
    await page.screenshot({ path: 'example.png' });
    console.log("screenshot")
    //await browser.close();
  })();