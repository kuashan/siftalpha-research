"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const child=require("node:child_process");
const {compareTV,pivotAll,derive,backtest}=require("./compare_tv_export.js");

function syntheticBars(n=850){
 return Array.from({length:n},(_,i)=>{
  let p=125+i*.021+8*Math.sin(i/13)+1.7*Math.cos(i/3.1);
  let open=p-.15*Math.sin(i*1.3),close=p+.13*Math.cos(i*.77);
  let high=Math.max(open,close)+1.5+Math.abs(Math.sin(i)),low=Math.min(open,close)-1.25-Math.abs(Math.cos(i));
  return {t:new Date(Date.UTC(2023,0,1,i,0,0,0)).toISOString(),o:open,h:high,l:low,c:close,v:NaN};
 });
}
function csvSimulation(bars){
 const a=derive(bars),wp=pivotAll(bars,a.hist,5,1,5,60),pp=pivotAll(bars,a.pai,2,2,2,10);
 const fields=["PARITY_PAI_RAW","PARITY_WT_RAW","PARITY_WT_SIGNAL_RAW","PARITY_WT_HIST_RAW",
  "PARITY_WT_PIVOT_LOW_CONFIRMED","PARITY_WT_PIVOT_HIGH_CONFIRMED","PARITY_WT_BULL_CONFIRMED",
  "PARITY_WT_BEAR_CONFIRMED","PARITY_PAI_PIVOT_LOW_CONFIRMED","PARITY_PAI_PIVOT_HIGH_CONFIRMED",
  "PARITY_PAI_BULL_CONFIRMED","PARITY_PAI_BEAR_CONFIRMED","PARITY_PAI_UP5_CONFIRMED","PARITY_PAI_DOWN_MINUS5_CONFIRMED"];
 const over=(x,c,i)=>i>0&&x[i-1]<=c&&x[i]>c,under=(x,c,i)=>i>0&&x[i-1]>=c&&x[i]<c;
 const values={
  PARITY_PAI_RAW:a.pai,PARITY_WT_RAW:a.wt,PARITY_WT_SIGNAL_RAW:a.signal,PARITY_WT_HIST_RAW:a.hist,
  PARITY_WT_PIVOT_LOW_CONFIRMED:wp.pl,PARITY_WT_PIVOT_HIGH_CONFIRMED:wp.ph,
  PARITY_WT_BULL_CONFIRMED:a.bull,PARITY_WT_BEAR_CONFIRMED:a.bear,
  PARITY_PAI_PIVOT_LOW_CONFIRMED:pp.pl,PARITY_PAI_PIVOT_HIGH_CONFIRMED:pp.ph,
  PARITY_PAI_BULL_CONFIRMED:pp.bull,PARITY_PAI_BEAR_CONFIRMED:pp.bear,
  PARITY_PAI_UP5_CONFIRMED:a.pai.map((_,i)=>over(a.pai,5,i)),
  PARITY_PAI_DOWN_MINUS5_CONFIRMED:a.pai.map((_,i)=>under(a.pai,-5,i))
 };
 const fmt=x=>typeof x==="boolean"?(x?1:0):Number.isFinite(x)?Number(x).toFixed(8):"";
 const lines=[["time","open","high","low","close",...fields.map(x=>"★ MFRA R3 PARITY ★: "+x)].join(",")];
 for(let i=0;i<bars.length;i++){let b=bars[i];lines.push([b.t,b.o,b.h,b.l,b.c,...fields.map(x=>fmt(values[x][i]))].join(","));}
 return lines.join("\n")+"\n";
}
function run(){
 const series=syntheticBars(),s=csvSimulation(series);
 let v=compareTV(s);
 assert.equal(v.status,"CSV_VALUES_MATCH_JS_RECONSTRUCTION",JSON.stringify(v.first_mismatches.slice(0,5)));
 assert.equal(v.total_mismatches,0);
 assert.equal(Object.keys(v.fields).length,14);
 assert.ok(Object.values(v.fields).every(x=>x.compared>100));

 // Single deliberately changed exported PAI numerical cell must fail with a timestamp.
 const arr=s.trimEnd().split("\n");const line=arr[420].split(",");line[5]=String(+line[5]+.125);arr[420]=line.join(",");
 const wrong=compareTV(arr.join("\n")+"\n");
 assert.equal(wrong.status,"MISMATCH_REQUIRES_AUDIT");
 assert.equal(wrong.fields.PARITY_PAI_RAW.mismatches,1);
 assert.ok(wrong.first_mismatches[0].t);

 // Validation always uses the actual confirmation bar (left=5,right=1).
 const oscillator=[11,10,9,8,7,1,7,8,9,10,11,12,13,14,15,16,17,18,19,20];
 const small=oscillator.map((v,i)=>({t:String(i),o:v,h:v+1,l:v-1,c:v}));
 const pivot=pivotAll(small,oscillator,5,1,5,60);
 assert.equal(pivot.pl[5],false);
 assert.equal(pivot.pl[6],true);

 // Trade after a confirmed signal, not at the signal candle itself.
 const bars=[{t:"0",o:10,h:10,l:10,c:10},{t:"1",o:11,h:12,l:11,c:12},{t:"2",o:13,h:14,l:13,c:14},{t:"3",o:14,h:15,l:14,c:15}];
 const f={ent:[true,false,false,false],exit:[false,true,false,false]};
 let tr=backtest(bars,f,0,3,.0015);
 assert.ok(Math.abs(tr.ret-((13/11)*(.9985**2)-1))<1e-12);
 assert.equal(tr.trades,1);
 const nf={ent:[false,false,false,false],exit:[false,false,false,false]};
 assert.equal(backtest(bars,nf,0,3,0).ret,0);

 // Re-run frozen R2 snapshots from repository checkout and compare saved results.
 const root=path.resolve(__dirname,"../matrixquant_crypto_mtf_r2");
 if(fs.existsSync(path.join(root,"data","4h_BTC_USD.csv"))){
  child.execFileSync(process.execPath,[path.join(root,"backtest_engine.js")],{cwd:root,stdio:"pipe"});
  const prior=JSON.parse(fs.readFileSync(path.join(root,"RESULTS.json"),"utf8"));
  const replay=JSON.parse(fs.readFileSync(path.join(root,"REPLAY_RESULTS.json"),"utf8"));
  assert.equal(replay.rows.length,16);
  assert.equal(replay.summary.length,28);
  for(let i=0;i<16;i++){
   assert.equal(replay.rows[i].coin,prior.rows[i].coin);
   assert.equal(replay.rows[i].timeframe,prior.rows[i].timeframe);
   for(let key of ["PAI_SLOW","PAI_WT","PAI_BEAR_EXIT"])
    assert.ok(Math.abs(replay.rows[i].models[key].late.ret-prior.rows[i].models[key].late.ret)<1e-12);
  }
  console.log("PASS: frozen R2 16x7 replay unchanged");
 } else console.log("SKIP: previous R2 snapshots not found in this local checkout");
 console.log("PASS: exported CSV parse, 14 columns, mismatch detection, pivot confirmation, next-open execution, both-side friction");
 console.log("INFO: this is a synthetic JS regression, NOT a real TradingView/Pine parity result");
}
run();
