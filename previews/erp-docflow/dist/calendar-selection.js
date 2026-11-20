import {validDate,moveDate,presetRange,rangeDays} from './range-model.js?v=17';

export const insideSelection=(s,date)=>date>=s.start&&date<=s.end;
export function newCalendarSelection(date){
  return {start:date,end:date,focus:date,month:date.slice(0,7),mode:'day',anchor:null,pending:false,panel:'day',page:1,flowAccount:'all',draft:null,error:''};
}
export function setCalendarRange(s,start,end=start,focus=end){
  if(!validDate(start)||!validDate(end)){s.error='Informe duas datas válidas, a partir de 1900.';return false;}
  if(start>end)[start,end]=[end,start];
  Object.assign(s,{start,end,focus:focus>=start&&focus<=end?focus:start,month:start.slice(0,7),anchor:null,pending:false,page:1,draft:null,error:'',panel:start===end?'day':'range'});
  return true;
}
export function pickCalendarDate(s,date,extend=false){
  if(!validDate(date))return false;
  if(extend){const anchor=s.anchor||s.focus;setCalendarRange(s,anchor,date,date);s.mode='range';s.anchor=anchor;s.month=date.slice(0,7);return true;}
  if(s.mode==='day'){setCalendarRange(s,date);return true;}
  if(!s.pending){const previous={start:s.start,end:s.end,focus:s.focus,month:s.month};setCalendarRange(s,date);s.previous=previous;s.anchor=date;s.pending=true;s.panel='range';}
  else{const anchor=s.anchor;setCalendarRange(s,anchor,date,date);s.month=date.slice(0,7);}
  return true;
}
export function calendarPreset(s,preset,today){
  const anchor=preset==='today'||preset==='next7'?today:s.focus;
  const r=preset==='today'?{start:today,end:today}:preset==='next7'?{start:today,end:moveDate(today,6)}:presetRange(preset,anchor);
  if(!setCalendarRange(s,r.start,r.end,anchor))return false;
  s.mode=r.start===r.end?'day':'range';s.month=s.focus.slice(0,7);return true;
}
export function shiftCalendarRange(s,direction){
  const n=rangeDays(s)*direction;
  return setCalendarRange(s,moveDate(s.start,n),moveDate(s.end,n),moveDate(s.focus,n));
}
export function selectionPage(items,page,size=12){
  const pages=Math.max(1,Math.ceil(items.length/size)),current=Math.min(pages,Math.max(1,Math.trunc(Number(page))||1)),start=(current-1)*size;
  return {items:items.slice(start,start+size),page:current,pages,total:items.length,first:items.length?start+1:0,last:Math.min(start+size,items.length)};
}
// Keep the whole day on the same page, even when it has many movements.
export function calendarDayGroups(items){
  const groups=new Map();
  for(const item of items){
    if(!groups.has(item.date))groups.set(item.date,{date:item.date,items:[],incoming:0,outgoing:0,counts:{realized:0,obligation:0,task:0,forecast:0}});
    const group=groups.get(item.date);group.items.push(item);group.counts[item.type]=(group.counts[item.type]||0)+1;
    if(item.type==='realized'){if(item.amount>0)group.incoming+=item.amount;else if(item.amount<0)group.outgoing-=item.amount;}
  }
  return [...groups.values()].sort((a,b)=>a.date.localeCompare(b.date));
}
export function calendarDayPage(items,page,size=7){
  const groups=calendarDayGroups(items),slice=selectionPage(groups,page,size);
  return {...slice,groups:slice.items,items:slice.items.flatMap(group=>group.items),totalItems:items.length};
}
