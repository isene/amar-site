// Screenshots of chosen pages at desktop and phone width.
// Usage: node tools/shots.js <outdir> <base-url> page.html [page.html ...]
// A page name ending in "!" is shot full length; add "@dark" for dark mode,
// "+menu" to open the phone menu, "?q=word" to type a search.
const { chromium } = require("playwright");
(async () => {
  const [out, base, ...pages] = process.argv.slice(2);
  const browser = await chromium.launch();
  for (const [tag, vp] of [["desk", { width: 1400, height: 950 }], ["phone", { width: 390, height: 844 }]]) {
    for (let p of pages) {
      const dark = p.includes("@dark"); p = p.replace("@dark", "");
      const menu = p.includes("+menu"); p = p.replace("+menu", "");
      const [pth, q] = p.split("?q="); p = pth;
      const full = p.endsWith("!"); p = p.replace(/!$/, "");
      const ctx = await browser.newContext({ viewport: vp, deviceScaleFactor: tag === "phone" ? 2 : 1,
        colorScheme: dark ? "dark" : "light" });
      const page = await ctx.newPage();
      await page.goto(base + p, { waitUntil: "networkidle" });
      await page.evaluate(() => document.fonts.ready);
      if (menu && tag === "phone") await page.click(".menu-btn");
      if (q) { await page.fill("#q", q); await page.waitForTimeout(400); }
      const name = `${out}/${tag}-${p.replace(/[^A-Za-z0-9]+/g, "_")}${dark ? "-dark" : ""}${menu ? "-menu" : ""}${q ? "-q" : ""}.png`;
      await page.screenshot({ path: name, fullPage: full });
      await ctx.close();
    }
  }
  await browser.close();
})();
