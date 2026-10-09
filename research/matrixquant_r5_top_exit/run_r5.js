// run: node run_r5.js data_batch_01.json data_batch_02.json data_batch_03.json
const fs=require('fs');
function runR5(batches) {
 const data={};
 for(const b of batches)for(const [sym,raw] of Object.entries(b.raw))data[sym]=raw;
 const symbols=Object.keys(data).sort(), valid=[];
 const MEAN=a=>a.length?a.reduce((z,x)=>z+x,0)/a.length:null;
 const MED=a=>a.length?[...a].sort((x,y)=>x-y)[Math.floor(a.length/2)]:null;
 const P=x=>x===null?null:Math.round(x*1e4)/100;
 const ema=(x,old,n)=>old===null?x:old+(2/(n+1))*(x-old);
 const scope={start:"2020-01-01",end:"2026-08-31",warmup:250};
 const eventNames=["S0_TOP_ENTER","S1_PAI_DOWN80","S2_WT_BEAR","S3_PRICE_BREAK","S4_WT_AND_PRICE"];
 const allEv=Object.fromEntries(eventNames.map(k=>[k,[]]));
 const live={},episodes=[];
 function calcInd(rows) {
  const n=rows.length,ind=[];
  let ema10=null,dev10=null,tci21=null,prevLag=null;
  const st=[],sds=[],wave=[];
  for(let i=0;i<n;i++){
   const z=rows[i];
   let stv=null;
   if(i>=13){let H=-Infinity,L=Infinity;for(let k=i-13;k<=i;k++){H=Math.max(H,rows[k].h);L=Math.min(L,rows[k].l)}if(H>L)stv=100*(z.c-L)/(H-L)}
   st.push(stv);
   let sd=null;
   if(i>=20){const arr=rows.slice(i-20,i+1).map(r=>r.c),m=MEAN(arr);sd=Math.sqrt(MEAN(arr.map(x=>(x-m)*(x-m))))}
   sds.push(sd);
   let pai=null;
   if(i>=33&&st.slice(i-2,i+1).every(Number.isFinite)){
    const a=sds.slice(i-13,i+1);
    if(a.length===14&&a.every(Number.isFinite)){
     const lo=Math.min(...a),hi=Math.max(...a);
     if(hi>lo)pai=50+50*(MEAN(st.slice(i-2,i+1))-50)/50*(sd-lo)/(hi-lo);
     // pai = 50+((mean(stoch)-50)/50)*100*stochDispNormalized/2
    }
   }
   const hlc=(z.h+z.l+z.c)/3;
   ema10=ema(hlc,ema10,10);
   dev10=ema(Math.abs(hlc-ema10),dev10,10);
   const ci=dev10>0?(hlc-ema10)/(0.015*dev10):0;
   tci21=ema(ci,tci21,21);
   let lag;
   if(prevLag===null)lag=[tci21,tci21,tci21,tci21];
   else{lag=[];lag[0]=0.92*tci21+0.08*prevLag[0];for(let k=1;k<4;k++)lag[k]=prevLag[k-1]-0.08*lag[k-1]+0.08*prevLag[k]}
   prevLag=lag;
   const main=(lag[0]+2*lag[1]+2*lag[2]+lag[3])/6;
   wave.push(main);
   const signal=i>=3?MEAN(wave.slice(i-3,i+1)):null;
   ind.push({pai,main,signal});
  }
  return ind;
 }
 const filtersCache={},inRes={};
 for(const sym of symbols){
  const rows=data[sym].trim().split(/\r?\n/).slice(1).map(l=>{let [date,o,h,lo,c,v]=l.split(";");return{date,o:+o,h:+h,l:+lo,c:+c,v:+v}}).sort((a,b)=>a.date.localeCompare(b.date));
  let invalid=0,dupe=0,badjump=0;
  for(let i=0;i<rows.length;i++){
   const r=rows[i];if(!Number.isFinite(r.o)||!Number.isFinite(r.c)||!Number.isFinite(r.v)||r.v<=0||r.h<Math.max(r.o,r.c)||r.l>Math.min(r.o,r.c))invalid++;
   if(i>0){if(rows[i-1].date===r.date)dupe++;if(Math.abs(r.o/rows[i-1].c-1)>.45)badjump++}
  }
  const inds=calcInd(rows);const f=[];
  const hasTopAt=i=>i>=0&&inds[i].pai!==null&&inds[i].pai>=85;
  const recentTop=i=>{for(let k=Math.max(0,i-10);k<i;k++)if(hasTopAt(k))return true;return false};
  const brokenAt=i=>{if(i<5)return false;let min=Infinity;for(let k=i-5;k<i;k++)min=Math.min(min,rows[k].l);return rows[i].c<min};
  for(let i=0;i<rows.length;i++){
   const p=inds[i].pai,prev=i>0?inds[i-1].pai:null;
   const top=p!==null&&prev!==null&&p>=85&&prev<85;
   const rev=p!==null&&prev!==null&&p<80&&prev>=80&&recentTop(i);
   const bear=i>0&&inds[i].signal!==null&&inds[i-1].signal!==null&&inds[i].main<inds[i].signal&&inds[i-1].main>=inds[i-1].signal;
   const break5=brokenAt(i)&&!brokenAt(i-1);
   const t=recentTop(i);
   f.push({B:p!==null&&prev!==null&&p<=15&&prev>15,
      S0_TOP_ENTER:top,
      S1_PAI_DOWN80:rev,
      S2_WT_BEAR:bear&&t,
      S3_PRICE_BREAK:break5&&t,
      S4_WT_AND_PRICE:break5&&t&&inds[i].main<inds[i].signal});
  }
  filtersCache[sym]=f;inRes[sym]={rows,ind:inds,filters:f};
  let eligible=0;
  for(let i=250;i<rows.length-20;i++){
   if(rows[i].date<scope.start||rows[i].date>scope.end)continue;
   eligible++;
   for(const type of eventNames){
    if(!f[i][type])continue;
    let open=rows[i+1].o;
    const fut=rows.slice(i+1,i+21);
    allEv[type].push({sym,i,date:rows[i].date,ret5:rows[i+5].c/open-1,ret10:rows[i+10].c/open-1,ret20:rows[i+20].c/open-1,
       mfe:Math.max(...fut.map(r=>r.h/open-1)),mae:Math.min(...fut.map(r=>r.l/open-1))});
   }
  }
  valid.push({sym,n:rows.length,start:rows[0].date,end:rows.at(-1).date,invalid,dupe,badjump,eligible});
  // study top episodes from first top event separated by >=20 candles within same stock
  let last=-1e9;
  for(let i=250;i<rows.length-35;i++){
   if(rows[i].date<scope.start||rows[i].date>scope.end||!f[i].S0_TOP_ENTER||i-last<20)continue;
   last=i;
   const e={sym,date:rows[i].date,priceAtTopNextOpen:rows[i+1].o};
   for(const type of eventNames.slice(1)){
    let j=null;for(let k=i+1;k<=i+15;k++)if(f[k][type]){j=k;break}
    e[type]=j===null?null:{barsWait:j-i,missedChange:rows[j+1].o/rows[i+1].o-1,confirmDate:rows[j].date};
   }
   episodes.push(e);
  }
 }
 function pick(ev,nonoverlap=true){
  const sorted=[...ev].sort((a,b)=>a.sym.localeCompare(b.sym)||a.i-b.i);
  if(!nonoverlap)return sorted;
  const last={};return sorted.filter(x=>{if(last[x.sym]!==undefined&&x.i-last[x.sym]<20)return false;last[x.sym]=x.i;return true});
 }
 function stats(events) {
  if(!events.length)return {n:0};
  const a=events;
  return {n:a.length,stocks:new Set(a.map(x=>x.sym)).size,down5:P(MEAN(a.map(x=>+(x.ret5<0)))),down10:P(MEAN(a.map(x=>+(x.ret10<0)))),down20:P(MEAN(a.map(x=>+(x.ret20<0)))),
    meanLong5:P(MEAN(a.map(x=>x.ret5))),meanLong20:P(MEAN(a.map(x=>x.ret20))),medianLong20:P(MED(a.map(x=>x.ret20))),mfe20:P(MEAN(a.map(x=>x.mfe))),mae20:P(MEAN(a.map(x=>x.mae)))};
 }
 const eventStats={};
 for(const name of eventNames){
  const arr=allEv[name],clean=pick(arr);
  eventStats[name]={all:stats(arr),dedup:stats(clean),early:stats(pick(arr.filter(x=>x.date<"2024-01-01"))),late:stats(pick(arr.filter(x=>x.date>="2024-01-01")))};
 }
 const episodeStats={};
 for(const name of eventNames.slice(1)){
  const a=episodes.map(e=>e[name]).filter(Boolean),total=episodes.length;
  episodeStats[name]={topEpisodes:total,confirmedWithin15:a.length,coverage:P(a.length/total),medianDelayBars:MED(a.map(x=>x.barsWait)),meanMissedLongReturn:P(MEAN(a.map(x=>x.missedChange))),medianMissedLongReturn:P(MED(a.map(x=>x.missedChange)))};
 }
 function simulate(sym,type,start=scope.start,end=scope.end){
  const {rows,filters:f}=inRes[sym],a=rows.findIndex(z=>z.date>=start),b=rows.findLastIndex(z=>z.date<=end);
  if(a<1||b<a+15)return null;
  let cash=10000,shares=0,entryCapital=null,enteredAt=null,trades=[],peak=cash,dd=0,exposure=0;
  for(let i=a;i<=b;i++){
   if(i>a){
    if(shares>0&&f[i-1][type]){
     const value=shares*rows[i].o*(1-.0015);
     trades.push({buy:enteredAt,sell:rows[i].date,ret:value/entryCapital-1,days:i-enteredAt.i});
     cash=value;shares=0;enteredAt=null;entryCapital=null;
    }else if(shares===0&&f[i-1].B){
     entryCapital=cash;
     shares=cash*(1-.0015)/rows[i].o;
     enteredAt={i,date:rows[i].date};
     cash=0;
    }
   }
   if(shares>0)exposure++;
   const eq=cash+shares*rows[i].c;
   peak=Math.max(peak,eq);dd=Math.min(dd,eq/peak-1);
  }
  const net=cash+shares*rows[b].c*(1-.0015);
  const bh=10000*(1-.0015)/rows[a].o*rows[b].c*(1-.0015);
  return {sym,start,end,ret:net/10000-1,bh:bh/10000-1,mdd:dd,exposure:exposure/(b-a+1),
   exits:trades.length,tradeWins:trades.filter(t=>t.ret>0).length,winRate:trades.length?trades.filter(t=>t.ret>0).length/trades.length:null,avgTradeNet:MEAN(trades.map(t=>t.ret)),openPosition:shares>0};
 }
 const round={};
 for(const [period,start,end] of [["whole","2020-01-01","2026-08-31"],["early","2020-01-01","2023-12-29"],["late","2024-01-01","2026-08-31"]]){
  round[period]={};
  const baseline=Object.fromEntries(symbols.map(s=>[s,simulate(s,eventNames[0],start,end)]));
  for(const name of eventNames){
   const all=symbols.map(s=>simulate(s,name,start,end));
   round[period][name]={
      n:all.length,medianAssetReturn:P(MED(all.map(x=>x.ret))),medianBuyHold:P(MED(all.map(x=>x.bh))),
      beatsBuyHold:all.filter(x=>x.ret>x.bh).length,
      beatsNaive:all.filter(x=>x.ret>baseline[x.sym].ret).length,
      medianMdd:P(MED(all.map(x=>x.mdd))),medianExposure:P(MED(all.map(x=>x.exposure))),
      completedRoundTrips:all.reduce((k,x)=>k+x.exits,0),
      allTradeWinRate:P(all.reduce((a,x)=>a+x.tradeWins,0)/Math.max(1,all.reduce((a,x)=>a+x.exits,0))),
      noClosedTradeAssets:all.filter(x=>x.exits===0).map(x=>x.sym),
      perStock:all.map(x=>({sym:x.sym,return:P(x.ret),buyHold:P(x.bh),maxDD:P(x.mdd),exposure:P(x.exposure),closedTrades:x.exits,tradeWin:P(x.winRate),hasOpen:x.openPosition}))
   };
  }
 }
 return {status:"EXPLORATORY_NO_AUTO_TRADING",refPolicy:"PROTOCOL_FROZEN_BEFORE_RESULTS.md",warnings:[
  "Prior price data are re-fetched archived Twelve Data snapshots; not certified adjusted; no dividends.",
  "TDX-modified PAI 14/3/21 and WaveTrend lag gamma .08, NOT original Pine default 20/3/20; per-bar TDX parity has not been independently certified.",
  "Later period is a historical robustness segment, not independent untouched OOS.",
  "Event directional hits are conditional price statistics, not completed-trade win rates."
 ],data:valid,events:eventStats,topEpisodeWait:episodeStats,roundTrips:round};
}
const batches=process.argv.slice(2).map(p=>JSON.parse(fs.readFileSync(p,'utf8')));
process.stdout.write(JSON.stringify(runR5(batches),null,2)+'\n');
