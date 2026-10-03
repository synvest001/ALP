// Post-build step: shrink artwork in dist/art so old iPads (iOS 9, 512 MB RAM) do not run out of
// memory decoding it. Source art in public/art is untouched. Run via `npm run build`.
//  - square images (avatars, ~1024 px, shown at <150 px)  -> 256 px
//  - wide backgrounds (1376x768, shown on a 768-1024 px screen) -> max 1024 px wide
//  - anything else larger than 1024 px on its long side -> 1024 px
import fs from 'node:fs';
import path from 'node:path';
import sharp from 'sharp';

const DIR = path.resolve('dist/art');
let before = 0, after = 0;
for (const f of fs.readdirSync(DIR)) {
  if (!/\.(jpe?g|png)$/i.test(f)) continue;
  const file = path.join(DIR, f);
  const buf = fs.readFileSync(file);
  before += buf.length;
  const meta = await sharp(buf).metadata();
  const w = meta.width || 0, h = meta.height || 0;
  const square = Math.abs(w - h) / Math.max(w, h) < 0.15;
  const target = square ? 256 : 1024;
  if (Math.max(w, h) <= target) { after += buf.length; continue; }
  const out = await sharp(buf)
    .resize({ width: w >= h ? target : undefined, height: h > w ? target : undefined })
    .jpeg({ quality: 72, mozjpeg: true })
    .toBuffer();
  fs.writeFileSync(file, out);
  after += out.length;
}
console.log(`[optimize-art] ${(before / 1048576).toFixed(1)} MB -> ${(after / 1048576).toFixed(1)} MB`);
