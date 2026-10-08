// Reproducible, pre-specified R4-A study (no order calls).\n'use strict';\nconst fs=require('node:fs');\nconst path=require('node:path');\nconst runStudy=function runStudy(inputs){
const N=20, W=250, H=20, TF=14400000, symbols=["BTC","ETH","BNB","SOL"];
const isF=Number.isFinite, S=(z,n)=>{let o=Array(z.length).fill(NaN);for(let i=n-1;i<z.length;i++){let a=z.slice(i-n+1,i+1);if(a.every(isF))o[i]=a.reduce((p,v)=>p+v,0)/n;}return o;};
const E=(z,n)=>{let out=[],v=NaN,a=2/(n+1);for(let x of z){if(isF(x))v=isF(v)?v+a*(x-v):x;out.push(v);}return out};
const R=(z,n)=>{let out=Array(z.length).fill(NaN),v=NaN,init=[];for(let i=0;i<z.length;i++){let x=z[i];if(!isF(x))continue;if(!isF(v)){init.push(x);if(init.length===n){v=init.reduce((s,y)=>s+y,0)/n;out[i]=v}}else{v=(v*(n-1)+x)/n;out[i]=v}}return out};
const T=(p,hi,lo,n)=>{let o=Array(p.length).fill(NaN);for(let i=n-1;i<p.length;i++){let h=hi.slice(i-n+1,i+1),l=lo.slice(i-n+1,i+1);if(!isF(p[i])||h.some(v=>!isF(v))||l.some(v=>!isF(v)))continue;let high=Math.max(...h),low=Math.min(...l);if(high>low)o[i]=(p[i]-low)/(high-low)*100;}return o};
const STD=(z,n)=>{let o=Array(z.length).fill(NaN);for(let i=n-1;i<z.length;i++){let b=z.slice(i-n+1,i+1);if(b.some(v=>!isF(v)))continue;let m=b.reduce((s,v)=>s+v,0)/n;o[i]=Math.sqrt(b.reduce((s,v)=>s+(v-m)**2,0)/n)}return o};
const cross=(a,b,i,up)=>i>0 && [a[i-1],a[i],b[i-1],b[i]].every(isF)&&(up?(a[i-1]<=b[i-1]&&a[i]>b[i]):(a[i-1]>=b[i-1]&&a[i]<b[i]));
const stats=(items)=>{const n=items.length;if(!n)return {n:0};const sort=a=>[...a].sort((x,y)=>x-y);const v=(name)=>items.map(x=>x[name]), q=(a,p)=>{let k=(a.length-1)*p,i=Math.floor(k),u=k-i;return a[i]*(1-u)+a[Math.min(i+1,a.length-1)]*u};let returns=v("r20"),sr=sort(returns);return {n,r5_mean:v("r5").reduce((a,b)=>a+b,0)/n,r20_mean:returns.reduce((a,b)=>a+b,0)/n,r20_median:q(sr,.5),r20_p10:q(sr,.1),r20_p90:q(sr,.9),positive:returns.filter(x=>x>0).length/n,mfe20_mean:v("mfe").reduce((a,b)=>a+b,0)/n,mae20_mean:v("mae").reduce((a,b)=>a+b,0)/n};};
const events=["BASE","PAI_UP5","PAI_DOWN5","WT_UP","WT_DOWN","WT_BULL_DIV","WT_BEAR_DIV","GOLD_ENTER_LT30","GOLD_EXIT_GT30"];
const results={metadata:{universe:symbols,timeframe:"4h",warmup:W,future5:5,future20:H,source:"frozen R2 Twelve Data USD OHLC no volume",producer:"R4-A standalone audit, no trade orders",formulas:"PAI default, WT default, GoldZoneRSI of PriceVolatility(hlc3,8)"},per_coin:{},aggregated:{}};
let all={};for(let k of events)all[k]=[];
for(const coin of symbols){
  const raw=inputs[coin],ls=raw.trim().split(/\r?\n/),header=ls.shift();
  if(header!=="datetime;open;high;low;close")throw Error("unexpected header "+coin+": "+header);
  const z=ls.map(line=>{let [t,o,h,l,c]=line.split(";");return {t,ms:Date.parse(t.replace(" ","T")+"Z"),o:Number(o),h:Number(h),l:Number(l),c:Number(c)};}).sort((a,b)=>a.ms-b.ms);
  if(z.length!==5000)throw Error("wrong data rows "+coin+" "+z.length);
  let quality={bars:z.length,start:z[0].t,end:z[z.length-1].t,gaps:0,duplicate:0,invalid:0};
  for(let i=0;i<z.length;i++){let a=z[i];if(![a.ms,a.o,a.h,a.l,a.c].every(isF)||a.l<=0||a.l>Math.min(a.o,a.c,a.h)||a.h<Math.max(a.o,a.c,a.l))quality.invalid++;if(i){let d=a.ms-z[i-1].ms;if(d===0)quality.duplicate++;else if(d!==TF)quality.gaps++}}
  if(quality.invalid||quality.duplicate||quality.gaps)throw Error("data failed "+coin+JSON.stringify(quality));
  const close=z.map(a=>a.c),hi=z.map(a=>a.h),lo=z.map(a=>a.l);
  const rawMom=S(T(close,hi,lo,20),3).map(v=>(v-50)/50);
  const dev=STD(close,20),vs=T(dev,dev,dev,20);
  const pai=rawMom.map((v,i)=>v*vs[i]);
  const src=z.map(a=>(a.h+a.l+a.c)/3),base=E(src,10),devE=E(src.map((v,i)=>Math.abs(v-base[i])),10);
  const ci=src.map((v,i)=>isF(devE[i])&&devE[i]>0?(v-base[i])/(0.015*devE[i]):NaN);
  const wt=E(ci,21),sig=S(wt,4),hist=wt.map((v,i)=>v-sig[i]);
  const priceVol=src.map((v,i)=>{if(i<7)return NaN;let sum=0;for(let k=i-7;k<=i;k++)sum+=Math.log(hi[k]/lo[k])**2;return Math.sqrt(v/(8*4*Math.log(2))*sum)});
  const up=priceVol.map((v,i)=>i&&isF(v)&&isF(priceVol[i-1])?Math.max(v-priceVol[i-1],0):NaN);
  const dn=priceVol.map((v,i)=>i&&isF(v)&&isF(priceVol[i-1])?Math.max(priceVol[i-1]-v,0):NaN);
  const ru=R(up,8),rd=R(dn,8),gold=ru.map((v,i)=>isF(v)&&isF(rd[i])?(rd[i]===0?(v>0?100:NaN):100-100/(1+v/rd[i])):NaN);
  const eventsByCoin={};for(let k of events)eventsByCoin[k]=[];
  // Pivot confirmed at index i, centered at k=i-1: equal values to LEFT allowed; to RIGHT forbidden.
  const pivots=(series,i,isHigh)=>{let k=i-1,v=series[k];if(k<5||i>=series.length||!isF(v))return false;for(let j=k-5;j<=i;j++){if(j===k)continue;let x=series[j];if(!isF(x))return false;if(isHigh?(j<k?x>v:x>=v):(j<k?x<v:x<=v))return false;}return true;};
  let prevLo=null,prevHi=null;
  for(let i=0;i<z.length;i++){
    let bull=false,bear=false;
    if(pivots(hist,i,false)){
      let curr={i,p:i-1,osc:hist[i-1],price:lo[i-1]};
      if(prevLo&&i-prevLo.i>=5&&i-prevLo.i<=60&&curr.osc>prevLo.osc&&curr.price<prevLo.price)bull=true;
      prevLo=curr;
    }
    if(pivots(hist,i,true)){
      let curr={i,p:i-1,osc:hist[i-1],price:hi[i-1]};
      if(prevHi&&i-prevHi.i>=5&&i-prevHi.i<=60&&curr.osc<prevHi.osc&&curr.price>prevHi.price)bear=true;
      prevHi=curr;
    }
    if(i<W||i+H>=z.length)continue;
    if(![pai[i],wt[i],sig[i],gold[i]].every(isF))continue;
    let start=z[i+1].o;
    let after=z.slice(i+1,i+1+H);
    let item={r5:z[i+5].c/start-1,r20:z[i+H].c/start-1,mfe:Math.max(...after.map(y=>y.h))/start-1,mae:Math.min(...after.map(y=>y.l))/start-1,t:z[i].t};
    let k=["BASE"];
    if(i>0&&isF(pai[i-1])&&pai[i-1]<=5&&pai[i]>5)k.push("PAI_UP5");
    if(i>0&&isF(pai[i-1])&&pai[i-1]>=-5&&pai[i]<-5)k.push("PAI_DOWN5");
    if(cross(wt,sig,i,true))k.push("WT_UP");
    if(cross(wt,sig,i,false))k.push("WT_DOWN");
    if(bull)k.push("WT_BULL_DIV");if(bear)k.push("WT_BEAR_DIV");
    if(i>0&&isF(gold[i-1])&&gold[i-1]>=30&&gold[i]<30)k.push("GOLD_ENTER_LT30");
    if(i>0&&isF(gold[i-1])&&gold[i-1]<=30&&gold[i]>30)k.push("GOLD_EXIT_GT30");
    for(let key of k){eventsByCoin[key].push(item);all[key].push({...item,coin})}
  }
  results.per_coin[coin]={quality,stats:Object.fromEntries(events.map(k=>[k,stats(eventsByCoin[k])])),range:{pai:[Math.min(...pai.filter(isF)),Math.max(...pai.filter(isF))],wt:[Math.min(...wt.filter(isF)),Math.max(...wt.filter(isF))],gold:[Math.min(...gold.filter(isF)),Math.max(...gold.filter(isF))]}};
}
for(let key of events){results.aggregated[key]=stats(all[key]);results.aggregated[key].per_coin_n=Object.fromEntries(symbols.map(c=>[c,results.per_coin[c].stats[key].n]));}
return results;
};\nconst dir=path.resolve(__dirname,'../matrixquant_crypto_mtf_r2/data');\nconst names=['BTC','ETH','BNB','SOL'];\nconst input=Object.fromEntries(names.map(c=>[c,fs.readFileSync(path.join(dir,'4h_'+c+'_USD.csv'),'utf8')]));\nprocess.stdout.write(JSON.stringify(runStudy(input),null,2)+'\\n');\n