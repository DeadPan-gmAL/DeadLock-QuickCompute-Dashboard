const fs = require("fs");
const path = require("path");
const { pathToFileURL } = require("url");
const { chromium } = require("playwright");

const root = path.resolve(__dirname, "..");
const htmlPath = path.join(root, "deadlock_hero_level_curves.html");
const outDir = path.join(root, "render-check", "screenshots");
const browserCandidates = [
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files\\Microsoft\\Edge\\Application\\msedge.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
];

function browserLaunchOptions() {
  const executablePath = browserCandidates.find((candidate) => fs.existsSync(candidate));
  return executablePath
    ? { headless: true, executablePath }
    : { headless: true };
}

async function inspectPage(page) {
  const errors = [];
  page.on("pageerror", (err) => errors.push(`pageerror: ${err.message}`));
  page.on("console", (msg) => {
    if (msg.type() === "error") errors.push(`console: ${msg.text()}`);
  });

  await page.addInitScript(() => localStorage.setItem("deadlock-level-tool-language", "zh"));
  await page.goto(pathToFileURL(htmlPath).href, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("#chart path.curve", { timeout: 30000 });
  await page.waitForSelector("#skillInspector .skill-panel", { timeout: 30000 });
  await page.waitForSelector("#versionLabel", { timeout: 30000 });
  await page.evaluate(() => document.fonts?.ready);

  const beforeModal = await page.evaluate(() => ({
    title: document.title,
    h1: document.querySelector("h1")?.textContent || "",
    versionLabel: document.querySelector("#versionLabel")?.textContent || "",
    latestAsset: document.querySelector("#versionLatest")?.textContent || "",
    fontLoaded: document.fonts?.check('16px "Deadlock WenKai"') || false,
    chartCurves: document.querySelectorAll("#chart path.curve").length,
    skillCards: document.querySelectorAll("#skillInspector .skill-panel").length,
    buildRows: document.querySelectorAll("#buildRows tr").length,
    crossingRows: document.querySelectorAll("#crossingRows tr").length,
    selectedCount: document.querySelector("#selectedCount")?.textContent || "",
    firstHero: document.querySelector("#heroList .check span:last-child")?.textContent || "",
    firstAbility: document.querySelector("#abilityControls .ability b")?.textContent || "",
    firstItem: document.querySelector("#itemList .item b")?.textContent || "",
  }));

  await page.click("#openVersionLog");
  await page.waitForFunction(() => !document.querySelector("#versionModal")?.hidden, null, { timeout: 10000 });
  const modal = await page.evaluate(() => ({
    visible: !document.querySelector("#versionModal")?.hidden,
    cards: document.querySelectorAll("#versionModal .version-card").length,
    logEntries: document.querySelectorAll("#versionModal .log-entry").length,
    sourceRows: document.querySelectorAll("#versionModal .source-table tbody tr").length,
    text: document.querySelector("#versionModal")?.textContent?.slice(0, 300) || "",
  }));

  await page.click("#closeVersionLog");
  await page.click("#langToggle");
  await page.waitForFunction(() => document.documentElement.lang === "en", null, { timeout: 10000 });
  await page.waitForSelector("#chart path.curve", { timeout: 30000 });
  const english = await page.evaluate(() => ({
    title: document.title,
    h1: document.querySelector("h1")?.textContent || "",
    langButton: document.querySelector("#langToggle")?.textContent || "",
    chartTitle: document.querySelector("#chartTitle")?.textContent || "",
    versionButton: document.querySelector("#openVersionLog")?.textContent || "",
    attributeLabel: document.querySelector("label[for='attribute']")?.textContent || "",
    skillCards: document.querySelectorAll("#skillInspector .skill-panel").length,
    firstHero: document.querySelector("#heroList .check span:last-child")?.textContent || "",
    firstAbility: document.querySelector("#abilityControls .ability b")?.textContent || "",
    firstItem: document.querySelector("#itemList .item b")?.textContent || "",
  }));

  return { beforeModal, modal, english, errors };
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch(browserLaunchOptions());
  const desktop = await browser.newPage({ viewport: { width: 1440, height: 1100 }, deviceScaleFactor: 1 });
  const desktopResult = await inspectPage(desktop);
  const desktopShot = path.join(outDir, "deadlock-desktop.png");
  await desktop.screenshot({ path: desktopShot, fullPage: true });

  await desktop.click("#openVersionLog");
  await desktop.waitForFunction(() => !document.querySelector("#versionModal")?.hidden, null, { timeout: 10000 });
  const modalShot = path.join(outDir, "deadlock-version-modal.png");
  await desktop.screenshot({ path: modalShot, fullPage: false });
  await desktop.click("#closeVersionLog");

  const mobile = await browser.newPage({ viewport: { width: 390, height: 900 }, isMobile: true, deviceScaleFactor: 2 });
  await mobile.addInitScript(() => localStorage.setItem("deadlock-level-tool-language", "zh"));
  await mobile.goto(pathToFileURL(htmlPath).href, { waitUntil: "domcontentloaded" });
  await mobile.waitForSelector("#chart path.curve", { timeout: 30000 });
  await mobile.waitForSelector("#skillInspector .skill-panel", { timeout: 30000 });
  const mobileResult = await mobile.evaluate(() => ({
    h1: document.querySelector("h1")?.textContent || "",
    chartCurves: document.querySelectorAll("#chart path.curve").length,
    skillCards: document.querySelectorAll("#skillInspector .skill-panel").length,
    versionButton: document.querySelector("#openVersionLog")?.textContent || "",
    firstHero: document.querySelector("#heroList .check span:last-child")?.textContent || "",
  }));
  const mobileShot = path.join(outDir, "deadlock-mobile.png");
  await mobile.screenshot({ path: mobileShot, fullPage: true });

  await browser.close();

  const result = {
    desktop: desktopResult,
    mobile: mobileResult,
    screenshots: {
      desktop: desktopShot,
      versionModal: modalShot,
      mobile: mobileShot,
    },
  };

  const failures = [];
  if (!desktopResult.beforeModal.h1.includes("Deadlock 英雄数值控制台")) failures.push("desktop h1 missing Chinese title");
  if (!desktopResult.beforeModal.firstHero.includes("艾布拉姆斯")) failures.push(`desktop first hero not localized: ${desktopResult.beforeModal.firstHero}`);
  if (!desktopResult.beforeModal.firstAbility.includes("汲取生命")) failures.push(`desktop first ability not localized: ${desktopResult.beforeModal.firstAbility}`);
  if (!desktopResult.beforeModal.firstItem.includes("额外充能")) failures.push(`desktop first item not localized: ${desktopResult.beforeModal.firstItem}`);
  if (!desktopResult.beforeModal.fontLoaded) failures.push("Deadlock WenKai font did not load");
  if (!desktopResult.english.h1.includes("Deadlock Hero Stat Console")) failures.push("English h1 missing after language toggle");
  if (!desktopResult.english.firstHero.includes("Abrams")) failures.push(`English first hero missing after language toggle: ${desktopResult.english.firstHero}`);
  if (!desktopResult.english.firstAbility.includes("Siphon Life")) failures.push(`English first ability missing after language toggle: ${desktopResult.english.firstAbility}`);
  if (!desktopResult.english.firstItem.includes("Extra Charge")) failures.push(`English first item missing after language toggle: ${desktopResult.english.firstItem}`);
  if (!desktopResult.english.versionButton.includes("Version Log")) failures.push("English version button missing after language toggle");
  if (!desktopResult.english.chartTitle.includes("Max Health")) failures.push(`English chart title not translated: ${desktopResult.english.chartTitle}`);
  if (desktopResult.beforeModal.chartCurves < 30) failures.push(`too few desktop chart curves: ${desktopResult.beforeModal.chartCurves}`);
  if (desktopResult.beforeModal.skillCards !== 4) failures.push(`expected 4 skill cards, got ${desktopResult.beforeModal.skillCards}`);
  if (desktopResult.beforeModal.buildRows < 20) failures.push(`too few build rows: ${desktopResult.beforeModal.buildRows}`);
  if (!desktopResult.modal.visible || desktopResult.modal.sourceRows < 3) failures.push("version modal did not render source rows");
  if (mobileResult.chartCurves < 30) failures.push(`too few mobile chart curves: ${mobileResult.chartCurves}`);
  if (mobileResult.skillCards !== 4) failures.push(`expected 4 mobile skill cards, got ${mobileResult.skillCards}`);
  if (!mobileResult.firstHero.includes("艾布拉姆斯")) failures.push(`mobile first hero not localized: ${mobileResult.firstHero}`);
  if (desktopResult.errors.length) failures.push(`browser errors: ${desktopResult.errors.join("; ")}`);

  console.log(JSON.stringify({ ok: failures.length === 0, failures, result }, null, 2));
  if (failures.length) process.exit(1);
})();
