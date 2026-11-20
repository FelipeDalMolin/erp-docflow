import assert from 'node:assert/strict';
import {readFileSync,readdirSync,existsSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
const root=fileURLToPath(new URL('..',import.meta.url));
const walk=dir=>readdirSync(dir,{withFileTypes:true}).flatMap(x=>x.isDirectory()?walk(path.join(dir,x.name)):[path.join(dir,x.name)]);
for(const file of walk(root)){
  assert.ok(!/\.(pdf|ofx|qfx|qif|csv|tsv|xlsx?|zip|pem|p12|pfx)$/i.test(file),path.relative(root,file));
  assert.ok(!file.includes(path.sep+'.openai'+path.sep),file);
}
assert.ok(!existsSync(path.join(root,'dist/sources')));
assert.ok(!existsSync(path.join(root,'dist/import-audit.json')));
const base=path.join(root,'dist/vendor/amcharts5-5.22.0');
const manifest=JSON.parse(readFileSync(path.join(base,'manifest.json'),'utf8'));
assert.equal(manifest.version,'5.22.0');
for(const entry of manifest.files)assert.equal(createHash('sha256').update(readFileSync(path.join(base,entry.file))).digest('hex'),entry.sha256,entry.file);
for(const file of walk(path.join(root,'dist')).filter(x=>x.endsWith('.js')&&!x.includes(path.sep+'vendor'+path.sep))){
  const text=readFileSync(file,'utf8');
  for(const match of text.matchAll(/from\s+['"](\.\.?\/[^'"]+)['"]/g))assert.ok(existsSync(path.resolve(path.dirname(file),match[1].split('?')[0])),match[1]);
}
console.log('PASS public content: prohibited document formats absent, static imports resolve, vendored library hashes unchanged.');
