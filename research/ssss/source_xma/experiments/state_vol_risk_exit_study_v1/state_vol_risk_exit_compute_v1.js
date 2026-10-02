// SSSS State / Volatility-Aware Risk Exit Study v1 helper.
// Requires globalThis.FIVEGZ5SE_STAGED_ENTRY_V1.build().

(function(){
const dims=["trend","capital","momentum","accel","anomaly"];
const mean=a=>{const x=a.filter(Number.isFinite);return x.length?x.reduce((s,v)=>s+v,0)/x.length:null};
const q=(a,p)=>{const x=a.filter(Number.isFinite).sort((a,b)=>a-b);if(!x.length)return null;const z=(x.length-1)*p,l=Math.floor(z),h=Math.ceil(z);return x[l]+(x[h]-x[l])*(z-l)};
const configs=["BASELINE","ATR2_ONLY","ATR3_ONLY","LOSS2_MOD","LOSS3_MOD","LOSS2_SEV","PEAK2_MOD","PEAK3_MOD","HYBRID25_MOD","CONFIRM_ADAPT","LOSS4_SEV"];

function tdCsv(s){
 const L=s.trim().split(/\r?\n/),h=L[0].split(";"),ix={d:h.indexOf("datetime"),o:h.indexOf("open"),hi:h.indexOf("high"),l:h.indexOf("low"),c:h.indexOf("close"),v:h.indexOf("volume")};
 if(Object.values(ix).some(x=>x<0))throw Error("TD_FIELDS:"+L[0]);
 const rows=L.slice(1).filter(Boolean).map(x=>x.split(";")).map(p=>[p[ix.d],p[ix.o],p[ix.hi],p[ix.l],p[ix.c],p[ix.v]])
  .filter(r=>r[0]&&[1,2,3,4,5].every(i=>Number.isFinite(+r[i]))).sort((a,b)=>a[0].localeCompare(b[0]));
 return "Date,Open,High,Low,Close,Volume\n"+rows.map(r=>r.join(",")).join("\n");
}
function sourceCsv(s){
 const L=s.trim().split(/\r?\n/),h=L[0].split(","),lower=h.map(x=>x.trim().toLowerCase());
 const ix={d:lower.indexOf("date"),o:lower.indexOf("open"),hi:lower.indexOf("high"),l:lower.indexOf("low"),c:lower.indexOf("close"),v:lower.indexOf("volume")};
 if(Object.values(ix).some(x=>x<0))throw Error("SOURCE_FIELDS:"+L[0]);
 const rows=L.slice(1).filter(Boolean).map(x=>x.split(",")).map(p=>[p[ix.d],p[ix.o],p[ix.hi],p[ix.l],p[ix.c],p[ix.v]])
  .filter(r=>r[0]&&[1,2,3,4,5].every(i=>Number.isFinite(+r[i]))).sort((a,b)=>a[0].localeCompare(b[0]));
 return "Date,Open,High,Low,Close,Volume\n"+rows.map(r=>r.join(",")).join("\n");
}
function setup(text){
 const M=globalThis.FIVEGZ5SE_STAGED_ENTRY_V1.build(text),F=M.F,raw=M.raw,N=raw.length;
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
 const tr=Array(N).fill(null),atr14=Array(N).fill(null);
 for(let i=0;i<N;i++){
   if(i===0)tr[i]=raw[i].high-raw[i].low;
   else tr[i]=Math.max(raw[i].high-raw[i].low,Math.abs(raw[i].high-raw[i-1].close),Math.abs(raw[i].low-raw[i-1].close));
   if(i>=13){let s=0;for(let k=i-13;k<=i;k++)s+=tr[k];atr14[i]=s/14;}
 }
 function state(i){
   if(!F[i])return null;
   const cur=dims.map(d=>F[i][d+"_cur"]),score=cur.reduce((a,b)=>a+b,0),bearish=cur.filter(x=>x<=-1).length,d3=dims.reduce((s,d)=>s+F[i][d+"_net3"],0);
   return {score,bearish,d3,moderate:score<=-2&&bearish>=2&&d3<=-2,severe:score<=-4&&bearish>=3&&d3<=-3};
 }
 return {...M,BUY,SELL,onset,active,atr14,state};
}
function riskCondition(name,ctx){
 const {lossAtr,peakDdAtr,state,confirmed}=ctx;
 if(name==="ATR2_ONLY")return lossAtr>=2;
 if(name==="ATR3_ONLY")return lossAtr>=3;
 if(name==="LOSS2_MOD")return lossAtr>=2&&state.moderate;
 if(name==="LOSS3_MOD")return lossAtr>=3&&state.moderate;
 if(name==="LOSS2_SEV")return lossAtr>=2&&state.severe;
 if(name==="PEAK2_MOD")return peakDdAtr>=2&&state.moderate;
 if(name==="PEAK3_MOD")return peakDdAtr>=3&&state.moderate;
 if(name==="HYBRID25_MOD")return Math.max(lossAtr,peakDdAtr)>=2.5&&state.moderate;
 if(name==="CONFIRM_ADAPT")return confirmed?(Math.max(lossAtr,peakDdAtr)>=3&&state.severe):(Math.max(lossAtr,peakDdAtr)>=2&&state.moderate);
 if(name==="LOSS4_SEV")return lossAtr>=4&&state.severe;
 return false;
}
function simulate(M,{config="BASELINE",assetClass="stock"}={}){
 const {raw,BUY,SELL,onset,active,atr14,state}=M,N=raw.length,start=63,end=N-1;
 let cash=10000,qty=0,totalCost=0,pending=null,entrySignal=null,entryExec=null,entryFam=null,startEq=0,confirmed=false,firstSellSet=null;
 let peakClosePx=null,peakEq=10000,closeMdd=0,intraMdd=0,exposure=0,normalFull=0,normalHalf=0,riskExits=0,gapExits=0;
 const trades=[],risks=[];
 function finish(i,px,reason,meta=null){
   const weighted=qty>0?totalCost/qty:null,posRet=weighted?px/weighted-1:null,proceeds=qty*px;
   cash+=proceeds;qty=0;totalCost=0;
   const portRet=startEq?cash/startEq-1:null;
   const tr={entry_signal:raw[entrySignal].date,entry_date:raw[entryExec].date,entry_family:entryFam,confirmed,exit_date:raw[i].date,exit_reason:reason,ret:portRet,pos_ret:posRet,days:i-entryExec,weighted_cost:weighted,exit_price:px};
   trades.push(tr);
   if(reason==="NORMAL_FULL")normalFull++; else if(reason==="RISK")riskExits++;
   if(reason==="RISK"&&meta){
     const ev={...meta,exec_date:raw[i].date,fill:px,trade_ret:portRet,pos_ret:posRet,days:tr.days};
     for(const h of [3,5,10,20]){
       const j=Math.min(end,i+h),seg=raw.slice(i+1,j+1);
       ev["post_ret_"+h]=raw[j].close/px-1;
       ev["post_min_"+h]=seg.length?Math.min(...seg.map(r=>r.low))/px-1:null;
       ev["post_max_"+h]=seg.length?Math.max(...seg.map(r=>r.high))/px-1:null;
       ev["recovered_cost_"+h]=seg.some(r=>r.high>=meta.weighted_cost);
     }
     risks.push(ev);
   }
   entrySignal=entryExec=entryFam=null;startEq=0;confirmed=false;firstSellSet=null;peakClosePx=null;
 }
 function partial(i,f=.5){
   const sellQty=qty*f,weighted=totalCost/qty,px=raw[i].open*.9995;
   cash+=sellQty*px;qty-=sellQty;totalCost-=sellQty*weighted;if(qty<1e-12){qty=0;totalCost=0;}normalHalf++;
 }
 for(let i=start;i<=end;i++){
   let riskExecutedToday=false;
   if(pending?.type==="NORMAL_FULL"&&qty>0){finish(i,raw[i].open*.9995,"NORMAL_FULL");pending=null;}
   else if(pending?.type==="RISK_FULL"&&qty>0){
     const prevClose=raw[i-1]?.close,px=raw[i].open*.9995;if(prevClose!=null&&raw[i].open<prevClose)gapExits++;
     finish(i,px,"RISK",pending.meta);pending=null;riskExecutedToday=true;
   } else if(pending?.type==="NORMAL_HALF"&&qty>0){partial(i,.5);pending=null;}
   else if(pending?.type==="BUY_INIT"&&qty===0){
     const amt=Math.min(cash,pending.amount),px=raw[i].open*1.0005,qv=amt/px;qty+=qv;cash-=amt;totalCost+=amt;entryExec=i;peakClosePx=null;pending=null;
   } else if(pending?.type==="BUY_TOPUP"&&qty>0){
     const amt=Math.min(cash,pending.amount),px=raw[i].open*1.0005,qv=amt/px;qty+=qv;cash-=amt;totalCost+=amt;confirmed=true;pending=null;
   } else if(pending)pending=null;

   if(qty>0)exposure++;
   const closeEq=cash+qty*raw[i].close,lowEq=qty>0?cash+qty*raw[i].low:cash;
   closeMdd=Math.min(closeMdd,closeEq/peakEq-1);intraMdd=Math.min(intraMdd,lowEq/peakEq-1);peakEq=Math.max(peakEq,closeEq);
   if(qty>0)peakClosePx=peakClosePx==null?raw[i].close:Math.max(peakClosePx,raw[i].close);

   if(i===end)break;
   const bs=active(BUY,i),ss=active(SELL,i);
   if(qty===0){
     if(!riskExecutedToday){const init=bs.filter(x=>x==="A"||x==="B");if(init.length&&ss.length===0){startEq=closeEq;entrySignal=i;entryFam=init[0];confirmed=false;firstSellSet=null;pending={type:"BUY_INIT",amount:closeEq*.6};}}
     continue;
   }

   // Normal SELL decisions always outrank risk decisions.
   if(ss.length){
     if(assetClass==="crypto"){pending={type:"NORMAL_FULL"};continue;}
     if(firstSellSet==null){firstSellSet=new Set(ss);pending=(ss.includes("C")||ss.length>=2)?{type:"NORMAL_FULL"}:{type:"NORMAL_HALF"};continue;}
     if(ss.some(f=>!firstSellSet.has(f))){pending={type:"NORMAL_FULL"};continue;}
   }

   if(config!=="BASELINE"&&Number.isFinite(atr14[i])&&atr14[i]>0){
     const weighted=totalCost/qty,st=state(i),lossAtr=Math.max(0,(weighted-raw[i].close)/atr14[i]),peakDdAtr=Math.max(0,((peakClosePx??raw[i].close)-raw[i].close)/atr14[i]);
     const ctx={lossAtr,peakDdAtr,state:st,confirmed};
     if(st&&riskCondition(config,ctx)){
       pending={type:"RISK_FULL",meta:{signal_date:raw[i].date,entry_signal:raw[entrySignal].date,entry_family:entryFam,confirmed,weighted_cost:weighted,close:raw[i].close,atr14:atr14[i],loss_atr:lossAtr,peak_dd_atr:peakDdAtr,state_score:st.score,bearish_count:st.bearish,d3:st.d3,moderate:st.moderate,severe:st.severe,after_half:firstSellSet!=null}};
       continue;
     }
   }
   if(!confirmed&&entrySignal!=null&&i>entrySignal&&i-entrySignal<=3&&onset(BUY.C,i))pending={type:"BUY_TOPUP",amount:Math.min(cash,startEq*.4)};
 }
 const finalEquity=cash+(qty>0?qty*raw[end].close:0),openAtEnd=qty>0,rets=trades.map(t=>t.ret);
 return {return:finalEquity/10000-1,close_mdd:closeMdd,intra_mdd:intraMdd,trades:trades.length,win:rets.length?rets.filter(x=>x>0).length/rets.length:null,avg_trade:mean(rets),median_trade:q(rets,.5),p10:q(rets,.1),p5:q(rets,.05),cvar10:rets.length?mean([...rets].sort((a,b)=>a-b).slice(0,Math.max(1,Math.ceil(rets.length*.1)))):null,worst:rets.length?Math.min(...rets):null,exposure:exposure/(end-start+1),normal_full_exits:normalFull,normal_half_exits:normalHalf,risk_exits:riskExits,gap_exits:gapExits,open_at_end:openAtEnd,trade_details:trades,risk_details:risks};
}
function matchDiagnostics(result,baseline){
 const bm=new Map(baseline.trade_details.map(t=>[t.entry_signal,t])),matched=[];
 for(const e of result.risk_details){const b=bm.get(e.entry_signal);if(!b)continue;matched.push({...e,baseline_ret:b.ret,delta_vs_baseline:e.trade_ret-b.ret,baseline_winner:b.ret>0,baseline_loser:b.ret<0});}
 const killed=matched.filter(x=>x.baseline_winner),saved=matched.filter(x=>x.baseline_loser&&x.delta_vs_baseline>0),conf=matched.filter(x=>x.confirmed),pre=matched.filter(x=>!x.confirmed);
 return {matched_stops:matched.length,killed_winners:killed.length,saved_losers:saved.length,mean_delta_vs_baseline:mean(matched.map(x=>x.delta_vs_baseline)),killed_winner_opportunity_cost:mean(killed.map(x=>x.delta_vs_baseline)),saved_loser_improvement:mean(saved.map(x=>x.delta_vs_baseline)),confirmed_matched_stops:conf.length,confirmed_baseline_winners:conf.filter(x=>x.baseline_winner).length,confirmed_mean_delta:mean(conf.map(x=>x.delta_vs_baseline)),preconfirm_matched_stops:pre.length,preconfirm_mean_delta:mean(pre.map(x=>x.delta_vs_baseline)),matched};
}
globalThis.STATE_VOL_RISK_EXIT_V1={configs,tdCsv,sourceCsv,setup,simulate,matchDiagnostics,mean,q};
})();