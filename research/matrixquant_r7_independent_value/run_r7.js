
// MatrixQuant R7, fixed-protocol incremental information falsification.
// Usage: node run_r7.js training_01.json training_02.json training_03.json new_holdout_01.json new_holdout_02.json new_holdout_03.json new_holdout_04.json
// Fixed source and score criteria: PROTOCOL_FROZEN.md
'use strict';
const fs=require('fs');

function runR7(trainBatches,testBatches){
const trainSymbols=["AAPL","MSFT","NVDA","AMD","ABT","JNJ","AMZN","GOOGL","META","ORCL","LLY","JPM","BAC","GS","WMT","PG","COST","XOM","CAT","TSLA"];
const testSymbols=["V","MA","UNH","ABBV","MRK","PFE","HD","LOW","NKE","KO","PEP","DIS","NFLX","CRM","ADBE","INTC","CSCO","BA","UPS","MS"];
const variants={MODIFIED:{pk:14,sd:21,o:13,c:21,g:0.08,lag:true},ORIGINAL:{pk:20,sd:20,o:8,c:20,g:0.02,lag:false}};
const featureNames=["return5","return20","volatility20","closeRange20","candleCloseLoc","volumeLog5over20","SPYreturn5","SPYreturn20","trend","trendDelta5","goldRSI","goldBelow30","wtMain","wtMainMinusSignal","wtDifferenceChange","paiRaw","paiDelta1","paiHigh40","paiLowMinus40"];
const G={BASE:[0,1,2,3,4,5,6,7],Trend:[8,9],Gold:[10,11],WT:[12,13,14],PAI:[15,16,17,18]};
const modelKeys=["BASE","BASE_Trend","BASE_Gold","BASE_WT","BASE_PAI","FULL","NO_Trend","NO_Gold","NO_WT","NO_PAI"];
const idxs={BASE:G.BASE};
for(const type of ["Trend","Gold","WT","PAI"])idxs["BASE_"+type]=G.BASE.concat(G[type]);
idxs.FULL=featureNames.map((_,i)=>i);
for(const type of ["Trend","Gold","WT","PAI"])idxs["NO_"+type]=idxs.FULL.filter(j=>!G[type].includes(j));
function parse(batches){const r={};for(const b of batches)for(const [sym,t]of Object.entries(b.raw||{})){if(r[sym])throw Error("duplicate symbol "+sym);const a=t.trim().split(/\r?\n/);if(a[0]!=="datetime;open;high;low;close;volume")throw Error("schema "+sym);
 r[sym]=a.slice(1).map(l=>{const [d,o,h,lo,c,v]=l.split(";");return {d,o:+o,h:+h,l:+lo,c:+c,v:+v};}).sort((a,b)=>a.d.localeCompare(b.d));
 }return r}
const trainRaw=parse(trainBatches),testRaw=parse(testBatches);if(!testRaw.SPY)throw Error("SPY benchmark not present");
function check(data,symbols){const report=[];for(const sym of symbols){const v=data[sym];if(!v){report.push({sym,error:"missing"});continue;}let bad=0,dupe=0,gap=0;for(let i=0;i<v.length;i++){const z=v[i];if(!(z.l>0&&z.o>0&&z.c>0&&z.v>0&&z.h>=Math.max(z.o,z.c)&&z.l<=Math.min(z.o,z.c)))bad++;if(i){if(z.d===v[i-1].d)dupe++;if(Math.abs(z.o/v[i-1].c-1)>0.45)gap++;}}
 report.push({sym,bars:v.length,start:v[0].d,end:v.at(-1).d,bad,dupe,gap});}return report}
const qc=[...check(trainRaw,trainSymbols),...check(testRaw,testSymbols.concat("SPY"))];
if(qc.some(x=>x.error||x.bad||x.dupe||x.gap))throw Error("input OHLCV validation failed "+JSON.stringify(qc.filter(x=>x.error||x.bad||x.dupe||x.gap)));
const mean=a=>a.reduce((x,y)=>x+y,0)/a.length;
const ema=(x,prev,len)=>prev==null?x:prev+2/(len+1)*(x-prev);
function indicator(rows,cfg,spyMap){
 const arr=[],st=[],std=[],mainSeries=[],sdev=[];
 let prev10=null,dev10=null,comp21=null,previousLag=[0,0,0,0];
 let volPrev=null,upR=null,downR=null;
 const volDeltas=[];
 for(let i=0;i<rows.length;i++){
  const z=rows[i],typ=(z.h+z.l+z.c)/3;
  let stochastic=null;
  if(i>=cfg.pk-1){let high=-Infinity,low=Infinity;for(let j=i-cfg.pk+1;j<=i;j++){high=Math.max(high,rows[j].h);low=Math.min(low,rows[j].l)}if(high>low)stochastic=100*(z.c-low)/(high-low);}
  st.push(stochastic);
  let sd=null;if(i>=cfg.sd-1){let sum=0,sum2=0;for(let j=i-cfg.sd+1;j<=i;j++){const c=rows[j].c;sum+=c;sum2+=c*c;}const m=sum/cfg.sd;sd=Math.sqrt(Math.max(0,sum2/cfg.sd-m*m));}
  std.push(sd);
  let pai=null;if(i>=Math.max(cfg.pk+2,cfg.sd+cfg.pk-2)){const p=st.slice(i-2,i+1),s=std.slice(i-cfg.pk+1,i+1);if(p.length===3&&p.every(Number.isFinite)&&s.length===cfg.pk&&s.every(Number.isFinite)){const hi=Math.max(...s),lo=Math.min(...s);if(hi>lo)pai=((mean(p)-50)/50)*100*(sd-lo)/(hi-lo);}}
  prev10=ema(typ,prev10,10);dev10=ema(Math.abs(typ-prev10),dev10,10);
  if(dev10>0)comp21=ema((typ-prev10)/(.015*dev10),comp21,21);
  let wt=null;if(comp21!=null){
   const g=cfg.g,l=[0,0,0,0];l[0]=(1-g)*comp21+g*previousLag[0];for(let k=1;k<4;k++)l[k]=-g*l[k-1]+previousLag[k-1]+g*previousLag[k];previousLag=l;
   wt=cfg.lag?(l[0]+2*l[1]+2*l[2]+l[3])/6:comp21;
  }mainSeries.push(wt);
  const signal=i>=3&&mainSeries.slice(-4).every(v=>v!=null)?mean(mainSeries.slice(-4)):null;
  let gold=null,gv=null;
  if(i>=7){let sum=0;for(let j=i-7;j<=i;j++)sum+=Math.log(rows[j].h/rows[j].l)**2;gv=Math.sqrt(typ/(8*4*Math.log(2))*sum);}
  if(gv!=null&&volPrev!=null){
   const dd=gv-volPrev,up=Math.max(dd,0),down=Math.max(-dd,0);
   volDeltas.push({up,down});
   if(volDeltas.length===8){upR=mean(volDeltas.map(a=>a.up));downR=mean(volDeltas.map(a=>a.down));}
   else if(volDeltas.length>8){upR=(upR*7+up)/8;downR=(downR*7+down)/8;}
   if(upR!=null&&downR!=null)gold=upR+downR>0?100*upR/(upR+downR):50;
  }
  if(gv!=null)volPrev=gv;
  let trend=null;
  if(i>=Math.max(cfg.o,cfg.c)){let up1=0,dn1=0,up2=0,dn2=0;for(let j=i-cfg.o+1;j<=i;j++){const a=rows[j],b=rows[j-1],ap=(a.o+a.h+a.l+a.c)/4,bp=(b.o+b.h+b.l+b.c)/4;if(ap>bp)up1+=a.v*ap;else if(ap<bp)dn1+=a.v*ap;}
   for(let j=i-cfg.c+1;j<=i;j++){const a=rows[j],b=rows[j-1];if(a.c>b.c)up2+=a.v*a.c;else if(a.c<b.c)dn2+=a.v*a.c;}
   if(up1+dn1>0&&up2+dn2>0&&up2>0){const ln1=100*up1/(up1+dn1),ln2=100*up2/(up2+dn2),tdw=z.h>z.l?(2*z.c-z.l-z.h)/(z.h-z.l):0;if(ln2>0)trend=ln1+tdw/ln2+tdw;}
  }
  let base=null;
  if(i>=25&&spyMap.has(z.d)){
   const spy=spyMap.get(z.d);
   if(spy&&spy.r5!=null&&spy.r20!=null){
    const r5=z.c/rows[i-5].c-1,r20=z.c/rows[i-20].c-1;
    let mu=0,v=0;for(let j=i-19;j<=i;j++){const ret=Math.log(rows[j].c/rows[j-1].c);mu+=ret;v+=ret*ret;}
    mu/=20;const vol=Math.sqrt(Math.max(0,v/20-mu*mu));
    let hi=-Infinity,lo=Infinity,v5=0,v20=0;for(let j=i-19;j<=i;j++){hi=Math.max(hi,rows[j].h);lo=Math.min(lo,rows[j].l);v20+=rows[j].v;if(j>=i-4)v5+=rows[j].v;}
    base=[r5,r20,vol,hi>lo?(z.c-lo)/(hi-lo):null,z.h>z.l?(z.c-z.l)/(z.h-z.l):null,v20>0?Math.log((v5/5)/(v20/20)):null,spy.r5,spy.r20];
   }
  }
  const prev=arr.at(-1),wd=wt!=null&&signal!=null?wt-signal:null;
  const feats=base?base.concat([trend,prev&&prev.trend!=null&&trend!=null?trend-prev.trend5:null,gold,gold==null?null:Number(gold<30),wt,wd,prev&&prev.wd!=null&&wd!=null?wd-prev.wd:null,pai,prev&&prev.pai!=null&&pai!=null?pai-prev.pai:null,pai==null?null:Number(pai>40),pai==null?null:Number(pai< -40)]):null;
  arr.push({d:z.d,feat:feats,trend,trend5:arr.length>4?arr[arr.length-5].trend:null,gold,wt,wd,pai,y5:i+5<rows.length?+(rows[i+5].c>rows[i+1].o):null,y20:i+20<rows.length?+(rows[i+20].c>rows[i+1].o):null});
 }
 return arr;
}
const spyMap=new Map(),spy=testRaw.SPY;for(let i=20;i<spy.length;i++)spyMap.set(spy[i].d,{r5:spy[i].c/spy[i-5].c-1,r20:spy[i].c/spy[i-20].c-1});
function gather(data,symbols,cfg,isTrain){const ret=[];for(const sym of symbols){const ticks=indicator(data[sym],cfg,spyMap);
  for(let i=250;i<ticks.length;i++){const x=ticks[i];if((isTrain&&(x.d<"2020-01-01"||x.d>"2023-11-30"))||(!isTrain&&(x.d<"2024-01-01"||x.d>"2026-08-31")))continue;
    if(x.feat&&x.feat.length===featureNames.length&&x.feat.every(z=>typeof z==="number"&&Number.isFinite(z))&&x.y20!=null)ret.push({sym,d:x.d,month:x.d.slice(0,7),year:x.d.slice(0,4),x:x.feat,y5:x.y5,y20:x.y20});
  }
}return ret;}
function gaussian(H,g,p){const A=new Float64Array(H),b=new Float64Array(g);for(let j=0;j<p;j++){let pivot=j;for(let q=j+1;q<p;q++)if(Math.abs(A[q*p+j])>Math.abs(A[pivot*p+j]))pivot=q; if(Math.abs(A[pivot*p+j])<1e-12)return null;
  if(pivot!==j){for(let k=j;k<p;k++){let tmp=A[j*p+k];A[j*p+k]=A[pivot*p+k];A[pivot*p+k]=tmp;}let tmp=b[j];b[j]=b[pivot];b[pivot]=tmp;}
  const f=A[j*p+j];for(let k=j;k<p;k++)A[j*p+k]/=f;b[j]/=f;
  for(let q=0;q<p;q++){if(q===j)continue;const fac=A[q*p+j];if(fac===0)continue;for(let k=j;k<p;k++)A[q*p+k]-=fac*A[j*p+k];b[q]-=fac*b[j];}
}return Array.from(b);}
const sigmoid=z=>z>=0?1/(1+Math.exp(-z)):Math.exp(z)/(1+Math.exp(z));
function fit(train,indices,horizon){
 const n=train.length,p=indices.length+1,mu=new Float64Array(p),sd=new Float64Array(p);
 for(let j=1;j<p;j++){let su=0,su2=0;const col=indices[j-1];for(const z of train){const v=z.x[col];su+=v;su2+=v*v;}mu[j]=su/n;sd[j]=Math.sqrt(Math.max(0,su2/n-mu[j]*mu[j]));if(sd[j]<1e-9)sd[j]=1;}
 const X=new Float64Array(n*p),y=new Uint8Array(n);let positive=0;
 for(let i=0;i<n;i++){const r=train[i],start=i*p;X[start]=1;for(let j=1;j<p;j++)X[start+j]=(r.x[indices[j-1]]-mu[j])/sd[j];y[i]=r[horizon];positive+=y[i];}
 let w=new Float64Array(p),baseRate=positive/n;w[0]=Math.log(baseRate/(1-baseRate));
 const lambda=.01,maxIterations=9;let iterations=0,converged=false;
 for(let it=0;it<maxIterations;it++){
  const H=new Float64Array(p*p),g=new Float64Array(p);
  for(let i=0;i<n;i++){
   const offset=i*p;let score=0;for(let a=0;a<p;a++)score+=X[offset+a]*w[a];
   const prob=sigmoid(score),dif=prob-y[i],v=prob*(1-prob);
   for(let a=0;a<p;a++){
    const x=X[offset+a];g[a]+=dif*x;
    for(let b=0;b<=a;b++)H[a*p+b]+=v*x*X[offset+b];
   }
  }
  for(let a=0;a<p;a++){g[a]/=n;for(let b=0;b<=a;b++)H[a*p+b]/=n;
    if(a!==0){g[a]+=lambda*w[a];H[a*p+a]+=lambda;}
  }
  for(let a=0;a<p;a++)for(let b=0;b<a;b++)H[b*p+a]=H[a*p+b];
  const step=gaussian(H,g,p);if(!step)throw Error("singular Hessian");let mx=0;
  for(let a=0;a<p;a++){w[a]-=step[a];mx=Math.max(mx,Math.abs(step[a]));}iterations++;
  if(mx<1e-7){converged=true;break;}
 }
 return{weights:Array.from(w),mu:Array.from(mu),sd:Array.from(sd),columns:indices,iterations,converged,positiveRate:baseRate};
}
function predictions(fitted,rows){
 return rows.map(r=>{let z=fitted.weights[0];for(let j=1;j<fitted.weights.length;j++)z+=fitted.weights[j]*(r.x[fitted.columns[j-1]]-fitted.mu[j])/fitted.sd[j];return Math.min(1-1e-9,Math.max(1e-9,sigmoid(z)));});
}
function score(rows,pred,h){let b=0,ll=0,acc=0;const pair=[];
 for(let i=0;i<rows.length;i++){const y=rows[i][h],p=pred[i];b+=(p-y)**2;ll-=y*Math.log(p)+(1-y)*Math.log(1-p);acc+=+(Number(p>=.5)===y);pair.push({p,y});}
 pair.sort((a,b)=>a.p-b.p);let ranks=0,pos=0,neg=0;
 for(let i=0;i<pair.length;){let j=i+1;while(j<pair.length&&pair[i].p===pair[j].p)j++;const r=(i+1+j)/2;for(let k=i;k<j;k++)if(pair[k].y===1){ranks+=r;pos++;}else neg++;i=j}
 const auc=pos&&neg?(ranks-pos*(pos+1)/2)/(pos*neg):null;
 return{n:rows.length,brier:b/rows.length,logLoss:ll/rows.length,auc,accuracy:acc/rows.length,prevalence:rows.reduce((s,r)=>s+r[h],0)/rows.length};
}
function bootstrap(rows,base,comp,seed){
 const months=new Map(),symbols=new Map();let total=0,meanSum=0;
 for(let i=0;i<rows.length;i++){
  const item=rows[i],y=item.yy,a=(base[i]-y)**2-(comp[i]-y)**2;meanSum+=a;total++;
  if(!months.has(item.month))months.set(item.month,{sum:0,n:0});const m=months.get(item.month);m.sum+=a;m.n++;
  if(!symbols.has(item.sym))symbols.set(item.sym,{sum:0,n:0});const s=symbols.get(item.sym);s.sum+=a;s.n++;
 }
 let s=seed>>>0;const rand=()=>{s=(Math.imul(1664525,s)+1013904223)>>>0;return s/4294967296;};
 const entries=[...months.values()],n=entries.length,samples=[];for(let z=0;z<3000;z++){let sums=0,counts=0;for(let i=0;i<n;i++){const k=Math.floor(rand()*n),r=entries[k];sums+=r.sum;counts+=r.n;}samples.push(sums/counts);}
 samples.sort((a,b)=>a-b);
 const byStock=Object.fromEntries([...symbols.entries()].map(([sym,x])=>[sym,x.sum/x.n]));
 return{deltaBrier:meanSum/total,ci95:[samples[74],samples[2924]],months:n,positiveStockCount:Object.values(byStock).filter(x=>x>0).length,stockCount:Object.keys(byStock).length,byStock};
}
let results={meta:{status:"RESEARCH_ONLY",trainingStocks:trainSymbols,holdoutStocks:testSymbols,features:featureNames,groups:G,settings:variants,
 trainWindow:"2020-01-01..2023-11-30",testWindow:"2024-01-01..2026-08-31",l2:0.01,bootstrapReplicates:3000,splitCaveat:"2024–2026 data historically available now, symbol/date jointly withheld from model, not prospective future"},
 inputQC:qc,variant:{}};
for(const [vn,cfg] of Object.entries(variants)){
 const train=gather(trainRaw,trainSymbols,cfg,true),test=gather(testRaw,testSymbols,cfg,false);
 if(train.length<1000||test.length<1000)throw Error("insufficient rows "+vn+": "+train.length+"/"+test.length);
 const output={trainN:train.length,holdoutN:test.length,holdoutTickers:[...new Set(test.map(x=>x.sym))],horizons:{}};
 for(const h of [5,20]){
  const horizon="y"+h,keys={};const allPred={};
  for(const model of modelKeys){const fitted=fit(train,idxs[model],horizon),pred=predictions(fitted,test);
    allPred[model]=pred;
    keys[model]={...score(test,pred,horizon),iterations:fitted.iterations,converged:fitted.converged,coefficientCount:fitted.weights.length,trainingPrevalence:fitted.positiveRate};
  }
  const testRows=test.map(x=>({...x,yy:x[horizon]}));
  const comps={};
  for(const model of modelKeys){
   if(model==="BASE")continue;
   const baseline=model.startsWith("NO_")?"FULL":"BASE";
   const cmp=bootstrap(testRows,allPred[baseline],allPred[model],0x87ac34+(vn==="ORIGINAL"?8800:0)+h*13+model.length);
   comps[model]={reference:baseline,...cmp,deltaLogLoss:keys[baseline].logLoss-keys[model].logLoss,
    earlyDeltaBrier:null,lateDeltaBrier:null};
   for(const [label,subset] of [["early",testRows.map((x,i)=>({x,i})).filter(x=>x.x.d<"2026-01-01")],
      ["late",testRows.map((x,i)=>({x,i})).filter(x=>x.x.d>="2026-01-01")]]){
    let sum=0;for(const {x,i} of subset)sum+=(allPred[baseline][i]-x.yy)**2-(allPred[model][i]-x.yy)**2;
    comps[model][label+"DeltaBrier"]=subset.length?sum/subset.length:null;
   }
  }
  output.horizons[h]={models:keys,comparisons:comps};
 }
 results.variant[vn]=output;
}
for(const [v,o] of Object.entries(results.variant)){
 o.modulePass={};
 for(const g of ["Trend","Gold","WT","PAI"]){
  const h5=o.horizons[5].comparisons["BASE_"+g],h20=o.horizons[20].comparisons["BASE_"+g],a5=o.horizons[5].comparisons["NO_"+g],a20=o.horizons[20].comparisons["NO_"+g];
  // NO group compare is FULL - NO: a positive delta means dropping improves. For group value need negative.
  const pass=h5.ci95[0]>0&&h20.ci95[0]>0&&h5.positiveStockCount>o.holdoutTickers.length/2&&h20.positiveStockCount>o.holdoutTickers.length/2&&a5.deltaBrier<0&&a20.deltaBrier<0;
  o.modulePass[g]={pass,individual5:h5.deltaBrier,individual20:h20.deltaBrier,ablationWorseIfRemoved5:a5.deltaBrier<0,ablationWorseIfRemoved20:a20.deltaBrier<0};
 }
 const f5=o.horizons[5].comparisons.FULL,f20=o.horizons[20].comparisons.FULL;
 o.fullPass=f5.ci95[0]>0&&f20.ci95[0]>0&&f5.positiveStockCount>o.holdoutTickers.length/2&&f20.positiveStockCount>o.holdoutTickers.length/2;
}
results.status=Object.values(results.variant).some(o=>o.fullPass||Object.values(o.modulePass).some(p=>p.pass))?"POTENTIAL_INCREMENT_REQUIRES_FURTHER_VALIDATION":"NO_PROVEN_INCREMENTAL_VALUE";
return results;
}
if(require.main===module){
 const a=process.argv.slice(2);if(a.length<7)throw Error("expected 7 file args");
 const batches=a.map(p=>JSON.parse(fs.readFileSync(p,"utf8")));
 process.stdout.write(JSON.stringify(runR7(batches.slice(0,3),batches.slice(3)),null,2)+"\n");
}
