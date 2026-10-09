// Node.js: node run_stock_extremes.js raw_batch_01.json raw_batch_02.json raw_batch_03.json
const fs=require('fs');
function study(batches){
 const by={};for(const b of batches)for(const [k,v] of Object.entries(b.raw||{}))by[k]=v;
 const parsed={},warnings=[];
 const avg=a=>a.length?a.reduce((s,x)=>s+x,0)/a.length:null;
 const median=a=>a.length?[...a].sort((x,y)=>x-y)[Math.floor(a.length/2)]:null;
 const pct=(x,d=2)=>x==null?null:Math.round(x*100*10**d)/10**d;
 const ema=(v,prev,len)=>prev==null?v:prev+2/(len+1)*(v-prev);
 const rma=(v,prev,len)=>prev==null?v:(prev*(len-1)+v)/len;
 function calc(rows){
  const out=[];let ema10=null,dev10=null,tci21=null, rUp=null,rDn=null,prevVol=null;
  let prevLag=[null,null,null,null]; const pk=[],sd=[],goldA=[];
  const n=rows.length;
  for(let i=0;i<n;i++){
   const z=rows[i],hlc3=(z.h+z.l+z.c)/3;
   let stochastic=null;
   if(i>=13){
    let hi=-Infinity,lo=Infinity;for(let k=i-13;k<=i;k++){hi=Math.max(hi,rows[k].h);lo=Math.min(lo,rows[k].l)}
    if(hi>lo)stochastic=100*(z.c-lo)/(hi-lo);
   }
   pk.push(stochastic);
   let sdev=null;
   if(i>=20){
    const vals=rows.slice(i-20,i+1).map(x=>x.c),m=avg(vals);
    sdev=Math.sqrt(avg(vals.map(x=>(x-m)**2)));
   }
   sd.push(sdev);
   let pai=null;
   if(i>=33&&pk.slice(i-2,i+1).every(Number.isFinite)){
     const v=sd.slice(i-13,i+1);
     if(v.every(Number.isFinite)){
      const hi=Math.max(...v),lo=Math.min(...v);
      if(hi>lo)pai=(100+((avg(pk.slice(i-2,i+1))-50)/50)*100*(sdev-lo)/(hi-lo))/2;
     }
   }
   ema10=ema(hlc3,ema10,10);
   dev10=ema(Math.abs(hlc3-ema10),dev10,10);
   const ci=dev10>0?(hlc3-ema10)/(0.015*dev10):0;
   tci21=ema(ci,tci21,21);
   let lag;
   if(prevLag[0]===null){lag=[tci21,tci21,tci21,tci21]}
   else {lag=[];lag[0]=.92*tci21+.08*prevLag[0];for(let k=1;k<4;k++)lag[k]=-.08*lag[k-1]+prevLag[k-1]+.08*prevLag[k]}
   prevLag=lag;
   const wr=(lag[0]+2*lag[1]+2*lag[2]+lag[3])/6;
   goldA.push(wr);
   const ws=goldA.length>=4?avg(goldA.slice(-4)):null;
   let vol=null;
   if(i>=7){
    let gl=0;for(let j=i-7;j<=i;j++){const a=rows[j];const u=Math.log(a.h/a.l);gl+=u*u}
    vol=Math.sqrt(hlc3/(8*4*Math.log(2))*gl);
   }
   let gold=null;
   if(vol!=null&&prevVol!=null){
    const delta=vol-prevVol;rUp=rma(Math.max(delta,0),rUp,8);rDn=rma(Math.max(-delta,0),rDn,8);
    gold=rUp+rDn>0?100*rUp/(rUp+rDn):50;
   }
   if(vol!=null)prevVol=vol;
   let tdw=z.h>z.l?(2*z.c-z.l-z.h)/(z.h-z.l)*z.v:0;
   let tu13=0,td13=0,tu21=0,td21=0;
   for(let j=Math.max(1,i-12);j<=i;j++){const x=rows[j],y=rows[j-1]; const p=(x.o+x.h+x.l+x.c)/4,q=(y.o+y.h+y.l+y.c)/4;if(p>q)tu13+=x.v*p;else if(p<q)td13+=x.v*p}
   for(let j=Math.max(1,i-20);j<=i;j++){const x=rows[j],y=rows[j-1];if(x.c>y.c)tu21+=x.v*x.c;else if(x.c<y.c)td21+=x.v*x.c}
   const v13=tu13+td13>0?100*tu13/(tu13+td13):null;
   const v21=tu21+td21>0?100*tu21/(tu21+td21):null;
   const ts=z.v?tdw/z.v:null;
   const trend=v13!=null&&v21>0&&ts!=null?v13+ts/v21+ts:null;
   out.push({pai,wr,ws,gold,trend});
  }return out;
 }
 for(const [sym,txt] of Object.entries(by)){
  const arr=txt.trim().split(/\r?\n/),rows=arr.slice(1).map(l=>{const [d,o,h,lo,c,v]=l.split(";");return {d,o:+o,h:+h,l:+lo,c:+c,v:+v}}).sort((a,b)=>a.d.localeCompare(b.d));
  const invalid=rows.filter(r=>!Number.isFinite(r.o)||!Number.isFinite(r.v)||r.v<=0||r.h<Math.max(r.o,r.c)||r.l>Math.min(r.o,r.c)).length;
  const dup=rows.filter((r,i)=>i&&r.d===rows[i-1].d).length;
  const jumps=rows.filter((r,i)=>i&&Math.abs(r.o/rows[i-1].c-1)>.45).length;
  if(invalid||dup||jumps)warnings.push({sym,invalid,dup,jumps});
  parsed[sym]={rows,ind:calc(rows)};
 }
 const EVENT_TYPES=["ALL","LOW_FILL","LOW_INSIDE","LOW_ENTER15","LOW_ENTER20","LOW_EXIT20","LOW_CONFIRMED","LOW_CONF_WT","LOW_CONF_GOLD","LOW_CONF_TREND","HIGH_FILL","HIGH_INSIDE","HIGH_ENTER85","HIGH_ENTER80","HIGH_EXIT80","HIGH_CONFIRMED","HIGH_CONF_WT","HIGH_CONF_TREND"];
 function flags(q,i){
  const v=q[i],p=q[i-1];if(!v||!p||v.pai==null||p.pai==null)return [];
  const a=v.pai,b=p.pai, arr=["ALL"];
  if(a<30)arr.push("LOW_FILL");
  if(a<=15)arr.push("LOW_INSIDE");
  if(a<=15&&b>15)arr.push("LOW_ENTER15");
  if(a<20&&b>=20)arr.push("LOW_ENTER20");
  if(a>20&&b<=20)arr.push("LOW_EXIT20");
  const lowRecent=q.slice(Math.max(0,i-10),i).some(x=>x.pai!=null&&x.pai<=15);
  const lowConf=a>20&&b<=20&&lowRecent;
  if(lowConf){
   arr.push("LOW_CONFIRMED");
   if(v.ws!=null&&v.wr>v.ws)arr.push("LOW_CONF_WT");
   if(q.slice(Math.max(0,i-10),i+1).some(x=>x.gold!=null&&x.gold<30))arr.push("LOW_CONF_GOLD");
   if(v.trend!=null&&p.trend!=null&&v.trend>p.trend)arr.push("LOW_CONF_TREND");
  }
  if(a>70)arr.push("HIGH_FILL");
  if(a>=85)arr.push("HIGH_INSIDE");
  if(a>=85&&b<85)arr.push("HIGH_ENTER85");
  if(a>80&&b<=80)arr.push("HIGH_ENTER80");
  if(a<80&&b>=80)arr.push("HIGH_EXIT80");
  const highRecent=q.slice(Math.max(0,i-10),i).some(x=>x.pai!=null&&x.pai>=85);
  const highConf=a<80&&b>=80&&highRecent;
  if(highConf){
   arr.push("HIGH_CONFIRMED");
   if(v.ws!=null&&v.wr<v.ws)arr.push("HIGH_CONF_WT");
   if(v.trend!=null&&p.trend!=null&&v.trend<p.trend)arr.push("HIGH_CONF_TREND");
  }return arr;
 }
 const events={},cover={};for(const t of EVENT_TYPES)events[t]=[];
 const flagCache={};
 for(const [sym,p] of Object.entries(parsed)){
  const {rows,ind}=p,all=[];
  for(let i=0;i<rows.length;i++)all.push(flags(ind,i));
  flagCache[sym]=all;
  const valid=rows.filter(x=>x.d>="2020-01-01"&&x.d<="2026-08-31");
  cover[sym]={rows:rows.length,start:rows[0]?.d,end:rows.at(-1)?.d,signalBars:valid.length};
  for(let i=250;i<rows.length-20;i++){
   if(rows[i].d<"2020-01-01"||rows[i].d>"2026-08-31")continue;
   const op=rows[i+1].o,close=j=>rows[j].c/op-1;
   const future=rows.slice(i+1,i+21);
   const e={sym,i,date:rows[i].d,r5:close(i+5),r10:close(i+10),r20:close(i+20),mfe:Math.max(...future.map(z=>z.h/op-1)),mae:Math.min(...future.map(z=>z.l/op-1))};
   for(const t of all[i])events[t].push(e);
  }
 }
 function stat(list,down,nonoverlap){
  const xs=[...list].sort((a,b)=>a.sym.localeCompare(b.sym)||a.i-b.i);
  const last={};const ev=nonoverlap?xs.filter(e=>{if(last[e.sym]!=null&&e.i-last[e.sym]<20)return false;last[e.sym]=e.i;return true}):xs;
  const n=ev.length;if(!n)return {n:0};
  return {n,stocks:new Set(ev.map(e=>e.sym)).size,hit5:pct(avg(ev.map(e=>(down?e.r5<0:e.r5>0)?1:0))),hit10:pct(avg(ev.map(e=>(down?e.r10<0:e.r10>0)?1:0))),hit20:pct(avg(ev.map(e=>(down?e.r20<0:e.r20>0)?1:0))),mean5:pct(avg(ev.map(e=>e.r5))),mean20:pct(avg(ev.map(e=>e.r20))),median20:pct(median(ev.map(e=>e.r20))),mfe20:pct(avg(ev.map(e=>e.mfe))),mae20:pct(avg(ev.map(e=>e.mae)))};
 }
 const eventSummary={};for(const [type,es] of Object.entries(events)){
  const down=type.startsWith("HIGH");
  eventSummary[type]={whole:stat(es,down,true),all:stat(es,down,false),early:stat(es.filter(e=>e.date<"2024-01-01"),down,true),late:stat(es.filter(e=>e.date>="2024-01-01"),down,true)};
 }
 const perStock={};
 for(const sym of Object.keys(parsed)){
  perStock[sym]={};
  for(const type of ["LOW_ENTER15","LOW_CONFIRMED","LOW_CONF_WT","HIGH_ENTER85","HIGH_CONFIRMED","HIGH_CONF_WT"])
   perStock[sym][type]=stat(events[type].filter(e=>e.sym===sym),type.startsWith("HIGH"),true);
 }
 function backtest(sym,buy,sell,startDate="2020-01-01"){
  const {rows}=parsed[sym],fs=flagCache[sym],endDate="2026-08-31";
  const iStart=rows.findIndex(r=>r.d>=startDate),iEnd=rows.findLastIndex(r=>r.d<=endDate);
  if(iStart<0||iEnd<iStart+2)return null;
  let cash=10000,shares=0,trades=0,entries=0,exits=0,investedBars=0,peak=10000,maxDD=0;
  const fee=.0015;
  for(let i=iStart;i<=iEnd;i++){
   // execute previous day fully confirmed signal at today's OPEN
   if(i>iStart){
    if(shares>0&&fs[i-1].includes(sell)){cash=shares*rows[i].o*(1-fee);shares=0;exits++;trades++}
    else if(!shares&&fs[i-1].includes(buy)){shares=cash*(1-fee)/rows[i].o;cash=0;entries++;trades++}
   }
   if(shares>0)investedBars++;
   const eq=cash+shares*rows[i].c;peak=Math.max(peak,eq);maxDD=Math.min(maxDD,eq/peak-1);
  }
  const end=cash+shares*rows[iEnd].c*(1-fee);
  const bh=10000*(1-fee)/rows[iStart].o*rows[iEnd].c*(1-fee);
  return {ret:end/10000-1,bh:bh/10000-1,mdd:maxDD,exposure:investedBars/(iEnd-iStart+1),trades,entries,exits,openPosition:shares>0};
 }
 const configs={raw:["LOW_ENTER15","HIGH_ENTER85"],confirm:["LOW_CONFIRMED","HIGH_CONFIRMED"],confirmWT:["LOW_CONF_WT","HIGH_CONF_WT"]},trading={};
 for(const [name,[buy,sell]] of Object.entries(configs)){
  const x=Object.keys(parsed).map(sym=>({sym,...backtest(sym,buy,sell)}));
  trading[name]={n:x.length,medianReturn:pct(median(x.map(z=>z.ret))),medianBuyHold:pct(median(x.map(z=>z.bh))),beatBuyHold:x.filter(z=>z.ret>z.bh).length,medianMdd:pct(median(x.map(z=>z.mdd))),medianExposure:pct(median(x.map(z=>z.exposure))),totalRoundTrips:x.reduce((a,z)=>a+z.exits,0),perStock:x.map(z=>({sym:z.sym,ret:pct(z.ret),bh:pct(z.bh),mdd:pct(z.mdd),exposure:pct(z.exposure),entries:z.entries,exits:z.exits}))};
 }
 return {status:"EXPLORATORY_NOT_STRATEGY_VALIDATED",assumptions:{version:"TDX-modified 14/3/21; WT Lag gamma 0.08",period:"2020-01-01..2026-08-31",future:"next open to 5/10/20 close",feesEvent:"none",feesRoundTrip:"0.15% per side",nonOverlap:"per symbol per event type 20 bars"},coverage:cover,warnings,events:eventSummary,perStock,trading};
}
const batches=process.argv.slice(2).map(f=>JSON.parse(fs.readFileSync(f,'utf8')));
process.stdout.write(JSON.stringify(study(batches),null,2)+'\n');
