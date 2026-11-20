import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';

const imageUrl = new URL('./entry.png', import.meta.url);
const image = await readFile(imageUrl);
const signature = Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]);

if (image.length < 33 || !image.subarray(0, 8).equals(signature)) {
  throw new Error('entry.png must have a valid PNG signature and complete IHDR.');
}
if (image.readUInt32BE(8) !== 13 || image.toString('ascii', 12, 16) !== 'IHDR') {
  throw new Error('entry.png must begin with a 13-byte IHDR chunk.');
}
const width = image.readUInt32BE(16);
const height = image.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png must be 1024×1024; received ${width}×${height}.`);
}
if (image.length > 1048576) {
  throw new Error(`entry.png exceeds 1048576 bytes; received ${image.length}.`);
}

const outputDirectory = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
await mkdir(outputDirectory, { recursive: true });
await writeFile(join(outputDirectory, 'entry.png'), image);
console.log(`Copied ${image.length} bytes to ${join(outputDirectory, 'entry.png')}`);
