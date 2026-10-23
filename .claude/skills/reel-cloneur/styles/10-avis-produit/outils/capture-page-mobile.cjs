// Style n°10 « Avis produit » : capture d'une page PUBLIQUE (sans compte, navigation privée, aucun
// clic, aucun cookie accepté ; le bandeau de cookies est seulement masqué à l'image) en PNG pleine
// page, largeur mobile : 432 px CSS × densité 2,5 = 1080 px, la largeur des pièces du kit.
// Ce n'est pas un outil du dossier Monteur IA : utilisé pour l'épreuve du style (puppeteer-core de
// node_modules/ et Google Chrome installé), à intégrer ou non.
// Usage, depuis le dossier Monteur IA :
//   PPTR="$PWD/node_modules/puppeteer-core" node <kit>/outils/capture-page-mobile.cjs <url> <sortie.png> [432] [2.5] [hauteurMax CSS=9000]
const puppeteer = require(process.env.PPTR);
(async () => {
  const [url, out, w = "432", dpr = "2.5", hmax = "9000"] = process.argv.slice(2);
  const browser = await puppeteer.launch({
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    headless: true,
    args: ["--incognito", "--no-first-run", "--disable-extensions"],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: +w, height: 932, deviceScaleFactor: +dpr, isMobile: true, hasTouch: true });
  await page.setUserAgent("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1");
  await page.goto(url, { waitUntil: "networkidle2", timeout: 90000 });
  // défile doucement pour charger les images paresseuses, puis revient en haut
  const H = await page.evaluate(() => document.documentElement.scrollHeight);
  for (let y = 0; y < Math.min(H, +hmax); y += 600) {
    await page.evaluate((y) => window.scrollTo(0, y), y);
    await new Promise((r) => setTimeout(r, 350));
  }
  // Bandeau de cookies : masqué à l'image (aucun clic, rien d'accepté ni de refusé).
  await page.evaluate(() => {
    for (const el of document.querySelectorAll("body *")) {
      const st = getComputedStyle(el);
      if ((st.position === "fixed" || st.position === "sticky") && /cookie/i.test(el.textContent || "") && (el.textContent || "").length < 2000) el.style.setProperty("display", "none", "important");
    }
  });
  await page.evaluate(() => window.scrollTo(0, 0));
  await new Promise((r) => setTimeout(r, 1500));
  const h = Math.min(await page.evaluate(() => document.documentElement.scrollHeight), +hmax);
  await page.screenshot({ path: out, clip: { x: 0, y: 0, width: +w, height: h }, captureBeyondViewport: true });
  console.log(JSON.stringify({ url, out, cssWidth: +w, cssHeight: h, title: await page.title() }));
  await browser.close();
})().catch((e) => { console.error(e.message); process.exit(1); });
