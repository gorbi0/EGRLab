import {createRequire} from 'node:module';
import {readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
const require=createRequire(import.meta.url);
const sharp=require(process.argv[3] || 'sharp');
const root=process.argv[2];
for (const name of ['assembly','bottom','copper-front','copper-back']) {
 if(name.startsWith('copper-')) {
  // Style only: filled copper light grey, track strokes black. Native paths,
  // clearances and coordinates are untouched; easier to inspect and print.
  const f=path.join(root,'output/svg',name+'.svg');
  let native=await readFile(f,'utf8');
  native=native.replaceAll('fill:#000000','fill:#c8cdd0');
  await writeFile(f,native);
 }
 await sharp(path.join(root,'output/svg',name+'.svg'),{density:120}).resize({width:3200}).flatten({background:'#ffffff'}).png().toFile(path.join(root,'output/previews',name+'.png'));
}
// Crop the native vector plot by its viewBox; no shape geometry is re-created.
let svg=await readFile(path.join(root,'output/svg/assembly.svg'),'utf8');
svg=svg.replace(/width="[^"]+" height="[^"]+" viewBox="[^"]+"/,'width="100mm" height="100mm" viewBox="96 14 25 25"');
await writeFile(path.join(root,'output/svg/gate-detail.svg'),svg);
await sharp(Buffer.from(svg),{density:120}).resize({width:1800}).flatten({background:'#ffffff'}).png().toFile(path.join(root,'output/previews/gate-detail.png'));
