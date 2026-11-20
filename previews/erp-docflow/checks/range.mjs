import assert from 'node:assert/strict';
import {SEED} from './fixtures/demo.js';
import {rangeBook,presetRange,validDate,moveDate} from '../dist/range-model.js';
import {summarizePeriods} from '../dist/workbook-model.js';

const range={start:'2026-07-10',end:'2026-08-05'};
const daily=rangeBook(SEED,'aurora',range),monthly=rangeBook(SEED,'aurora',range,'monthly'),annual=rangeBook(SEED,'aurora',range,'yearly');
assert.equal(daily.length,27);
assert.equal(monthly.length,2);
assert.equal(monthly[0].start,range.start);
assert.equal(monthly[1].end,range.end);
for(const grouped of [daily,monthly,annual]){
  const s=summarizePeriods(grouped);
  assert.equal(s.opening,2175000);
  assert.equal(s.incoming,180000,'July 5 receipt is outside the filter');
  assert.equal(s.outgoing,203000);
  assert.equal(s.closing,2152000);
  assert.equal(s.pendingIn,810000,'Only due dates through August 5 are included');
  assert.equal(s.transactions.length,4);
}
assert.equal(summarizePeriods(rangeBook(SEED,'aurora',range,'monthly','bb')).incoming,0);
assert.equal(summarizePeriods(rangeBook(SEED,'aurora',range,'monthly','bb')).outgoing,48000);
assert.equal(rangeBook(SEED,'horizonte',range,'yearly')[0].transactions.some(t=>t.account==='bb'),false);
assert.deepEqual(presetRange('week','2026-08-01'),{start:'2026-07-27',end:'2026-08-02'});
assert.deepEqual(presetRange('quarter','2026-08-18'),{start:'2026-07-01',end:'2026-09-30'});
assert.deepEqual(presetRange('semester','2026-08-18'),{start:'2026-07-01',end:'2026-12-31'});
assert.deepEqual(presetRange('twelve','2026-07-18'),{start:'2025-08-01',end:'2026-07-31'});
assert.equal(moveDate('2028-02-29',0,12),'2029-02-28');
assert.equal(validDate('2026-02-30'),false);
assert.throws(()=>rangeBook(SEED,'aurora',{start:'2026-08-01',end:'2026-07-31'}));
const cross=rangeBook(SEED,'aurora',{start:'2025-12-20',end:'2026-01-10'},'yearly');
assert.deepEqual(cross.map(x=>[x.start,x.end]),[['2025-12-20','2025-12-31'],['2026-01-01','2026-01-10']]);
console.log('Verified exact ranges, partial months/years, invariant totals across grouping, cross-month weeks, presets, leap years and bank/company isolation.');
