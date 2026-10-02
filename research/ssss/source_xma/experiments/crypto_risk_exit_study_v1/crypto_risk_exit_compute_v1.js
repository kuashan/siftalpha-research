// FIVEGZ5SE Crypto Risk Exit Study v1 computation helper.
// Requires globalThis.FIVEGZ5SE_V1 and patched FIVEGZ5SE_STAGED_ENTRY_V1 exposing build().

(function(){
const mean=a=>{const x=a.filter(Number.isFinite);return x.length?x.reduce((s,v)=>s+v,0)/x.length:null};
const q=(a,p)=>{const x=a.filter(Number.isFinite).sort((a,b)=>a-b);if(!x.length)return null;const z=(x.length-1)*p,l=Math.floor(z),h=Math.ceil(z);return x[l]+(x[h]-x[l])*(z-l)};
function sourceCsv(s){const L=s.trim().split(/\r?\n/);return "Date,Open,High,Low,Close,Volume\n"+L.slice(1).filter(Boolean).map(l=>{const p=l.split(",");return [p[0],p[1],p[2],p[3],p[4],p[5]].join(",")}).join("\n")}
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
 let cash=10000,qty=0,totalCost=0,pending=null,entrySignal=null,entryExec=null,entryFam=null,startEq=0,confirmed=false;
 let peakClosePx=null,peakEq=10000,closeMdd=0,intraMdd=0,exposure=0,normalExits=0,hardExits=0,trailExits=0,bothExits=0,gapExits=0;
 const trades=[],stops=[];
 function finish(i,px,reason,gap=false){
   const weighted=totalCost/qty,proceeds=qty*px,posRet=px/weighted-1;
   cash+=proceeds;qty=0;totalCost=0;
   const portRet=cash/startEq-1;
   const tr={entry_signal:raw[entrySignal].date,entry_date:raw[entryExec].date,entry_family:entryFam,confirmed,exit_date:raw[i].date,exit_reason:reason,gap,ret:portRet,pos_ret:posRet,days:i-entryExec,weighted_cost:weighted,exit_price:px};
   trades.push(tr);
   if(reason==="NORMAL")normalExits++;else if(reason==="HARD")hardExits++;else if(reason==="TRAIL")trailExits++;else if(reason==="BOTH"){bothExits++;}
   if(reason!=="NORMAL"&&reason!=="END"&&gap)gapExits++;
   entrySignal=entryExec=entryFam=null;startEq=0;confirmed=false;peakClosePx=null;
   return tr;
 }
 for(let i=start;i<=end;i++){
   let stoppedToday=false,stopEvent=null;
   if(pending?.type==="SELL_NORMAL"&&qty>0){finish(i,raw[i].open*.9995,"NORMAL");pending=null;}
   else {
     if(pending?.type==="BUY_INIT"&&qty===0){
       const amt=Math.min(cash,pending.amount),px=raw[i].open*1.0005,qv=amt/px;
       qty+=qv;cash-=amt;totalCost+=amt;entryExec=i;peakClosePx=null;pending=null;
     } else if(pending?.type==="BUY_TOPUP"&&qty>0){
       const amt=Math.min(cash,pending.amount),px=raw[i].open*1.0005,qv=amt/px;
       qty+=qv;cash-=amt;totalCost+=amt;confirmed=true;pending=null;
     } else pending=null;
     if(qty>0&&(hard!=null||trail!=null)){
       const weighted=totalCost/qty,hardPx=hard!=null?weighted*(1-hard):null,trailPx=(trail!=null&&peakClosePx!=null)?peakClosePx*(1-trail):null;
       let stopPx=null,reason=null;
       if(hardPx!=null&&trailPx!=null){stopPx=Math.max(hardPx,trailPx);reason=Math.abs(hardPx-trailPx)<1e-12?"BOTH":hardPx>trailPx?"HARD":"TRAIL";}
       else if(hardPx!=null){stopPx=hardPx;reason="HARD";} else if(trailPx!=null){stopPx=trailPx;reason="TRAIL";}
       if(stopPx!=null&&(raw[i].open<=stopPx||raw[i].low<=stopPx)){
         const gap=raw[i].open<=stopPx,fill=(gap?raw[i].open:stopPx)*.9995;
         const before={date:raw[i].date,signal_date:raw[entrySignal].date,entry_family:entryFam,confirmed,reason,gap,stop_level:stopPx,fill,weighted_cost:weighted,peak_close:peakClosePx,bar_index:i};
         const tr=finish(i,fill,reason,gap);stopEvent={...before,trade_ret:tr.ret,pos_ret:tr.pos_ret,days:tr.days};stops.push(stopEvent);stoppedToday=true;
       }
     }
   }
   if(qty>0)exposure++;
   const closeEq=cash+qty*raw[i].close,lowEq=qty>0?cash+qty*raw[i].low:cash;
   closeMdd=Math.min(closeMdd,closeEq/peakEq-1);intraMdd=Math.min(intraMdd,lowEq/peakEq-1);peakEq=Math.max(peakEq,closeEq);
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
     if(!stoppedToday){const init=bs.filter(x=>x==="A"||x==="B");if(init.length&&ss.length===0){startEq=closeEq;entrySignal=i;entryFam=init[0];confirmed=false;pending={type:"BUY_INIT",amount:closeEq*.6};}}
   } else {
     if(ss.length)pending={type:"SELL_NORMAL"};
     else if(!confirmed&&entrySignal!=null&&i>entrySignal&&i-entrySignal<=3&&onset(BUY.C,i))pending={type:"BUY_TOPUP",amount:Math.min(cash,startEq*.4)};
   }
 }
 if(qty>0)finish(end,raw[end].close*.9995,"END");
 const rets=trades.map(t=>t.ret);
 return {return:cash/10000-1,close_mdd:closeMdd,intra_mdd:intraMdd,trades:trades.length,win:rets.length?rets.filter(x=>x>0).length/rets.length:null,avg_trade:mean(rets),median_trade:q(rets,.5),p10:q(rets,.1),p5:q(rets,.05),cvar10:rets.length?mean([...rets].sort((a,b)=>a-b).slice(0,Math.max(1,Math.ceil(rets.length*.1)))):null,worst:rets.length?Math.min(...rets):null,exposure:exposure/(end-start+1),normal_exits:normalExits,hard_exits:hardExits,trail_exits:trailExits,both_exits:bothExits,gap_exits:gapExits,open_at_end:false,trade_details:trades,stop_details:stops};
}
globalThis.CRYPTO_RISK_EXIT_V1={sourceCsv,setup,simulate,mean,q};
})();