import {createRequire} from 'node:module';
import {readdir} from 'node:fs/promises';
import path from 'node:path';
const require=createRequire(import.meta.url);
const sharp=require(process.argv[3]);
const dir=process.argv[2];
for(const f of await readdir(dir)) {
  if(!f.endsWith('.svg')) continue;
  if(f==='CAM-top.svg'||f==='CAM-bottom.svg') continue; // expensive SVG filter stack
  await sharp(path.join(dir,f),{density:180}).resize({width:3200}).flatten({background:'#ffffff'}).png().toFile(path.join(dir,f.replace(/\.svg$/,'.png')));
}
