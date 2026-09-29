const fs=require('fs'),path=require('path');
const sharp=require('C:/Users/tgorbacz/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');
const root=path.resolve(__dirname,'..');
(async()=>{for(const f of ['mechanical/P01-strefy','simulation/przebiegi']) await sharp(path.join(root,f+'.svg')).png().toFile(path.join(root,f+'.png'));})();
