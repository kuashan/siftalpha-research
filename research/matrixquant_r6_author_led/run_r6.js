// Usage: node run_r6.js ../matrixquant_stock_extreme_20261009/raw_batch_01.json ../matrixquant_stock_extreme_20261009/raw_batch_02.json ../matrixquant_stock_extreme_20261009/raw_batch_03.json
const fs=require('fs');
function runR6(batches){
 const raws={};for(const b of batches)for(const [s,t] of Object.entries(b.raw))raws[s]=t;
 const names=Object.keys(raws).sort(),variantNames=["MODIFIED","ORIGINAL"],rules=["A_PAI","B_PAI_TREND","C_ALIGN","D_GOLD","E_WT_CROSS","F_SLOW_EXIT"];
 const C={MODIFIED:{paiLook:14,dispLook:21,trendOHLC:13,trendClose:21,lag:.08,lagEnabled:true},ORIGINAL:{paiLook:20,dispLook:20,trendOHLC:8,trendClose:20,lag:.02,lagEnabled:false}};
 const windows={early:{start:"2020-01-01",end:"2023-12-29"},late:{start:"2024-01-01",end:"2026-08-31"},full:{start:"2020-01-01",end:"2026-08-31"}};
 const m=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:null;
 const mid=a=>a.length?[...a].sort((x,y)=>x-y)[Math.floor(a.length/2)]:null;
 const pc=(x,d=2)=>x==null?null:+(x*100).toFixed(d);
 const ema=(x,y,len)=>y==null?x:y+2/(len+1)*(x-y);
 const dict={};const qc=[];
 for(const sym of names){
  const rows=raws[sym].trim().split(/\r?\n/).slice(1).map(l=>{const [date,o,h,lo,c,v]=l.split(";");return {date,o:+o,h:+h,l:+lo,c:+c,v:+v}}).sort((a,b)=>a.date.localeCompare(b.date));
  let bad=0,dup=0,gap=0,volBad=0;
  for(let i=0;i<rows.length;i++){const z=rows[i];if(z.o<=0||z.h<Math.max(z.o,z.c)||z.l>Math.min(z.o,z.c)||z.l<=0||!Number.isFinite(z.c))bad++;
   if(z.v<=0)volBad++;if(i){if(rows[i-1].date===z.date)dup++;if(Math.abs(z.o/rows[i-1].c-1)>.45)gap++}}
  qc.push({sym,rows:rows.length,first:rows[0].date,last:rows.at(-1).date,bad,dup,gap,volBad});
  dict[sym]={rows,variants:{}};
 }
 function indicators(rows,cfg){
  const n=rows.length,pai=[],trend=[],gold=[],wMain=[],wSignal=[],wDiff=[];
  const stoch=[],stdv=[],volumeW=[],rsiD=[];
  let esa=null,dema=null,tci=null,prevLag=[0,0,0,0],rUp=null,rDown=null,volLast=null;
  for(let i=0;i<n;i++){
   const bar=rows[i];let x=null,sd=null,raw=null;
   if(i>=cfg.paiLook-1){
    let hi=-Infinity,lo=Infinity;for(let j=i-cfg.paiLook+1;j<=i;j++){hi=Math.max(hi,rows[j].h);lo=Math.min(lo,rows[j].l)}
    if(hi>lo)x=100*(bar.c-lo)/(hi-lo);
   }stoch.push(x);
   if(i>=cfg.dispLook-1){
    let sum=0,sum2=0;for(let j=i-cfg.dispLook+1;j<=i;j++){sum+=rows[j].c;sum2+=rows[j].c**2;}
    const avg=sum/cfg.dispLook;sd=Math.sqrt(Math.max(0,sum2/cfg.dispLook-avg**2));
   }stdv.push(sd);
   if(i>=Math.max(cfg.paiLook+2,cfg.dispLook+cfg.paiLook-2)){
    const three=stoch.slice(i-2,i+1),ds=stdv.slice(i-cfg.paiLook+1,i+1);
    if(three.length===3&&three.every(v=>v!=null)&&ds.length===cfg.paiLook&&ds.every(v=>v!=null)){
     const min=Math.min(...ds),max=Math.max(...ds);
     if(max>min)raw=((m(three)-50)/50)*100*(sd-min)/(max-min);
    }
   }pai.push(raw);
   const typical=(bar.h+bar.l+bar.c)/3;
   esa=ema(typical,esa,10);
   dema=ema(Math.abs(typical-esa),dema,10);
   const ci=dema>0?(typical-esa)/(.015*dema):null;
   if(ci!==null)tci=ema(ci,tci,21);
   let lagged;
   if(tci==null){lagged=null;}else{
    const lag=[0,0,0,0],g=cfg.lag;
    lag[0]=(1-g)*tci+g*prevLag[0];
    lag[1]=-g*lag[0]+prevLag[0]+g*prevLag[1];
    lag[2]=-g*lag[1]+prevLag[1]+g*prevLag[2];
    lag[3]=-g*lag[2]+prevLag[2]+g*prevLag[3];
    prevLag=lag;
    lagged=(lag[0]+2*lag[1]+2*lag[2]+lag[3])/6;
   }
   const wt=tci==null?null:cfg.lagEnabled?lagged:tci;
   wMain.push(wt);
   let sig=null;
   if(i>=3&&wMain.slice(-4).every(z=>z!=null))sig=m(wMain.slice(-4));
   wSignal.push(sig);wDiff.push(wt!=null&&sig!=null?wt-sig:null);
   let pv=null;
   if(i>=7){
    let sum=0;
    for(let j=i-7;j<=i;j++)sum+=Math.log(rows[j].h/rows[j].l)**2;
    pv=Math.sqrt(typical/(8*4*Math.log(2))*sum);
   }
   if(pv!=null&&volLast!=null){const dv=pv-volLast;
     rsiD.push({u:Math.max(dv,0),d:Math.max(-dv,0)});
     if(rsiD.length===8){rUp=m(rsiD.map(z=>z.u));rDown=m(rsiD.map(z=>z.d));}
     else if(rsiD.length>8){rUp=(rUp*7+Math.max(dv,0))/8;rDown=(rDown*7+Math.max(-dv,0))/8;}
   }
   if(pv!=null)volLast=pv;
   gold.push(rUp!==null&&rDown!==null?100*rUp/(rUp+rDown)|| (rDown===0?100:0):null);
   const qty=bar.v,tdw=bar.h>bar.l?(2*bar.c-bar.l-bar.h)/(bar.h-bar.l):0;volumeW.push(tdw);
   let up1=0,dn1=0,up2=0,dn2=0;
   for(let j=Math.max(1,i-cfg.trendOHLC+1);j<=i;j++){
    const cur=rows[j],prior=rows[j-1],a=(cur.o+cur.h+cur.l+cur.c)/4,b=(prior.o+prior.h+prior.l+prior.c)/4;
    if(a>b)up1+=cur.v*a;else if(a<b)dn1+=cur.v*a;
   }
   for(let j=Math.max(1,i-cfg.trendClose+1);j<=i;j++){
    const cur=rows[j],prior=rows[j-1];if(cur.c>prior.c)up2+=cur.v*cur.c;else if(cur.c<prior.c)dn2+=cur.v*cur.c;
   }
   const line1=up1+dn1>0?100*up1/(up1+dn1):null,line2=up2+dn2>0?100*up2/(up2+dn2):null;
   trend.push(i>=250&&line1!==null&&line2>0?line1+tdw/line2+tdw:null);
  }
  return {pai,trend,gold,wMain,wSignal,wDiff};
 }
 function makeFlags(ind,n){
  const flags=[];
  for(let i=0;i<n;i++){
   const pr=ind.pai[i],prPrev=i?ind.pai[i-1]:null,tr=ind.trend[i],trPrev=i?ind.trend[i-1]:null,wt=ind.wDiff[i],wtPrev=i?ind.wDiff[i-1]:null;
   const paiPos=pr!=null&&pr>5,paiNeg=pr!=null&&pr< -5,trUp=tr!=null&&tr>50;
   const crossedP=prPrev!=null&&prPrev<=5&&paiPos;
   const aligned=paiPos&&trUp&&wt!=null&&wt>0;
   const prevAligned=i>0&&ind.pai[i-1]!=null&&ind.pai[i-1]>5&&ind.trend[i-1]!=null&&ind.trend[i-1]>50&&ind.wDiff[i-1]!=null&&ind.wDiff[i-1]>0;
   const crossesWt=wt!=null&&wtPrev!=null&&wt>0&&wtPrev<=0;
   let goldRecently=false;for(let k=Math.max(0,i-5);k<=i;k++)if(ind.gold[k]!=null&&ind.gold[k]<30){goldRecently=true;break}
   const enter={A_PAI:crossedP,B_PAI_TREND:crossedP&&trUp,C_ALIGN:aligned&&!prevAligned,
     D_GOLD:crossedP&&trUp&&trPrev!=null&&tr>trPrev&&goldRecently,
     E_WT_CROSS:crossesWt&&trUp&&paiPos,F_SLOW_EXIT:aligned&&!prevAligned};
   const exit={A_PAI:paiNeg,B_PAI_TREND:paiNeg||!trUp,C_ALIGN:paiNeg||!trUp,D_GOLD:paiNeg||!trUp,E_WT_CROSS:paiNeg||!trUp,F_SLOW_EXIT:paiNeg&&!trUp};
   flags.push({enter,exit,values:{pai:pr,trend:tr,gold:ind.gold[i],wt}});
  }
  return flags;
 }
 for(const sym of names)for(const key of variantNames){
   const z=dict[sym];const ind=indicators(z.rows,C[key]);z.variants[key]={ind,flags:makeFlags(ind,z.rows.length)};
 }
 function testWindow(rows,flags,rule,w){
  const begin=rows.findIndex(x=>x.date>=w.start),end=rows.findLastIndex(x=>x.date<=w.end);
  if(begin<250||end<=begin+2)return null;
  let balance=10000,shares=0,peak=10000,mdd=0,exposure=0,completed=[],bought=0;
  let boughtCash=null,entryDay=null;
  for(let i=begin;i<=end;i++){
   if(i>begin&&flags[i-1]){
    if(shares>0&&flags[i-1].exit[rule]){
      const val=shares*rows[i].o*(1-.0015);
      completed.push({ret:val/boughtCash-1,days:i-entryDay});
      balance=val;shares=0;boughtCash=null;entryDay=null;
    }else if(shares<=0&&flags[i-1].enter[rule]){
      boughtCash=balance;entryDay=i;shares=balance*(1-.0015)/rows[i].o;balance=0;bought++;
    }
   }
   if(shares>0)exposure++;
   const equity=balance+shares*rows[i].c;
   peak=Math.max(peak,equity);mdd=Math.min(mdd,equity/peak-1);
  }
  const last=rows[end].c,first=rows[begin].o;
  const net=(balance+shares*last*(1-.0015))/10000-1;
  const bh=(1-.0015)**2*last/first-1;
  const alloc=exposure/(end-begin+1);
  const matched=alloc*bh;
  let benchPeak=10000,benchDD=0;
  const initial=10000*(1-.0015)*alloc/first;
  for(let i=begin;i<=end;i++){const eq=10000*(1-alloc)+initial*rows[i].c;benchPeak=Math.max(benchPeak,eq);benchDD=Math.min(benchDD,eq/benchPeak-1)}
  return {ret:net,bh,matched,mdd,benchDD,exposure:alloc,buys:bought,closed:completed.length,wins:completed.filter(z=>z.ret>0).length,tradeReturn:m(completed.map(z=>z.ret)),open:shares>0};
 }
 function eventStats(rows,flags,rule,w){
  const ev=[],start=rows.findIndex(x=>x.date>=w.start),end=rows.findLastIndex(x=>x.date<=w.end);let last=-1000,rawCount=0;
  for(let i=Math.max(250,start);i<=Math.min(end-20,rows.length-21);i++){
    if(!flags[i].enter[rule])continue;rawCount++;
    if(i-last<20)continue;last=i;
    const startOpen=rows[i+1].o;
    ev.push({r5:rows[i+5].c/startOpen-1,r10:rows[i+10].c/startOpen-1,r20:rows[i+20].c/startOpen-1});
  }
  return {n:ev.length,rawEvents:rawCount,win5:pc(m(ev.map(x=>+(x.r5>0)))),win20:pc(m(ev.map(x=>+(x.r20>0)))),mean20:pc(m(ev.map(x=>x.r20)))};
 }
 const all={};
 for(const setting of variantNames){all[setting]={};for(const [part,w] of Object.entries(windows)){
  all[setting][part]={};
  for(const rule of rules){
   const rows=names.map(sym=>{const x=dict[sym];const a=testWindow(x.rows,x.variants[setting].flags,rule,w);return {sym,...a}});
   const event=names.map(sym=>eventStats(dict[sym].rows,dict[sym].variants[setting].flags,rule,w));
   const exits=rows.reduce((s,x)=>s+x.closed,0),wins=rows.reduce((s,x)=>s+x.wins,0);
   all[setting][part][rule]={
    n:rows.length,
    medianReturn:pc(mid(rows.map(x=>x.ret))),
    medianBuyhold:pc(mid(rows.map(x=>x.bh))),
    medianExposureMatched:pc(mid(rows.map(x=>x.matched))),
    medianExcessMatched:pc(mid(rows.map(x=>x.ret-x.matched))),
    medianMdd:pc(mid(rows.map(x=>x.mdd))),
    medianMatchedMdd:pc(mid(rows.map(x=>x.benchDD))),
    medianExposure:pc(mid(rows.map(x=>x.exposure))),
    beatBH:rows.filter(x=>x.ret>x.bh).length,beatMatched:rows.filter(x=>x.ret>x.matched).length,
    averageReturn:pc(m(rows.map(x=>x.ret))),
    averageBuyhold:pc(m(rows.map(x=>x.bh))),
    averageMatched:pc(m(rows.map(x=>x.matched))),
    buys:rows.reduce((s,x)=>s+x.buys,0),exits,tradeWinRate:exits?pc(wins/exits):null,
    zeroEntryStocks:rows.filter(x=>x.buys===0).map(x=>x.sym),
    nEvent: event.reduce((s,x)=>s+x.n,0),
    perStock:rows.map(x=>({sym:x.sym,ret:pc(x.ret),buyHold:pc(x.bh),matched:pc(x.matched),maxDD:pc(x.mdd),exposure:pc(x.exposure),buys:x.buys,exits:x.closed,open:x.open})),
    events: {n:event.reduce((s,x)=>s+x.n,0),rawCount:event.reduce((s,x)=>s+x.rawEvents,0),win5:pc(m(event.filter(x=>x.n).map(x=>x.win5/100))),win20:pc(m(event.filter(x=>x.n).map(x=>x.win20/100))),byStock:event}
   };
  }
 }}
 const eligible=[];
 for(const setting of variantNames)for(const rule of rules){
   const s=all[setting].early[rule];
   if(s.exits>=40&&s.zeroEntryStocks.length<5)eligible.push({setting,rule,...s});
 }
 eligible.sort((a,b)=>b.beatMatched-a.beatMatched||b.medianExcessMatched-a.medianExcessMatched||b.medianMdd-a.medianMdd||a.exits-b.exits);
 const top=eligible[0],selected=top?{setting:top.setting,rule:top.rule,selection:{beatMatched:top.beatMatched,medianExcessMatched:top.medianExcessMatched,exits:top.exits},late:all[top.setting].late[top.rule],full:all[top.setting].full[top.rule]}:null;
 return {meta:{source:"frozen R4 Twelve Data 3 batches",population:"20 US stocks",start:"2018-01-02",end:"2026-09-29",periods:windows,transactionCostOneSide:.0015,
    caveats:["Stock OHLCV is frozen from prior re-fetch, but corporate-action adjustment parity not independently certified.","Original Pine v6 vs reconstructed formulas not independently per-bar certified; beta reproduction is a research approximation.","Exposure-matched passive benchmark is allocated once at initial open at strategy's realized invested-days fraction, cash otherwise; it is not a perfectly time-matched randomized strategy.","The late 2024+ segment is a historical replication, not pristine untouched out-of-sample."]},
   inputAudit:qc,predeclaredRules:rules,config:C,candidates:all,eligibleSelectionRanking:eligible.map(x=>({setting:x.setting,rule:x.rule,beatMatched:x.beatMatched,medianExcessMatched:x.medianExcessMatched,medianReturn:x.medianReturn,medianMdd:x.medianMdd,exits:x.exits})),selected,
   status:"EXPLORATORY_RESEARCH_ONLY"};
}
const batches=process.argv.slice(2).map(p=>JSON.parse(fs.readFileSync(p,'utf8')));
process.stdout.write(JSON.stringify(runR6(batches),null,2)+'\n');
