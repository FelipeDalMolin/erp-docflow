import {dateStamp,DAY_MS,zoomDateRange} from './amchart-model.js?v=21';
import {CHART_MODES,cursorDateRange,wheelPolicy} from './chart-navigation-model.js?v=19';

let libraryPromise;
export function loadAmCharts(){
  if(!libraryPromise)libraryPromise=(async()=>{
    for(const file of ['index.js','xy.js','locales/pt_BR.js']){
      await new Promise((resolve,reject)=>{
        const script=document.createElement('script');
        script.src='/vendor/amcharts5-5.22.0/'+file;
        script.onload=resolve;script.onerror=()=>{script.remove();reject(new Error('Não foi possível carregar o gráfico.'));};
        document.head.appendChild(script);
      });
    }
    return {am5:window.am5,am5xy:window.am5xy,locale:window.am5locales_pt_BR};
  })().catch(error=>{libraryPromise=null;throw error;});
  return libraryPromise;
}

export const FINANCE_SERIES=[
  {field:'balance',group:'balance',label:'Saldo identificado',color:0x677f90,opacity:.16},
  {field:'incoming',group:'incoming',label:'Entradas',color:0x237c5b,opacity:.85},
  {field:'outgoing',group:'outgoing',label:'Saídas',color:0xc45440,opacity:.85}
];
export function financeSeries(accounts=[],composition='total'){
  if(composition!=='bank')return FINANCE_SERIES;
  return [FINANCE_SERIES[0],...['incoming','outgoing'].flatMap(group=>accounts.map((account,index)=>({
    field:group+'_'+index,group,bankIndex:index,label:(group==='incoming'?'Entradas':'Saídas')+' · '+account.name,
    color:(group==='incoming'?[0x237c5b,0x7eac65]:[0xbd4e3c,0xe28b68])[index%2],opacity:.88,stacked:index>0
  })))];
}

// The amounts stay in integer cents in the application. Only the chart receives reais.
export function createFinanceChart(element,options,library){
  const {am5,am5xy,locale}=library;
  const {rows,range,zoomRange,selectionRange,accounts=[],composition='total',hidden=[],yRange,onZoom=()=>{},onSelect=()=>{},onScale=()=>{},onHover=()=>{},onBar=()=>{}}=options;
  let mode=CHART_MODES[options.mode]?options.mode:'zoom',wheelZoom=!!options.wheelZoom;
  const specs=financeSeries(accounts,composition);
  const root=am5.Root.new(element);
  try{
  root.utc=true;if(locale)root.locale=locale;
  root.numberFormatter.setAll({numberFormat:'#,###.00',smallNumberPrefixes:[],bigNumberPrefixes:[{number:1e3,suffix:' mil'},{number:1e6,suffix:' mi'}]});
  root.dateFormatter.setAll({dateFormat:'dd/MM/yyyy',utc:true});
  const chart=root.container.children.push(am5xy.XYChart.new(root,{
    panX:mode==='pan',panY:mode==='pan',wheelX:'none',wheelY:'none',wheelStep:.12,pinchZoomX:true,pinchZoomY:mode==='area',arrangeTooltips:true,
    layout:root.verticalLayout,paddingLeft:0,paddingRight:14,paddingTop:12,paddingBottom:8
  }));
  const xr=am5xy.AxisRendererX.new(root,{minGridDistance:65});
  xr.labels.template.setAll({fontSize:12,fill:am5.color(0x54655e)});
  xr.grid.template.setAll({strokeOpacity:.06});
  const xAxis=chart.xAxes.push(am5xy.DateAxis.new(root,{
    baseInterval:{timeUnit:'day',count:1},min:dateStamp(range.start),max:dateStamp(range.end)+DAY_MS,
    strictMinMax:true,maxDeviation:0,minZoomCount:1,interpolationDuration:0,renderer:xr,tooltip:am5.Tooltip.new(root,{}),
    dateFormats:{day:'dd/MM',week:'dd/MM',month:'MMM yyyy',year:'yyyy'},
    periodChangeDateFormats:{day:'dd/MM',week:'dd/MM',month:'MMM yyyy',year:'yyyy'}
  }));
  const yr=am5xy.AxisRendererY.new(root,{minGridDistance:45,pan:'zoom'});
  yr.labels.template.setAll({fontSize:12,fill:am5.color(0x54655e)});
  yr.grid.template.setAll({strokeOpacity:.12,strokeDasharray:[3,3]});
  const yAxis=chart.yAxes.push(am5xy.ValueAxis.new(root,{renderer:yr,extraMin:.08,extraMax:.1,numberFormat:'R$ #,###a',maxDeviation:0,interpolationDuration:0,maxZoomFactor:100}));
  const zero=yAxis.createAxisRange(yAxis.makeDataItem({value:0}));
  zero.get('grid').setAll({stroke:am5.color(0x53675e),strokeOpacity:.7,strokeWidth:1.5,strokeDasharray:[]});
  const reais=new Intl.NumberFormat('pt-BR',{style:'currency',currency:'BRL'});
  const values=rows.map(r=>{
    const value={timestamp:r.timestamp,date:r.date};
    for(const spec of specs){
      const flow=spec.bankIndex===undefined?r:r.bankFlows[spec.bankIndex];
      const cents=flow[spec.group],count=flow[spec.group+'Count']||0;
      value[spec.field]=cents===null?null:cents/100;
      value[spec.field+'Count']=count;
      value[spec.field+'Tooltip']=r.date.split('-').reverse().join('/')+'\n'+spec.label+': '+(cents===null?'Não informado':reais.format(cents/100))
        +(spec.group==='balance'?(r.partial?' · parcial':''):'\n'+count+' lançamento'+(count===1?'':'s')+' · clique para ver correspondências');
    }
    return value;
  });
  const mainSeries=[];
  const lookup=new Map(rows.map(row=>[row.date,row]));
  let pointerDown=null;
  chart.plotContainer.events.on('pointerdown',event=>{const e=event.originalEvent;pointerDown=e?{x:e.clientX,y:e.clientY}:null;});
  for(const spec of specs){
    const color=am5.color(spec.color),isBalance=spec.group==='balance';
    const series=chart.series.push((isBalance?am5xy.LineSeries:am5xy.ColumnSeries).new(root,{
      name:spec.label,xAxis,yAxis,valueXField:'timestamp',valueYField:spec.field,stroke:color,fill:color,
      connect:false,visible:!hidden.includes(spec.group),...(isBalance?{}:{clustered:false}),
      ...(spec.stacked!==undefined?{stacked:spec.stacked,stackToNegative:true}:{}),
      tooltip:am5.Tooltip.new(root,{labelText:'{'+spec.field+'Tooltip}'})
    }));
    if(isBalance){
      series.strokes.template.setAll({strokeWidth:2.2});
      series.fills.template.setAll({visible:true,fillOpacity:spec.opacity});
    }else{
      series.columns.template.setAll({width:am5.percent(72),fillOpacity:spec.opacity,strokeOpacity:0,
        interactive:true,cursorOverStyle:'pointer',role:'button',ariaLabel:'{'+spec.field+'Tooltip}'});
      series.columns.template.events.on('click',event=>{
        const value=event.target.dataItem?.dataContext,e=event.originalEvent;
        // A drag that starts on a bar belongs to zoom/selection/pan, not drill-down.
        if(pointerDown&&e&&Math.hypot(e.clientX-pointerDown.x,e.clientY-pointerDown.y)>6)return;
        const row=lookup.get(value?.date);
        if(row&&value[spec.field+'Count']>0)onBar({date:row.date,direction:spec.group,account:spec.bankIndex===undefined?null:accounts[spec.bankIndex].id});
      });
    }
    mainSeries.push(series);
  }
  const cursor=chart.set('cursor',am5xy.XYCursor.new(root,{xAxis,behavior:CHART_MODES[mode].behavior,clickTolerance:18,moveThreshold:6,snapToSeries:mainSeries,snapToSeriesBy:'x'}));
  cursor.lineY.set('forceHidden',mode!=='area');
  cursor.selection.setAll({fill:am5.color(0x527da0),fillOpacity:.18,stroke:am5.color(0x527da0),strokeOpacity:.8});
  const selectionItem=xAxis.makeDataItem({value:dateStamp(range.start),endValue:dateStamp(range.end)+DAY_MS});
  xAxis.createAxisRange(selectionItem);
  selectionItem.get('grid').set('visible',false);
  selectionItem.get('axisFill').setAll({visible:false,fill:am5.color(0x527da0),fillOpacity:.12});
  function highlight(selected){
    cursor.selection.set('forceHidden',true);
    selectionItem.get('axisFill').set('visible',!!selected);
    if(selected)selectionItem.setAll({value:dateStamp(selected.start),endValue:dateStamp(selected.end)+DAY_MS});
  }
  cursor.events.on('selectstarted',()=>{cursor.selection.set('forceHidden',false);});
  cursor.events.on('selectended',()=>{
    if(mode!=='select')return;
    const selected=cursorDateRange(cursor.getPrivate('downPositionX'),cursor.getPrivate('positionX'),xAxis,range);
    if(selected){highlight(selected);onSelect(selected);}
  });
  chart.plotContainer.events.on('wheel',event=>{
    const policy=wheelPolicy(event.originalEvent,mode,wheelZoom);if(!policy)return;
    if(event.originalEvent.cancelable)event.originalEvent.preventDefault();
    chart.setAll(policy);chart.handleWheel(event);chart.setAll({wheelX:'none',wheelY:'none'});
  });
  cursor.events.on('cursormoved',event=>{
    const position=event.target.getPrivate('positionX');
    if(!Number.isFinite(position))return;
    const date=xAxis.positionToDate(xAxis.toAxisPosition(position)).toISOString().slice(0,10);
    const row=lookup.get(date);if(row)onHover(row);
  });

  // This is the native amCharts scrollbar, with a second chart and two draggable grips.
  const scrollbar=am5xy.XYChartScrollbar.new(root,{orientation:'horizontal',height:82,marginTop:20,opposite:true});
  chart.set('scrollbarX',scrollbar);
  chart.bottomAxesContainer.children.push(scrollbar);
  const vertical=chart.set('scrollbarY',am5.Scrollbar.new(root,{orientation:'vertical',minWidth:16,marginLeft:8}));
  vertical.startGrip.set('ariaLabel','Limite superior da escala de valores');vertical.endGrip.set('ariaLabel','Limite inferior da escala de valores');
  vertical.thumb.set('ariaLabel','Mover a escala de valores');
  scrollbar.startGrip.setAll({scale:1.1,ariaLabel:'Início do intervalo. Use as setas para ajustar.'});
  scrollbar.endGrip.setAll({scale:1.1,ariaLabel:'Fim do intervalo. Use as setas para ajustar.'});
  scrollbar.thumb.setAll({ariaLabel:'Mover o intervalo selecionado',fillOpacity:.12});
  const miniX=scrollbar.chart.xAxes.push(am5xy.DateAxis.new(root,{
    baseInterval:{timeUnit:'day',count:1},min:dateStamp(range.start),max:dateStamp(range.end)+DAY_MS,
    renderer:am5xy.AxisRendererX.new(root,{minGridDistance:80}),strictMinMax:true
  }));
  const miniSeries=[];
  const miniY=scrollbar.chart.yAxes.push(am5xy.ValueAxis.new(root,{renderer:am5xy.AxisRendererY.new(root,{})}));
  for(const spec of specs){
    const isBalance=spec.group==='balance';
    const series=scrollbar.chart.series.push((isBalance?am5xy.LineSeries:am5xy.ColumnSeries).new(root,{
      xAxis:miniX,yAxis:miniY,valueXField:'timestamp',valueYField:spec.field,connect:false,visible:!hidden.includes(spec.group),
      ...(isBalance?{}:{clustered:false}),...(spec.stacked!==undefined?{stacked:spec.stacked,stackToNegative:true}:{}),
      stroke:am5.color(spec.color),fill:am5.color(spec.color)
    }));
    if(isBalance){series.fills.template.setAll({visible:true,fillOpacity:.18});series.strokes.template.setAll({strokeWidth:1.2});}
    else series.columns.template.setAll({width:am5.percent(72),fillOpacity:.7,strokeOpacity:0,interactive:false});
    miniSeries.push(series);
  }
  let timer,disposed=false,lastRange=JSON.stringify(zoomRange||range),initializing=true;
  const notify=()=>{
    if(disposed||initializing)return;
    clearTimeout(timer);timer=setTimeout(()=>{
      if(disposed)return;
      const selected=zoomDateRange(xAxis.getPrivate('selectionMin'),xAxis.getPrivate('selectionMax'),range);
      if(selected&&JSON.stringify(selected)!==lastRange){lastRange=JSON.stringify(selected);highlight(null);onZoom(selected);}
    },120);
  };
  xAxis.onPrivate('selectionMin',notify);xAxis.onPrivate('selectionMax',notify);
  const scaleChanged=()=>{if(!disposed&&!initializing)onScale([yAxis.get('start',0),yAxis.get('end',1)]);};
  yAxis.on('start',scaleChanged);yAxis.on('end',scaleChanged);
  mainSeries[0].events.once('datavalidated',()=>{
    if(disposed)return;
    if(yRange)yAxis.zoom(yRange[0],yRange[1],0);
    highlight(selectionRange);
    if(zoomRange)xAxis.zoomToDates(new Date(dateStamp(zoomRange.start)),new Date(dateStamp(zoomRange.end)+DAY_MS),0);
    // Axis validation is finished before starting to broadcast zoom changes.
    root.events.once('frameended',()=>{initializing=false;notify();});
  });
  for(const series of [...mainSeries,...miniSeries])series.data.setAll(values);
  return {
    root,chart,xAxis,yAxis,cursor,scrollbar,vertical,selectionItem,
    setMode(value){if(!CHART_MODES[value])return;mode=value;cursor.set('behavior',CHART_MODES[mode].behavior);cursor.lineY.set('forceHidden',mode!=='area');chart.setAll({panX:mode==='pan',panY:mode==='pan',pinchZoomY:mode==='area'});cursor.selection.set('forceHidden',true);},
    setWheelZoom(value){wheelZoom=!!value;},
    highlight,
    setVisible(group,visible){specs.forEach((spec,i)=>{if(spec.group===group)for(const series of [mainSeries[i],miniSeries[i]])visible?series.show(0):series.hide(0);});},
    resetScale(){yAxis.zoom(0,1,0);onScale(null);},
    zoom(selected){xAxis.zoomToDates(new Date(dateStamp(selected.start)),new Date(dateStamp(selected.end)+DAY_MS),0);},
    dispose(){disposed=true;clearTimeout(timer);root.dispose();}
  };
  }catch(error){root.dispose();throw error;}
}
