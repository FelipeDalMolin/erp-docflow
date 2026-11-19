import assert from 'node:assert/strict';
import {SEED,figures,total,remaining,paid} from './fixtures/demo.js';
const s=structuredClone(SEED);
const july=figures(s,'aurora','2026-07');
assert.equal(july.opening,1845000);
assert.equal(july.incoming,510000);
assert.equal(july.outgoing,203000);
assert.equal(july.balance,2152000);
assert.equal(july.toReceive,480000);
assert.equal(july.toPay,85000);
assert.equal(july.projected,2547000);
assert.equal(total(s.obligations.find(o=>o.id==='o204')),330000);
const partial=s.obligations.find(o=>o.id==='o105');
assert.equal(paid(s,partial),180000);
assert.equal(remaining(s,partial),60000);
s.tasks.find(t=>t.id==='tmatch').done=true;
assert.equal(remaining(s,partial),60000,'Completing a task must not settle an obligation');
s.transactions.push({id:'test-settlement',company:'aurora',account:'bradesco',date:'2026-07-18',amount:60000,obligation:'o105',confirmed:false});
assert.equal(remaining(s,partial),0);
assert.equal(figures(s,'aurora','2026-07').balance,2212000);
assert.equal(figures(s,'horizonte','2026-07').balance,1365000,'Companies must remain separate');
const bb=figures(SEED,'aurora','2026-07','bb'),br=figures(SEED,'aurora','2026-07','bradesco');
assert.equal(bb.balance+br.balance,july.balance);
assert.equal(figures(SEED,'aurora','2026-08').current.length,0);
assert.equal(figures(SEED,'aurora','2026-08').toReceive,990000);
for(const o of SEED.obligations){assert.ok(Number.isSafeInteger(total(o)));assert.ok(SEED.companies.some(c=>c.id===o.company));assert.ok(SEED.accounts.some(a=>a.id===o.account&&a.company===o.company));}
for(const d of SEED.documents){if(d.obligation)assert.ok(SEED.obligations.some(o=>o.id===d.obligation&&o.company===d.company));}
console.log('Verified cash totals, components, partial settlement, task independence, account totals, company separation, future obligations and document references.');
