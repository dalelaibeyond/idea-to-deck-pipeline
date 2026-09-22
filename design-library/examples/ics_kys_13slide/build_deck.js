/**
 * ics_kys_style — html2pptx fidelity driver (generic).
 *
 * Usage:
 *   node build_deck.js <slides_dir> <output.pptx> [start=1] [end=N]
 *   NODE_PATH=/opt/homebrew/lib/node_modules node build_deck.js slides/ out.pptx
 *
 * Notes:
 * - Depends on globally installed pptxgenjs, playwright, sharp.
 *   Set NODE_PATH to the npm global root (e.g. /opt/homebrew/lib/node_modules).
 * - html2pptx.js ships with the `powerpoint` agent skill:
 *   ~/.agents/skills/powerpoint/scripts/html2pptx.js (override via HTML2PPTX env).
 * - Slide HTML files must be exactly 720x405pt body, LAYOUT_16x9.
 * - Hard exit (1) on any compile/validation error — never silently drop slides.
 */
const pptxgen = require('pptxgenjs');
const path = require('path');

const html2pptxPath = process.env.HTML2PPTX ||
  path.join(process.env.HOME, '.agents/skills/powerpoint/scripts/html2pptx.js');
const html2pptx = require(html2pptxPath);

async function main() {
  const [slidesDir, output, sArg = '1', eArg = '99'] = process.argv.slice(2);
  if (!slidesDir || !output) {
    console.error('usage: node build_deck.js <slides_dir> <output.pptx> [start] [end]');
    process.exit(1);
  }
  const start = parseInt(sArg, 10), end = parseInt(eArg, 10);

  const pptx = new pptxgen();
  pptx.layout = 'LAYOUT_16x9';

  const files = require('fs').readdirSync(slidesDir)
    .filter((f) => /^slide\d+\.html$/.test(f))
    .sort((a, b) => parseInt(a.match(/\d+/)[0], 10) - parseInt(b.match(/\d+/)[0], 10))
    .filter((f) => {
      const n = parseInt(f.match(/\d+/)[0], 10);
      return n >= start && n <= end;
    });

  if (files.length === 0) { console.error('no slide files found'); process.exit(1); }
  for (const f of files) {
    await html2pptx(path.join(path.resolve(slidesDir), f), pptx);
    console.log(`[ok] ${f}`);
  }
  await pptx.writeFile({ fileName: path.resolve(output) });
  console.log(`WROTE ${path.resolve(output)} with ${files.length} slides`);
}

main().catch((e) => { console.error(e.message); process.exit(1); });