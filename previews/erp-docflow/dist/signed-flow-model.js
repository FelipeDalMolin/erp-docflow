import {moveDate} from './range-model.js?v=17';

// Signed values in integer centavos. Investment transfers affect current account,
// but are excluded when viewing cash plus investments as one pool.
export function summarizeSignedFlows(transactions,excludeInvestmentTransfers=false){
  let incoming=0,outgoing=0,internalIn=0,internalOut=0,internalCount=0;
  for(const t of transactions){
    if(t.movementType==='investment-transfer'){
      internalCount++;
      if(t.amount>0)internalIn+=t.amount;else internalOut+=t.amount;
      if(excludeInvestmentTransfers)continue;
    }
    if(t.amount>0)incoming+=t.amount;else outgoing+=t.amount;
  }
  return {incoming,outgoing,net:incoming+outgoing,internalIn,internalOut,internalCount,count:transactions.length};
}

export function dailySignedFlows(data,range,excludeInvestmentTransfers=false){
  const dates=new Set([range.start,range.end,...data.points.filter(p=>!p.opening).map(p=>p.date)]);
  for(const t of data.transactions)for(const day of [moveDate(t.date,-1),t.date,moveDate(t.date,1)])if(day>=range.start&&day<=range.end)dates.add(day);
  return [...dates].sort().map(date=>({date,...summarizeSignedFlows(data.transactions.filter(t=>t.date===date),excludeInvestmentTransfers)}));
}

// A single BRL scale for both flows and balances, with an explicit zero and room
// on both sides even if the selected interval has movements of only one sign.
export function signedScale(values,top=28,bottom=348){
  const low=Math.min(0,...values),high=Math.max(0,...values),extent=Math.max(Math.abs(low),high,100);
  const minValue=Math.min(low-extent*.08,-extent*.2),maxValue=Math.max(high+extent*.08,extent*.2);
  const raw=(maxValue-minValue)/6,power=10**Math.floor(Math.log10(raw)),factor=raw/power;
  const step=([1,2,2.5,5,10].find(n=>n>=factor)||10)*power;
  const min=Math.floor(minValue/step)*step,max=Math.ceil(maxValue/step)*step;
  const ticks=Array.from({length:Math.round((max-min)/step)+1},(_,i)=>min+i*step);
  return {min,max,ticks,y:value=>bottom-(value-min)/(max-min)*(bottom-top)};
}
