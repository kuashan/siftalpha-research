// FIVEGZ5SE Stock Risk Exit Study v1 computation helper.
// Requires globalThis.FIVEGZ5SE_V1 and patched FIVEGZ5SE_STAGED_ENTRY_V1 exposing build().

(function(){
const mean=a=>{const x=a.filter(Number.isFinite);return x.length?x.reduce((s,v)=>s+v,0)/x.length:null};
const q=(a,p)=>{const x=a.filter(Number.isFinite).sort((a,b)=>a-b);if(!x.length)return null;const z=(x.length-1)*p,l=Math.floor(z),h=Math.ceil(z);return x[l]+(x[h]-x[l])*(z-l)};
function tdCsv(s){
 const L=s.trim().split(/\r?\n/),h=L[0].split(";"),ix={d:h.indexOf("datetime"),o:h.indexOf("open"),hi:h.indexOf("high"),l:h.indexOf("low"),c:h.indexOf("close"),v:h.indexOf("volume")};
 if(Object.values(ix).some(x=>x<0))throw Error("TD_FIELDS:"+L[0]);
 const rows=L.slice(1).filter(Boolean).map(x=>x.split(";")).map(p=>[p[ix.d],p[ix.o],p[ix.hi],p[ix.l],p[ix.c],p[ix.v]]).filter(r=>r[0]&&Number.isFinite(+r[4])&&Number.isFinite(+r[5])).sort((a,b)=>a[0].localeCompare(b[0]));
 return "Date,Open,High,Low,Close,Volume\n"+rows.map(r=>r.join(",")).join("\n");
}
function setup(text){
 const M=globalThis.FIVEGZ5SE_STAGED_ENTRY_V1.build(text),F=M.F;
 const BUY={
  A:i=>!!F[i]&&F[i].trend_slope3>0&&F[i].momentum_cur===-2&&F[i].momentum_slope5<0,
  B:i=>!!F[i]&&F[i].capital_cur===0&&F[i].capital_net1<0&&F[i].accel_slope3>0,
  C:i=>!!F[i]&&F[i].trend_cur===0&&F[i].capital_net3>0&&F[i].capital_pos3>=2&&F[i].capital_slope5>0&&F[i].anomaly_cur===0
 },SELL={
  A:i=>!!F[i]&&F[i].trend_cur===0&&F[i].accel_pos5>=3&&F[i].bullbars3>=2,
  B:i=>!!F[i]&&F[i].capital_slope5<0&&F[i].momentum_cur>=1&&F[i].anomaly_net1<0,
  C:i=>!!F[i]&&F[i].momentum_cur===2&&F[i].anomaly_net3>0&&F[i].bullbars3>=2
 };
 const onset=(fn,i)=>i>0&&fn(i)&&!fn(i-1),active=(g,i)=>Object.keys(g).filter(k=>onset(g[k],i));
 return {...M,BUY,SELL,onset,active};
}
function simulate(M,{hard=null,trail=null}={}){
 const {raw,BUY,SELL,onset,active}=M,N=raw.length,start=63,end=N-1;
 let cash=10000,qty=0,totalCost=0,pending=null,entrySignal=null,entryExec=null,entryFam=null,startEq=0,confirmed=false,firstSellSet=null;
 let peakClosePx=null,peakEq=10000,closeMdd=0,intraMdd=0,exposure=0,normalFullExits=0,normalHalfExits=0,hardExits=0,trailExits=0,bothExits=0,gapExits=0;
 const trades=[],stops=[];
 function fullFinish(i,px,reason,gap=false){
   const weighted=qty>0?totalCost/qty:null,proceeds=qty*px,posRet=weighted?px/weighted-1:null;
   cash+=proceeds;qty=0;totalCost=0;
   const portRet=startEq?cash/startEq-1:null;
   const tr={entry_signal:raw[entrySignal].date,entry_date:raw[entryExec].date,entry_family:entryFam,confirmed,exit_date:raw[i].date,exit_reason:reason,gap,ret:portRet,pos_ret:posRet,days:i-entryExec,weighted_cost:weighted,exit_price:px};
   trades.push(tr);
   if(reason==="NORMAL_FULL")normalFullExits++; else if(reason==="HARD")hardExits++; else if(reason==="TRAIL")trailExits++; else if(reason==="BOTH")bothExits++;
   if(reason!=="NORMAL_FULL"&&reason!=="END"&&gap)gapExits++;
   entrySignal=entryExec=entryFam=null;startEq=0;confirmed=false;firstSellSet=null;peakClosePx=null;
   return tr;
 }
 function partialSell(i,fraction){
   const sellQty=qty*fraction,weighted=totalCost/qty,px=raw[i].open*.9995;
   cash+=sellQty*px;qty-=sellQty;totalCost-=sellQty*weighted;
   if(qty<1e-12){qty=0;totalCost=0;}
   normalHalfExits++;
 }
 for(let i=start;i<=end;i++){
   let stoppedToday=false,stopEvent=null;
   if(pending?.type==="SELL_FULL"&&qty>0){fullFinish(i,raw[i].open*.9995,"NORMAL_FULL");pending=null;}
   else {
     if(pending?.type==="SELL_HALF"&&qty>0){partialSell(i,.5);pending=null;}
     else if(pending?.type==="BUY_INIT"&&qty===0){
       const amt=Math.min(cash,pending.amount),px=raw[i].open*1.0005,qv=amt/px;
       qty+=qv;cash-=amt;totalCost+=amt;entryExec=i;peakClosePx=null;pending=null;
     } else if(pending?.type==="BUY_TOPUP"&&qty>0){
       const amt=Math.min(cash,pending.amount),px=raw[i].open*1.0005,qv=amt/px;
       qty+=qv;cash-=amt;totalCost+=amt;confirmed=true;pending=null;
     } else if(pending) pending=null;

     if(qty>0&&(hard!=null||trail!=null)){
       const weighted=totalCost/qty,hardPx=hard!=null?weighted*(1-hard):null,trailPx=(trail!=null&&peakClosePx!=null)?peakClosePx*(1-trail):null;
       let stopPx=null,reason=null;
       if(hardPx!=null&&trailPx!=null){stopPx=Math.max(hardPx,trailPx);reason=Math.abs(hardPx-trailPx)<1e-12?"BOTH":hardPx>trailPx?"HARD":"TRAIL";}
       else if(hardPx!=null){stopPx=hardPx;reason="HARD";} else if(trailPx!=null){stopPx=trailPx;reason="TRAIL";}
       if(stopPx!=null&&(raw[i].open<=stopPx||raw[i].low<=stopPx)){
         const gap=raw[i].open<=stopPx,fill=(gap?raw[i].open:stopPx)*.9995;
         const before={date:raw[i].date,signal_date:raw[entrySignal].date,entry_family:entryFam,confirmed,reason,gap,stop_level:stopPx,fill,weighted_cost:weighted,peak_close:peakClosePx,bar_index:i,after_half:firstSellSet!=null};
         const tr=fullFinish(i,fill,reason,gap);
         stopEvent={...before,trade_ret:tr.ret,pos_ret:tr.pos_ret,days:tr.days};
         stops.push(stopEvent);stoppedToday=true;
       }
     }
   }

   if(qty>0)exposure++;
   const closeEq=cash+qty*raw[i].close,lowEq=qty>0?cash+qty*raw[i].low:cash;
   closeMdd=Math.min(closeMdd,closeEq/peakEq-1);
   intraMdd=Math.min(intraMdd,lowEq/peakEq-1);
   peakEq=Math.max(peakEq,closeEq);
   if(qty>0)peakClosePx=peakClosePx==null?raw[i].close:Math.max(peakClosePx,raw[i].close);

   if(stopEvent){
     for(const h of [3,5,10,20]){
       const j=Math.min(end,i+h),seg=raw.slice(i+1,j+1);
       stopEvent["post_ret_"+h]=raw[j].close/stopEvent.fill-1;
       stopEvent["post_min_"+h]=seg.length?Math.min(...seg.map(r=>r.low))/stopEvent.fill-1:null;
       stopEvent["post_max_"+h]=seg.length?Math.max(...seg.map(r=>r.high))/stopEvent.fill-1:null;
       stopEvent["recovered_cost_"+h]=seg.some(r=>r.high>=stopEvent.weighted_cost);
     }
   }

   if(i===end)break;
   const bs=active(BUY,i),ss=active(SELL,i);
   if(qty===0){
     if(!stoppedToday){
       const init=bs.filter(x=>x==="A"||x==="B");
       if(init.length&&ss.length===0){startEq=closeEq;entrySignal=i;entryFam=init[0];confirmed=false;firstSellSet=null;pending={type:"BUY_INIT",amount:closeEq*.6};}
     }
   } else {
     if(ss.length){
       if(firstSellSet==null){
         firstSellSet=new Set(ss);
         if(ss.includes("C")||ss.length>=2)pending={type:"SELL_FULL"};
         else pending={type:"SELL_HALF"};
       } else if(ss.some(f=>!firstSellSet.has(f))) pending={type:"SELL_FULL"};
     } else if(!confirmed&&entrySignal!=null&&i>entrySignal&&i-entrySignal<=3&&onset(BUY.C,i)){
       pending={type:"BUY_TOPUP",amount:Math.min(cash,startEq*.4)};
     }
   }
 }
 const openAtEnd=qty>0;
 const finalEquity=cash+(qty>0?qty*raw[end].close:0);
 const rets=trades.map(t=>t.ret);
 return {
   return:finalEquity/10000-1,close_mdd:closeMdd,intra_mdd:intraMdd,trades:trades.length,
   win:rets.length?rets.filter(x=>x>0).length/rets.length:null,avg_trade:mean(rets),median_trade:q(rets,.5),
   p10:q(rets,.1),p5:q(rets,.05),cvar10:rets.length?mean([...rets].sort((a,b)=>a-b).slice(0,Math.max(1,Math.ceil(rets.length*.1)))):null,
   worst:rets.length?Math.min(...rets):null,exposure:exposure/(end-start+1),
   normal_full_exits:normalFullExits,normal_half_exits:normalHalfExits,
   hard_exits:hardExits,trail_exits:trailExits,both_exits:bothExits,gap_exits:gapExits,
   open_at_end:openAtEnd,trade_details:trades,stop_details:stops
 };
}
function matchDiagnostics(result,baseline){
 const baseMap=new Map(baseline.trade_details.map(t=>[t.entry_signal,t]));
 const matched=[];
 for(const s of result.stop_details){
   const b=baseMap.get(s.signal_date); if(!b)continue;
   matched.push({...s,baseline_ret:b.ret,delta_vs_baseline:s.trade_ret-b.ret,baseline_winner:b.ret>0,baseline_loser:b.ret<0});
 }
 const killed=matched.filter(x=>x.baseline_winner),saved=matched.filter(x=>x.baseline_loser&&x.delta_vs_baseline>0),confirmed=matched.filter(x=>x.confirmed);
 return {
   matched_stops:matched.length,
   killed_winners:killed.length,
   saved_losers:saved.length,
   mean_delta_vs_baseline:mean(matched.map(x=>x.delta_vs_baseline)),
   killed_winner_opportunity_cost:mean(killed.map(x=>x.delta_vs_baseline)),
   saved_loser_improvement:mean(saved.map(x=>x.delta_vs_baseline)),
   confirmed_matched_stops:confirmed.length,
   confirmed_baseline_winners:confirmed.filter(x=>x.baseline_winner).length,
   confirmed_mean_delta:mean(confirmed.map(x=>x.delta_vs_baseline)),
   preconfirm_matched_stops:matched.filter(x=>!x.confirmed).length,
   matched
 };
}
globalThis.STOCK_RISK_EXIT_V1={tdCsv,setup,simulate,matchDiagnostics,mean,q};
})();