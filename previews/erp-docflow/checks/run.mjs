import {readdirSync} from 'node:fs';
import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
const directory=fileURLToPath(new URL('.',import.meta.url));
for(const file of readdirSync(directory).filter(x=>x.endsWith('.mjs')&&x!=='run.mjs').sort()){
  const result=spawnSync(process.execPath,[directory+file],{stdio:'inherit'});
  if(result.status!==0)process.exit(result.status||1);
}
console.log('PASS all public-preview checks');
