import {createRequire} from 'node:module';const require=createRequire(import.meta.url);const sharp=require('/opt/egrlab/node/node_modules/sharp');
await sharp(process.argv[2],{density:150}).flatten({background:'#ffffff'}).png().toFile(process.argv[3]);
