export const TREND_COLORS={up:'#247d52',down:'#bd5144',flat:'#677b70'};
// Direction follows the change in balance, including when both endpoints are negative.
export function balanceSegments(points){
  return points.slice(1).map((point,i)=>{
    const previous=points[i],delta=point.total-previous.total,direction=delta>0?'up':delta<0?'down':'flat';
    return {from:i,to:i+1,previous,point,delta,direction,color:TREND_COLORS[direction]};
  });
}
// Periods display closing balances; a focused day retains every transaction in source order.
export function balanceTrendPoints(data,view){
  if(view.day)return view.points;
  if(!view.reported)return view.points.filter(p=>!p.transaction);
  // A consolidated ledger already contains its automatic investment. An opening point
  // is safe only when no separate investment snapshot would have to be invented.
  const canUseOpening=data.accounts.every(a=>a.statement?.balanceBasis==='consolidated'||!(a.statement?.investments||[]).length)&&data.accounts.some(a=>a.statement?.balanceBasis==='consolidated');
  return canUseOpening?[{...data.points[0],partial:view.points[0]?.partial},...view.points]:view.points;
}
