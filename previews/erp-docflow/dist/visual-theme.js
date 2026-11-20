// Shared semantic palette: direction is stable; bank shades never depend on filter order.
export const VISUAL_THEME=Object.freeze({
  income:'#237c5b',incomeText:'#196344',incomeSoft:'#edf7f1',incomeLine:'#b7d9c6',
  expense:'#bd4e3c',expenseText:'#a53e30',expenseSoft:'#fcf0ec',expenseLine:'#e8c0b6',
  balance:'#677f90',balanceText:'#465f72',balanceSoft:'#edf2f6',
  task:'#356b9a',taskSoft:'#edf3fa',forecast:'#725396',forecastSoft:'#f3eef9',
  warning:'#8d600d',warningSoft:'#fff5df',warningLine:'#e3c785',
  danger:'#a53e30',dangerSoft:'#fcece8',info:'#356b9a',infoSoft:'#edf3fa',
  complete:'#52645b',completeSoft:'#eef2ef',text:'#233d34',muted:'#596b61',
  line:'#d9e2dc',surface:'#ffffff',surfaceSoft:'#f4f7f4',
  selection:'#356b9a',selectionSoft:'#e5eff9',today:'#e5eee5',
  incomeBradesco:'#237c5b',incomeBb:'#568548',expenseBradesco:'#bd4e3c',expenseBb:'#a96635'
});
const kebab=s=>s.replace(/[A-Z]/g,c=>'-'+c.toLowerCase());
export function installVisualTheme(doc=globalThis.document){
  if(!doc?.documentElement?.style)return;
  for(const [key,value] of Object.entries(VISUAL_THEME))doc.documentElement.style.setProperty('--df-'+kebab(key),value);
}
export function bankTone(account){
  const id=String(account?.id||account||'').toLowerCase(),code=String(account?.bankCode||account?.code||'');
  const name=String(account?.name||'').toLowerCase();
  if(id==='bradesco'||code==='237'||name.includes('bradesco'))return 'bradesco';
  if(id==='bb'||code==='001'||name.includes('banco do brasil'))return 'bb';
  return 'other';
}
export const flowDirection=amount=>amount>0?'incoming':amount<0?'outgoing':'neutral';
export function financeColor(group,account){
  const base=group==='incoming'?'income':group==='outgoing'?'expense':'balance',bank=bankTone(account);
  const key=base+(base!=='balance'&&bank!=='other'?(bank==='bb'?'Bb':'Bradesco'):'');
  return Number.parseInt(VISUAL_THEME[key].slice(1),16);
}
