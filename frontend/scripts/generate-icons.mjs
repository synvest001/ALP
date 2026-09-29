import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import sharp from 'sharp';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');

const SVG_SOURCE = path.join(projectRoot, 'branding', 'icon-source.svg');
const PUBLIC_DIR = path.join(projectRoot, 'public');

const TARGETS = [
  { filename: 'icon-192.png', size: 192 },
  { filename: 'icon-512.png', size: 512 },
  { filename: 'icon-180.png', size: 180 },
];

async function generateIcons() {
  if (!fs.existsSync(SVG_SOURCE)) {
    throw new Error(`Vector icon source not found at: ${SVG_SOURCE}`);
  }

  if (!fs.existsSync(PUBLIC_DIR)) {
    fs.mkdirSync(PUBLIC_DIR, { recursive: true });
  }

  const svgBuffer = fs.readFileSync(SVG_SOURCE);

  console.log(`Generating icon PNG assets from ${SVG_SOURCE}...`);

  for (const { filename, size } of TARGETS) {
    const outputPath = path.join(PUBLIC_DIR, filename);
    await sharp(svgBuffer)
      .resize(size, size)
      .png({ compressionLevel: 9 })
      .toFile(outputPath);

    const meta = await sharp(outputPath).metadata();
    console.log(`Generated ${filename}: ${meta.width}x${meta.height} (${meta.format})`);
  }

  console.log('All icons generated successfully.');
}

generateIcons().catch((err) => {
  console.error('Failed to generate icons:', err);
  process.exit(1);
});
