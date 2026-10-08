function parseCsv(csv,tf,symbol){
 const lines=csv.trim().split(/\r?\n/),heads=lines.shift().split(";");if(!["datetime","open","high","low","close"].every(x=>heads.includes(x)))throw Error("bad CSV "+symbol);
 let rows=lines.map(line=>{let a=line.split(";"),o={};heads.forEach((name,i)=>o[name]=name==="datetime"?a[i]:Number(a[i]));return{t:o.datetime,o:o.open,h:o.high,l:o.low,c:o.close,v:o.volume}}).sort((a,b)=>a.t.localeCompare(b.t));
 let duplicate=0,invalid=0,gaps=0,dates=new Set();
 for(let i=0;i<rows.length;i++){let x=rows[i];if(dates.has(x.t))duplicate++;dates.add(x.t);if(![x.o,x.h,x.l,x.c].every(v=>Number.isFinite(v)&&v>0)||x.h<Math.max(x.o,x.c,x.l)||x.l>Math.min(x.o,x.c,x.h))invalid++;
 if(i){let toMs=t=>Date.parse(t.replace(" ","T")+"Z"), expected={"15min":900000,"1h":3600000,"4h":14400000,"1day":86400000}[tf];if(toMs(x.t)-toMs(rows[i-1].t)!==expected)gaps++;}}
 if(invalid||duplicate||rows.length<301)throw Error("invalid data "+symbol+" "+tf+" "+JSON.stringify({invalid,duplicate,n:rows.length}));
 return {z:rows,quality:{n:rows.length,start:rows[0].t,end:rows.at(-1).t,invalid,duplicate,gaps,volume_rows:rows.filter(x=>Number.isFinite(x.v)).length}};
}

function sma(a,n){return a.map((_,i)=>{if(i<n-1)return NaN;let b=a.slice(i-n+1,i+1);return b.every(Number.isFinite)?b.reduce((s,x)=>s+x,0)/n:NaN;});}

function ema(a,n){let v=NaN;return a.map(x=>{if(Number.isFinite(x))v=Number.isFinite(v)?v+2/(n+1)*(x-v):x;return v;});}

function std(a,n){return a.map((_,i)=>{if(i<n-1)return NaN;let b=a.slice(i-n+1,i+1);if(b.some(x=>!Number.isFinite(x)))return NaN;let m=b.reduce((s,x)=>s+x,0)/n;return Math.sqrt(b.reduce((s,x)=>s+(x-m)*(x-m),0)/n);});}

function stoch(x,h,l,n){return x.map((v,i)=>{if(i<n-1)return NaN;let H=h.slice(i-n+1,i+1),L=l.slice(i-n+1,i+1);if(!Number.isFinite(v)||H.some(x=>!Number.isFinite(x))||L.some(x=>!Number.isFinite(x)))return NaN;let high=Math.max(...H),low=Math.min(...L);return high>low?100*(v-low)/(high-low):NaN;});}

function over(a,b,i){return i>0&&Number.isFinite(a[i])&&Number.isFinite(a[i-1])&&Number.isFinite(b[i])&&Number.isFinite(b[i-1])&&a[i]>b[i]&&a[i-1]<=b[i-1];}

function under(a,b,i){return i>0&&Number.isFinite(a[i])&&Number.isFinite(a[i-1])&&Number.isFinite(b[i])&&Number.isFinite(b[i-1])&&a[i]<b[i]&&a[i-1]>=b[i-1];}

function divergences(z,osc,left=5,right=1){
 let bull=Array(z.length).fill(false),bear=Array(z.length).fill(false),priorLow=-1,priorHigh=-1;
 for(let t=left+right;t<z.length;t++){let k=t-right,v=osc[k];if(!Number.isFinite(v))continue;let islow=true,ishigh=true;
 for(let j=k-left;j<=k+right;j++){if(!Number.isFinite(osc[j])){islow=ishigh=false;break;}if(j!==k){if(osc[j]<=v)islow=false;if(osc[j]>=v)ishigh=false;}}
 if(islow){if(priorLow>=0&&k-priorLow-1>=5&&k-priorLow-1<=60&&v>osc[priorLow]&&z[k].l<z[priorLow].l)bull[t]=true;priorLow=k;}
 if(ishigh){if(priorHigh>=0&&k-priorHigh-1>=5&&k-priorHigh-1<=60&&v<osc[priorHigh]&&z[k].h>z[priorHigh].h)bear[t]=true;priorHigh=k;}
 }return {bull,bear};
}

function derive(z){
 let c=z.map(x=>x.c),h=z.map(x=>x.h),l=z.map(x=>x.l),mom=sma(stoch(c,h,l,20),3).map(v=>(v-50)/50),st=std(c,20),vol=stoch(st,st,st,20),pai=mom.map((v,i)=>v*vol[i]);
 let source=z.map(x=>(x.h+x.l+x.c)/3),base=ema(source,10),dev=ema(source.map((v,i)=>Math.abs(v-base[i])),10),ci=source.map((v,i)=>dev[i]>0?(v-base[i])/(.015*dev[i]):NaN),wt=ema(ci,21),signal=sma(wt,4),hist=wt.map((v,i)=>v-signal[i]);
 let {bull,bear}=divergences(z,hist),plus=Array(z.length).fill(5),minus=Array(z.length).fill(-5),state=pai.map((v,i)=>Number.isFinite(v)&&v>5&&wt[i]>signal[i]),recent=bull.map((v,i)=>bull.slice(Math.max(0,i-5),i+1).some(Boolean));
 return{pai,wt,signal,hist,bull,bear,plus,minus,state,recent};
}

function makeFlags(z,a,name){
 let ent=Array(z.length).fill(false),exit=Array(z.length).fill(false),{pai,wt,signal,bear,plus,minus,state,recent}=a;
 for(let i=1;i<z.length;i++){let pUp=over(pai,plus,i),pSlowDn=under(pai,minus,i),pFastDn=under(pai,plus,i),wtUp=over(wt,signal,i),wtDn=under(wt,signal,i),fresh=state[i]&&!state[i-1],now=state[i]&&recent[i],before=state[i-1]&&recent[i-1];
 if(name==="PAI_SLOW"){ent[i]=pUp;exit[i]=pSlowDn;}
 else if(name==="PAI_FAST"){ent[i]=pUp;exit[i]=pFastDn;}
 else if(name==="PAI_WT"){ent[i]=fresh;exit[i]=pai[i]<-5||wt[i]<signal[i];}
 else if(name==="WT_WITH_PAI"){ent[i]=wtUp&&pai[i]>-5;exit[i]=wtDn;}
 else if(name==="WT_BULL_CONFIRM"){ent[i]=now&&!before;exit[i]=pai[i]<-5||wt[i]<signal[i];}
 else if(name==="PAI_BEAR_EXIT"){ent[i]=pUp;exit[i]=pSlowDn||bear[i];}
 else if(name==="PAI_WT_BEAR_EXIT"){ent[i]=fresh;exit[i]=pai[i]<-5||wt[i]<signal[i]||bear[i];}
 }return{ent,exit};
}

function backtest(z,flags,start,end,fee){
 if(start<0||end<=start||end>=z.length)throw Error("invalid bounds "+start+" "+end);
 let money=10000,qty=0,base=0,n=0,wins=0,exp=0,mdd=0,peak=10000;
 for(let i=start;i<=end;i++){
  if(i>start){let j=i-1;if(qty>0&&flags.exit[j]){money=qty*z[i].o*(1-fee);qty=0;n++;if(money>base)wins++;}else if(qty===0&&flags.ent[j]){base=money;qty=money*(1-fee)/z[i].o;money=0;}}
  if(qty>0)exp++;let v=money+qty*z[i].c;peak=Math.max(peak,v);mdd=Math.min(mdd,v/peak-1);
 }
 if(qty>0){money=qty*z[end].c*(1-fee);n++;if(money>base)wins++;mdd=Math.min(mdd,money/peak-1);}
 return{ret:money/10000-1,bh:z[end].c/z[start].o*(1-fee)**2-1,mdd,trades:n,wins,win_rate:n?wins/n:null,exposure:exp/(end-start+1),from:z[start].t,to:z[end].t};
}

function eventMetric(z,a,start,end){
 let types={PAI_BUY:[],PAI_SELL:[],WT_BULL:[],WT_BEAR:[]};
 for(let t=start;t<=Math.min(end,z.length-21);t++){if(over(a.pai,a.plus,t))types.PAI_BUY.push(t);if(under(a.pai,a.minus,t))types.PAI_SELL.push(t);if(a.bull[t])types.WT_BULL.push(t);if(a.bear[t])types.WT_BEAR.push(t);}
 let ret={};for(let [k,indices] of Object.entries(types)){
  let n=indices.length,rs=[],mfe=[],mae=[];
  for(let t of indices){let entry=z[t+1].o,part=z.slice(t+1,t+21),high=Math.max(...part.map(x=>x.h)),low=Math.min(...part.map(x=>x.l));rs.push(z[t+20].c/entry-1);mfe.push(high/entry-1);mae.push(low/entry-1);}
  ret[k]={n,mean20:n?rs.reduce((s,x)=>s+x,0)/n:null,pos20:n?rs.filter(x=>x>0).length/n:null,meanMFE:n?mfe.reduce((s,x)=>s+x,0)/n:null,meanMAE:n?mae.reduce((s,x)=>s+x,0)/n:null};
 }return ret;
}

function median(a){a=a.filter(Number.isFinite).sort((x,y)=>x-y);return a.length?(a.length%2?a[Math.floor(a.length/2)]:(a[a.length/2-1]+a[a.length/2])/2):null;}

function executeRound(inputs){
 let tfList=["15min","1h","4h","1day"],coins=["BTC/USD","ETH/USD","BNB/USD","SOL/USD"],names=["PAI_SLOW","PAI_FAST","PAI_WT","WT_WITH_PAI","WT_BULL_CONFIRM","PAI_BEAR_EXIT","PAI_WT_BEAR_EXIT"],rows=[],errors=[];
 for(let tf of tfList)for(let coin of coins){try{let key=tf+"_"+coin.replace("/","_");if(!inputs[key])throw Error("missing snapshot");
  let {z,quality}=parseCsv(inputs[key],tf,coin),a=derive(z),start=250,split=start+Math.floor((z.length-1-start)*.6),last=z.length-1,models={};
  for(let name of names){let ff=makeFlags(z,a,name);models[name]={early:backtest(z,ff,start,split-1,.0015),late:backtest(z,ff,split,last,.0015),full:backtest(z,ff,start,last,.0015)};
   if(name==="PAI_SLOW"||name==="PAI_WT")models[name].late_sensitivity={"0.05pct":backtest(z,ff,split,last,.0005),"0.30pct":backtest(z,ff,split,last,.003)};}
  rows.push({coin,timeframe:tf,quality,late_start:z[split].t,models,events:eventMetric(z,a,split,last)});
 }catch(e){errors.push({tf,coin,error:String(e)});}}
 let summary=[];for(let tf of tfList)for(let name of names){let sample=rows.filter(x=>x.timeframe===tf),a=sample.map(x=>x.models[name].late);if(!a.length)continue;
 summary.push({timeframe:tf,rule:name,coins:a.length,median_late_return:median(a.map(x=>x.ret)),median_late_buy_hold:median(a.map(x=>x.bh)),median_late_drawdown:median(a.map(x=>x.mdd)),median_late_exposure:median(a.map(x=>x.exposure)),beat_hold:a.filter(x=>x.ret>x.bh).length,positive:a.filter(x=>x.ret>0).length,total_trades:a.reduce((s,x)=>s+x.trades,0)});}
 return{method:{data:"Twelve Data; 16 saved CSV snapshots; spot-equivalent, no volume",warmup:250,fee_per_side:.0015,split:"60% early / 40% late chronological, not virgin OOS",execution:"close confirmed, next open",critical:"Pine numerical parity not yet independently validated"},rows,summary,errors};
}


/*
 * MatrixQuant R3 TradingView CSV parity validator.
 * Usage: node compare_tv_export.js <TradingView export.csv> [--warmup=250] [--abs-tol=0.0001]
 * Uses TV-exported OHLC (NOT Twelve Data). Numeric output and confirmed-bar
 * signal flags are checked independently. No trade orders, no network access.
 * The R2 engine above is retained byte-for-byte for its core functions.
 */
const fs = require("fs");
const path = require("path");

function parseRFC4180(content) {
  let out = [], row = [], val = "", quoted = false, i = 0;
  content = content.replace(/^\uFEFF/, "");
  for (; i < content.length; i++) {
    let c = content[i];
    if (c === '"') {
      if (quoted && content[i + 1] === '"') {val += '"'; i++;}
      else quoted = !quoted;
    } else if (!quoted && c === ',') {row.push(val); val = "";}
    else if (!quoted && (c === "\n" || c === "\r")) {
      if (c === "\r" && content[i + 1] === "\n") i++;
      row.push(val); if(row.some(x => x.length)) out.push(row);
      row = []; val = "";
    } else val += c;
  }
  if (quoted) throw Error("Unterminated CSV quoted field");
  row.push(val);if (row.some(x=>x.length)) out.push(row);
  return out;
}
function exportedHeader(headers, wanted, exact=false) {
  let candidates=headers.map((h,i)=>({h:String(h).trim(),i})).filter(x=>exact?x.h.toLowerCase()===wanted.toLowerCase():x.h.endsWith(wanted));
  if (candidates.length!==1) throw Error("Expected exactly one TradingView column for "+wanted+", found "+candidates.length+". Columns: "+headers.join(" | "));
  return candidates[0].i;
}
function tvRows(text) {
  let arr=parseRFC4180(text),headers=arr.shift();
  if (!headers?.length) throw Error("Empty TradingView CSV");
  const fields=["PARITY_PAI_RAW","PARITY_WT_RAW","PARITY_WT_SIGNAL_RAW","PARITY_WT_HIST_RAW",
    "PARITY_WT_PIVOT_LOW_CONFIRMED","PARITY_WT_PIVOT_HIGH_CONFIRMED","PARITY_WT_BULL_CONFIRMED",
    "PARITY_WT_BEAR_CONFIRMED","PARITY_PAI_PIVOT_LOW_CONFIRMED","PARITY_PAI_PIVOT_HIGH_CONFIRMED",
    "PARITY_PAI_BULL_CONFIRMED","PARITY_PAI_BEAR_CONFIRMED","PARITY_PAI_UP5_CONFIRMED",
    "PARITY_PAI_DOWN_MINUS5_CONFIRMED"];
  const meta=["open","high","low","close"].reduce((o,key)=>(o[key]=exportedHeader(headers,key,true),o),{});
  const tc=["time","datetime","date"].map(name=>{let i=headers.findIndex(h=>h.trim().toLowerCase()===name);return i>=0?i:null;}).find(x=>x!==null);
  if(tc===undefined)throw Error("Cannot identify TradingView time/date column: "+headers.join("|"));
  let fx={};for(let field of fields)fx[field]=exportedHeader(headers,field);
  let rows=arr.map((r,i)=>{
    if(r.length!==headers.length)throw Error("CSV bad column count at data row "+(i+2));
    let x={t:r[tc]};for(let name of ["open","high","low","close"])x[({open:"o",high:"h",low:"l",close:"c"})[name]]=Number(r[meta[name]]);
    x.v=NaN;x.tv={};
    for(let [field,idx] of Object.entries(fx))x.tv[field]=r[idx].trim()===""?NaN:Number(r[idx]);
    return x;
  });
  if(rows.length>=2 && String(rows[0].t)>String(rows.at(-1).t))rows.reverse();
  if(rows.length<350)throw Error("Not enough exported bars (need >350 including warm-up); got "+rows.length);
  const times=new Set();for(let r of rows) {
    if(times.has(r.t))throw Error("TradingView CSV contains duplicate timestamp "+r.t);times.add(r.t);
    if(![r.o,r.h,r.l,r.c].every(x=>Number.isFinite(x)&&x>0)||r.h<Math.max(r.o,r.c,r.l)||r.l>Math.min(r.o,r.c,r.h))throw Error("Invalid OHLC at "+r.t);
  }
  return {rows,fields};
}
function pivotAll(z,line,left,right,minSpacing,maxSpacing) {
  let pl=Array(z.length).fill(false),ph=Array(z.length).fill(false),bull=Array(z.length).fill(false),bear=Array(z.length).fill(false),prevL=-1,prevH=-1;
  for(let t=left+right;t<z.length;t++){
    const k=t-right,mid=line[k];if(!Number.isFinite(mid))continue;
    let isL=true,isH=true;
    for(let j=k-left;j<=k+right;j++) {
      if(!Number.isFinite(line[j])){isL=isH=false;break;}
      // Pine ta.pivotlow/high chooses the most recent bar on an equal-value
      // plateau: ties allowed to the left, never to the confirming right.
      if(j<k){if(line[j]<mid)isL=false;if(line[j]>mid)isH=false;}
      if(j>k){if(line[j]<=mid)isL=false;if(line[j]>=mid)isH=false;}
    }
    if(isL){pl[t]=true;if(prevL>=0&&k-prevL-1>=minSpacing&&k-prevL-1<=maxSpacing&&mid>line[prevL]&&z[k].l<z[prevL].l)bull[t]=true;prevL=k;}
    if(isH){ph[t]=true;if(prevH>=0&&k-prevH-1>=minSpacing&&k-prevH-1<=maxSpacing&&mid<line[prevH]&&z[k].h>z[prevH].h)bear[t]=true;prevH=k;}
  }
  return{pl,ph,bull,bear};
}
function compareTV(csvText,opts={}){
  let {rows,fields}=tvRows(csvText),ind=derive(rows),wp=pivotAll(rows,ind.hist,5,1,5,60),pp=pivotAll(rows,ind.pai,2,2,2,10),warmup=opts.warmup??250,absTol=opts.absTol??0.0001;
  if(rows.length-warmup<100)throw Error("Too few compare bars after warmup");
  let pred={
    PARITY_PAI_RAW:ind.pai,PARITY_WT_RAW:ind.wt,PARITY_WT_SIGNAL_RAW:ind.signal,PARITY_WT_HIST_RAW:ind.hist,
    PARITY_WT_PIVOT_LOW_CONFIRMED:wp.pl,PARITY_WT_PIVOT_HIGH_CONFIRMED:wp.ph,
    PARITY_WT_BULL_CONFIRMED:ind.bull,PARITY_WT_BEAR_CONFIRMED:ind.bear,
    PARITY_PAI_PIVOT_LOW_CONFIRMED:pp.pl,PARITY_PAI_PIVOT_HIGH_CONFIRMED:pp.ph,
    PARITY_PAI_BULL_CONFIRMED:pp.bull,PARITY_PAI_BEAR_CONFIRMED:pp.bear,
    PARITY_PAI_UP5_CONFIRMED:rows.map((x,i)=>over(ind.pai,ind.plus,i)),
    PARITY_PAI_DOWN_MINUS5_CONFIRMED:rows.map((x,i)=>under(ind.pai,ind.minus,i))
  };
  let out={status:"PENDING",bars:rows.length,compared_from:rows[warmup].t,compared_to:rows.at(-1).t,warmup,abs_tolerance:absTol,fields:{},total_mismatches:0,first_mismatches:[]};
  for(let name of fields){let actual=pred[name],continuous=name.endsWith("_RAW");
    let count=0,bad=0,maxDiff=0,meanDiff=0;
    for(let i=warmup;i<rows.length;i++){
      let want=continuous?actual[i]:(actual[i]?1:0),got=rows[i].tv[name];
      if(!Number.isFinite(want)||!Number.isFinite(got)){bad++;if(out.first_mismatches.length<35)out.first_mismatches.push({column:name,t:rows[i].t,i,reason:"not numeric",tv:got,js:want});continue;}
      let diff=Math.abs(want-got),fails=continuous?diff>absTol:(got!==want);
      count++;maxDiff=Math.max(maxDiff,diff);meanDiff+=diff;
      if(fails){bad++;if(out.first_mismatches.length<35)out.first_mismatches.push({column:name,t:rows[i].t,i,tv:got,js:want,absolute_delta:diff});}
    }
    out.fields[name]={compared:count,mismatches:bad,max_absolute_delta:maxDiff,mean_absolute_delta:count?meanDiff/count:null};
    out.total_mismatches+=bad;
  }
  out.status=out.total_mismatches===0?"CSV_VALUES_MATCH_JS_RECONSTRUCTION":"MISMATCH_REQUIRES_AUDIT";
  out.disclaimer="This validates only the supplied TradingView chart CSV against the JS formulas for identical OHLC. Price-feed and actual Binance-USDM trading parity remain separate gates.";
  return out;
}
if (require.main===module) {
 let [source,...args]=process.argv.slice(2);
 if(!source){console.error("Usage: node compare_tv_export.js <tv-chart-export.csv> [--warmup=250] [--abs-tol=0.0001]");process.exit(2);}
 let opts={};
 for(let v of args){if(v.startsWith("--warmup="))opts.warmup=Number(v.slice(9));if(v.startsWith("--abs-tol="))opts.absTol=Number(v.slice(10));}
 try{
  const report=compareTV(fs.readFileSync(source,"utf8"),opts);
  const output=path.join(path.dirname(source),path.basename(source).replace(/\.csv$/i,"")+"_PARITY_REPORT.json");
  fs.writeFileSync(output,JSON.stringify(report,null,2)+"\n");
  console.log(JSON.stringify({status:report.status,compared_bars:report.bars-report.warmup,mismatches:report.total_mismatches,output,examples:report.first_mismatches.slice(0,5)}));
  if(report.total_mismatches)process.exitCode=1;
 }catch(e){console.error("PARITY_INPUT_OR_ENGINE_ERROR:",e.message);process.exitCode=2;}
}

// Public API used by offline regression tests; no side effects.
module.exports = {compareTV,tvRows,pivotAll,derive,backtest};
