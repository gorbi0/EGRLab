import {createRequire} from 'node:module';
import {readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
const require=createRequire(import.meta.url);
const sharp=require(process.argv[3] || 'sharp');
const root=process.argv[2];
for (const name of ['assembly','copper-front','copper-back','copper-in1','copper-in2','fit']) {
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
