import {dateStamp,DAY_MS,zoomDateRange} from './amchart-model.js?v=19';

export const CHART_MODES={
  zoom:{label:'Ampliar período',behavior:'zoomX',hint:'Arraste sobre as datas para ampliar o período.'},
  select:{label:'Selecionar',behavior:'selectX',hint:'Arraste para marcar um período e filtrar os itens abaixo, mantendo a visão do gráfico.'},
  pan:{label:'Mover',behavior:'none',hint:'Arraste para percorrer o trecho ampliado. Os sliders também movem a janela.'},
  area:{label:'Ampliar área',behavior:'zoomXY',hint:'Desenhe um retângulo para ampliar datas e valores. O slider lateral ajusta a escala.'}
};

export function navigateChartRange(current,bounds,{factor=1,shift=0}={}){
  const lower=dateStamp(bounds.start)/DAY_MS,upper=dateStamp(bounds.end)/DAY_MS;
  const start=dateStamp(current.start)/DAY_MS,end=dateStamp(current.end)/DAY_MS;
  const span=end-start+1,width=Math.max(1,Math.min(upper-lower+1,Math.round(span*factor)));
  let from=Math.round(start+(span-width)/2+span*shift);
  from=Math.max(lower,Math.min(upper-width+1,from));
  const day=n=>new Date(n*DAY_MS).toISOString().slice(0,10);
  return {start:day(from),end:day(from+width-1)};
}

export function cursorDateRange(first,last,axis,bounds){
  if(!Number.isFinite(first)||!Number.isFinite(last)||first===last)return null;
  const stamps=[first,last].map(p=>axis.positionToDate(axis.toAxisPosition(Math.max(0,Math.min(1,p)))).getTime()).sort((a,b)=>a-b);
  return zoomDateRange(stamps[0],stamps[1],bounds);
}

export function wheelPolicy(event,mode='zoom',alwaysZoom=false){
  if(event.ctrlKey||event.metaKey||alwaysZoom)return {wheelX:'panX',wheelY:mode==='area'?'zoomXY':'zoomX'};
  if(event.shiftKey)return {wheelX:'panX',wheelY:'panX'};
  if(Math.abs(event.deltaX||0)>Math.abs(event.deltaY||0))return {wheelX:'panX',wheelY:'none'};
  return null;
}
