const fs=require("fs"),vm=require("vm"),path=require("path");
const root=path.resolve(__dirname,"../../../../../");
function load(p){vm.runInThisContext(fs.readFileSync(path.join(root,p),"utf8"),{filename:p});}
load("research/ssss/source_xma/experiments/fivegz5se_cross_symbol/fivegz5se_v1_engine.js");
let staged=fs.readFileSync(path.join(root,"research/ssss/source_xma/experiments/staged_entry_crypto_study/fivegz5se_staged_entry_experiment_v1.js"),"utf8");
staged=staged.replace("globalThis.FIVEGZ5SE_STAGED_ENTRY_V1={analyze};","globalThis.FIVEGZ5SE_STAGED_ENTRY_V1={analyze,build};");
vm.runInThisContext(staged);
load("research/ssss/source_xma/experiments/three_buy_three_sell_refinement_v1/refinement_compute_helpers_v1.js");
const H=globalThis.REFINEMENT_V1;
const mean=a=>{const x=a.filter(Number.isFinite);return x.length?x.reduce((s,v)=>s+v,0)/x.length:null};
const q=(a,p)=>{const x=a.filter(Number.isFinite).sort((a,b)=>a-b);if(!x.length)return null;const z=(x.length-1)*p,l=Math.floor(z),h=Math.ceil(z);return x[l]+(x[h]-x[l])*(z-l)};
const policies=[.25,.5,.75,1.0];
const specs=[["BTC","BTCUSDT"],["ETH","ETHUSDT"],["BNB","BNBUSDT"],["SOL","SOLUSDT"]];
const inputDir=path.join(root,"research/ssss/source_xma/experiments/state_vol_risk_exit_study_v1/crypto_inputs");

function sim(M,sellFrac){
 const {raw,BUY,SELL,onset}=M,N=raw.length,start=63,end=N-1;
 let cash=10000,sh=0,pending=[],sig=null,ex=null,entryFamily=null,confirmed=false,startEq=0,partialCDone=false;
 let peak=10000,closeMdd=0,intraMdd=0,exposure=0,cPartialEvents=0,fullExits=0,openAtEnd=false;
 let weightedCost=0; const trades=[],cEvents=[];
 const active=(g,i)=>Object.keys(g).filter(k=>onset(g[k],i));
 const schedule=(type,arg)=>pending.push([type,arg]);
 function finish(i,px,reason){
   const eq=cash+sh*px;
   const r=startEq?eq/startEq-1:null;
   trades.push({entry_signal:raw[sig].date,entry_date:raw[ex].date,entry_family:entryFamily,confirmed,exit_date:raw[i].date,reason,ret:r});
   sig=ex=entryFamily=null;confirmed=false;startEq=0;partialCDone=false;weightedCost=0;fullExits++;
 }
 for(let i=start;i<=end;i++){
   if(pending.length){
     for(const [type,arg] of pending){
       if(type==="BUY"&&arg>0&&cash>0){
         const amt=Math.min(cash,arg),px=raw[i].open*1.0005,qty=amt/px;
         weightedCost=(weightedCost*sh+px*qty)/(sh+qty); sh+=qty; cash-=amt; if(ex==null)ex=i;
       } else if(type==="SELL"&&sh>0){
         const frac=arg.frac,qty=frac>=.999999?sh:sh*frac,px=raw[i].open*.9995;
         cash+=qty*px;sh-=qty;if(sh<1e-12)sh=0;
         if(arg.family==="C_PARTIAL"){
           cPartialEvents++;
           cEvents.push({signal_date:arg.signal_date,exec_date:raw[i].date,confirmed:arg.confirmed,sell_frac:frac,position_weight:arg.position_weight,anchor_px:px});
         }
         if(sh===0&&ex!=null)finish(i,px,arg.family);
       }
     }
     pending=[];
   }
   if(sh>0)exposure++;
   const closeEq=cash+sh*raw[i].close,lowEq=cash+sh*raw[i].low;
   closeMdd=Math.min(closeMdd,closeEq/peak-1);
   intraMdd=Math.min(intraMdd,lowEq/peak-1);
   peak=Math.max(peak,closeEq);
   if(i===end)break;

   const bs=active(BUY,i),ss=active(SELL,i);
   if(sh===0&&sig==null){
     const init=bs.filter(x=>x==="A"||x==="B");
     if(init.length&&!ss.length){
       startEq=closeEq;sig=i;entryFamily=init[0];confirmed=false;partialCDone=false;weightedCost=0;
       schedule("BUY",closeEq*.6);
     }
     continue;
   }
   if(sh<=0)continue;

   if(!confirmed&&i>sig&&i-sig<=3&&onset(BUY.C,i)){
     const amt=Math.min(cash,startEq*.4);
     if(amt>0){schedule("BUY",amt);confirmed=true;}
   }

   if(ss.length){
     if(ss.length>=2 || ss.includes("A") || ss.includes("B")){
       schedule("SELL",{frac:1,family:ss.length>=2?"MULTI":"SELL_"+ss[0]});
       continue;
     }
     if(ss.length===1&&ss[0]==="C"){
       if(sellFrac>=.999999){
         schedule("SELL",{frac:1,family:"SELL_C"});
       } else if(!partialCDone){
         const posWeight=(sh*raw[i].close)/closeEq;
         schedule("SELL",{frac:sellFrac,family:"C_PARTIAL",signal_date:raw[i].date,confirmed,position_weight:posWeight});
         partialCDone=true;
       }
     }
   }
 }
 const finalEq=cash+sh*raw[end].close;openAtEnd=sh>0;
 const rets=trades.map(t=>t.ret);
 return {
   return:finalEq/10000-1,close_mdd:closeMdd,intra_mdd:intraMdd,trades:trades.length,
   win:rets.length?rets.filter(x=>x>0).length/rets.length:null,
   avg_trade:mean(rets),median_trade:q(rets,.5),p10:q(rets,.1),p5:q(rets,.05),
   cvar10:rets.length?mean([...rets].sort((a,b)=>a-b).slice(0,Math.max(1,Math.ceil(rets.length*.1)))):null,
   worst:rets.length?Math.min(...rets):null,exposure:exposure/(end-start+1),
   c_partial_events:cPartialEvents,full_exits:fullExits,open_at_end:openAtEnd,trade_details:trades,c_events:cEvents
 };
}

function parseCsv(text){
 return text.trim().split(/\r?\n/);
}
function oldBaselines(){
 const lines=parseCsv(fs.readFileSync(path.join(root,"research/ssss/source_xma/experiments/three_buy_three_sell_refinement_v1/CRYPTO_SELL_POLICIES_v1.csv"),"utf8"));
 const h=lines[0].split(","),out={};
 for(const line of lines.slice(1)){const p=line.split(","),o={};h.forEach((k,i)=>o[k]=p[i]);if(o.policy==="FULL_FIRST")out[o.symbol]=o;}
 return out;
}
function cEventAudit(){
 const lines=parseCsv(fs.readFileSync(path.join(root,"research/ssss/source_xma/experiments/three_buy_three_sell_refinement_v1/CRYPTO_SELL_EVENTS_v1.csv"),"utf8"));
 const h=lines[0].split(","),rows=[];
 for(const line of lines.slice(1)){
   const p=line.split(","),o={};h.forEach((k,i)=>o[k]=p[i]);
   if(o.family!=="C")continue;
   rows.push({symbol:o.symbol,date:o.date,confirmed:o.confirmed==="true",wait_ret:+o.wait_ret,ret3:+o.ret3,ret5:+o.ret5,ret10:+o.ret10});
 }
 return rows;
}
function rng(seed){let x=seed>>>0;return()=>{x^=x<<13;x^=x>>>17;x^=x<<5;return (x>>>0)/4294967296}}
function bootstrap(vals,n=5000,seed=20261001){
 const r=rng(seed),means=[];for(let b=0;b<n;b++){let s=0;for(let i=0;i<vals.length;i++)s+=vals[Math.floor(r()*vals.length)];means.push(s/vals.length)}
 return {mean:mean(vals),lo:q(means,.025),hi:q(means,.975)};
}

const old=oldBaselines(),results=[],repro=[];
for(const [symbol,file] of specs){
 const csv=fs.readFileSync(path.join(inputDir,file+".csv"),"utf8");
 const M=H.model(H.genericCsv(csv));
 const configs=[];
 for(const frac of policies){
   const r=sim(M,frac);
   const name="C_SELL_"+Math.round(frac*100);
   configs.push({config:name,sell_frac:frac,start:M.raw[0].date,end:M.raw.at(-1).date,rows:M.raw.length,
    return:r.return,close_mdd:r.close_mdd,intra_mdd:r.intra_mdd,trades:r.trades,win:r.win,
    avg_trade:r.avg_trade,median_trade:r.median_trade,p10:r.p10,p5:r.p5,cvar10:r.cvar10,worst:r.worst,
    exposure:r.exposure,c_partial_events:r.c_partial_events,full_exits:r.full_exits,open_at_end:r.open_at_end});
 }
 const b=configs.find(x=>x.config==="C_SELL_100"),o=old[symbol];
 repro.push({symbol,return:b.return-(+o.return),close_mdd:b.close_mdd-(+o.mdd),trades:b.trades-(+o.trades),win:b.win-(+o.win),p5:b.p5-(+o.p5),cvar10:b.cvar10-(+o.cvar10),exposure:b.exposure-(+o.exposure)});
 results.push({symbol,configs});
}
const tol=1e-9,bad=repro.filter(x=>Math.abs(x.return)>tol||Math.abs(x.close_mdd)>tol||x.trades!==0||Math.abs(x.win)>tol||Math.abs(x.p5)>tol||Math.abs(x.cvar10)>tol||Math.abs(x.exposure)>tol);
if(bad.length){fs.writeFileSync(path.join(__dirname,"BASELINE_REPRO_v1.json"),JSON.stringify({status:"FAIL",repro},null,2)+"\n");console.error(JSON.stringify({status:"BASELINE_REPRO_FAIL",bad},null,2));process.exit(3);}
fs.writeFileSync(path.join(__dirname,"BASELINE_REPRO_v1.json"),JSON.stringify({status:"PASS",tolerance:tol,repro},null,2)+"\n");

const cEvents=cEventAudit();
const eras=[["2017-2020",2017,2020],["2021-2023",2021,2023],["2024-2026",2024,2026]];
const eventAudit={
 total:cEvents.length,
 confirmed_n:cEvents.filter(x=>x.confirmed).length,
 confirmed_wait_mean:mean(cEvents.filter(x=>x.confirmed).map(x=>x.wait_ret)),
 preconfirm_n:cEvents.filter(x=>!x.confirmed).length,
 preconfirm_wait_mean:mean(cEvents.filter(x=>!x.confirmed).map(x=>x.wait_ret)),
 by_era:{}
};
for(const [label,a,b] of eras){const z=cEvents.filter(x=>{const y=+x.date.slice(0,4);return y>=a&&y<=b});eventAudit.by_era[label]={n:z.length,wait_mean:mean(z.map(x=>x.wait_ret)),ret3_mean:mean(z.map(x=>x.ret3)),ret5_mean:mean(z.map(x=>x.ret5)),ret10_mean:mean(z.map(x=>x.ret10))};}

const baseRows=results.map(x=>x.configs.find(c=>c.config==="C_SELL_100"));
const summary=[];
for(const frac of policies){
 const name="C_SELL_"+Math.round(frac*100),rows=results.map(x=>x.configs.find(c=>c.config===name));
 const deltas=rows.map((r,i)=>({symbol:results[i].symbol,ret:r.return-baseRows[i].return,mdd:r.intra_mdd-baseRows[i].intra_mdd,p5:r.p5-baseRows[i].p5,cvar:r.cvar10-baseRows[i].cvar10}));
 const positives=deltas.filter(x=>x.ret>0),sumPos=positives.reduce((s,x)=>s+x.ret,0),maxPos=positives.length?Math.max(...positives.map(x=>x.ret)):0;
 const retBoot=bootstrap(deltas.map(x=>x.ret)),mddBoot=bootstrap(deltas.map(x=>x.mdd)),p5Boot=bootstrap(deltas.map(x=>x.p5)),cvarBoot=bootstrap(deltas.map(x=>x.cvar));
 const gate={
   mean_return_higher:mean(rows.map(x=>x.return))>mean(baseRows.map(x=>x.return)),
   return_improve_ge_3_of_4:deltas.filter(x=>x.ret>0).length>=3,
   mean_intraday_mdd_no_worse:mean(deltas.map(x=>x.mdd))>=0,
   mean_p5_no_worse:mean(deltas.map(x=>x.p5))>=0,
   mean_cvar_no_worse:mean(deltas.map(x=>x.cvar))>=0,
   positive_uplift_concentration_le_60pct:sumPos>0?(maxPos/sumPos)<=.60:false,
   era_2021_2023_nonnegative:eventAudit.by_era["2021-2023"].wait_mean>=0,
   era_2024_2026_nonnegative:eventAudit.by_era["2024-2026"].wait_mean>=0,
   confirmed_wait_nonnegative:eventAudit.confirmed_wait_mean>=0
 };
 gate.pass=frac<1&&Object.values(gate).every(Boolean);
 summary.push({config:name,sell_frac:frac,mean_return:mean(rows.map(x=>x.return)),median_return:q(rows.map(x=>x.return),.5),mean_intra_mdd:mean(rows.map(x=>x.intra_mdd)),mean_p5:mean(rows.map(x=>x.p5)),mean_cvar10:mean(rows.map(x=>x.cvar10)),mean_exposure:mean(rows.map(x=>x.exposure)),total_trades:rows.reduce((s,x)=>s+x.trades,0),return_improve_n:deltas.filter(x=>x.ret>0).length,mdd_improve_n:deltas.filter(x=>x.mdd>0).length,mean_return_delta:mean(deltas.map(x=>x.ret)),mean_mdd_improvement:mean(deltas.map(x=>x.mdd)),mean_p5_delta:mean(deltas.map(x=>x.p5)),mean_cvar_delta:mean(deltas.map(x=>x.cvar)),return_bootstrap:retBoot,mdd_bootstrap:mddBoot,p5_bootstrap:p5Boot,cvar_bootstrap:cvarBoot,positive_uplift_concentration:sumPos>0?maxPos/sumPos:null,gate,deltas});
}
const passed=summary.filter(x=>x.gate.pass).map(x=>x.config);
const decision=passed.length?{CRYPTO_SELL_C_PARTIAL:"PROMOTED_TO_NEXT_VALIDATION",passed}:{CRYPTO_SELL_C_FULL:"RETAINED",CRYPTO_SELL_C_PARTIAL:"REJECTED_NOT_ADMITTED",passed:[]};
fs.writeFileSync(path.join(__dirname,"CRYPTO_SELL_C_PARTIAL_RESULTS_v1.json"),JSON.stringify({study:"crypto_sell_c_partial_v1",date:"2026-10-01",baseline_reproduction:"PASS",results,summary,eventAudit,decision},null,2)+"\n");
let csv="symbol,config,sell_frac,return,close_mdd,intra_mdd,trades,win,avg_trade,median_trade,p10,p5,cvar10,worst,exposure,c_partial_events,full_exits,open_at_end\n";
for(const a of results)for(const r of a.configs)csv+=[a.symbol,r.config,r.sell_frac,r.return,r.close_mdd,r.intra_mdd,r.trades,r.win,r.avg_trade,r.median_trade,r.p10,r.p5,r.cvar10,r.worst,r.exposure,r.c_partial_events,r.full_exits,r.open_at_end].join(",")+"\n";
fs.writeFileSync(path.join(__dirname,"CRYPTO_SELL_C_PARTIAL_PER_COIN_v1.csv"),csv);
let scsv="config,sell_frac,mean_return,median_return,mean_return_delta,return_improve_n,mean_intra_mdd,mean_mdd_improvement,mdd_improve_n,mean_p5,mean_p5_delta,mean_cvar10,mean_cvar_delta,positive_uplift_concentration,ret_ci_lo,ret_ci_hi,mdd_ci_lo,mdd_ci_hi,gate_pass\n";
for(const s of summary)scsv+=[s.config,s.sell_frac,s.mean_return,s.median_return,s.mean_return_delta,s.return_improve_n,s.mean_intra_mdd,s.mean_mdd_improvement,s.mdd_improve_n,s.mean_p5,s.mean_p5_delta,s.mean_cvar10,s.mean_cvar_delta,s.positive_uplift_concentration,s.return_bootstrap.lo,s.return_bootstrap.hi,s.mdd_bootstrap.lo,s.mdd_bootstrap.hi,s.gate.pass].join(",")+"\n";
fs.writeFileSync(path.join(__dirname,"CRYPTO_SELL_C_PARTIAL_SUMMARY_v1.csv"),scsv);
console.log(JSON.stringify({status:"PASS",repro,summary:summary.map(x=>({config:x.config,mean_return:x.mean_return,ret_delta:x.mean_return_delta,mdd_imp:x.mean_mdd_improvement,p5_delta:x.mean_p5_delta,cvar_delta:x.mean_cvar_delta,return_improve_n:x.return_improve_n,mdd_improve_n:x.mdd_improve_n,concentration:x.positive_uplift_concentration,gate:x.gate})),eventAudit,decision},null,2));
