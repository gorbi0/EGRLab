const fs=require('fs'),path=require('path');
const sharp=require('C:/Users/tgorbacz/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=path.resolve(__dirname,'..');
(async()=>{for(const n of ['P01','P01-AUX','P01-SAFE']) {await sharp(path.join(root,'output/svg',n+'.svg'),{density:145}).png().toFile(path.join(root,'output/svg',n+'.png'));} })();
