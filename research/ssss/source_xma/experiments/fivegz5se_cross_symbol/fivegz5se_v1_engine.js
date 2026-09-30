// Deterministic FIVEGZ5SE SCTYPE=1 replay engine for research.
// Frozen from AMZN 2025 reconstruction. Formula-native action labels are NOT used.
// Exposes globalThis.FIVEGZ5SE_V1 = { build, simulate, oneTrade, rank }.

(function(){
  const rank={SHORT:-2,LIGHT_SHORT:-1,GRAY:0,LIGHT_LONG:1,LONG:2};

  function parseCsv(text){
    const lines=text.trim().split(/\r?\n/);
    const hdr=lines[0].split(",");
    return lines.slice(1).filter(Boolean).map(line=>{
      const p=line.split(","),o={}; hdr.forEach((h,i)=>o[h]=p[i]);
      return {date:o.Date,open:+o.Open,high:+o.High,low:+o.Low,close:+o.Close,volume:+o.Volume};
    }).filter(r=>r.date&&Number.isFinite(r.close)).sort((a,b)=>a.date.localeCompare(b.date));
  }

  function build(text){
    const raw=parseCsv(text);
    const N=raw.length,C=raw.map(r=>r.close),H=raw.map(r=>r.high),L=raw.map(r=>r.low),V=raw.map(r=>r.volume);
    const blank=()=>Array(N).fill(null);
    function ma(a,n){const o=blank(),q=[];let s=0;for(let i=0;i<N;i++){q.push(a[i]);s+=a[i]??0;if(q.length>n)s-=q.shift()??0;if(q.length===n&&q.every(Number.isFinite))o[i]=s/n;}return o}
    function ema(a,n){const o=blank(),k=2/(n+1);let p=null;for(let i=0;i<N;i++){const x=a[i];if(!Number.isFinite(x))continue;p=p==null?x:k*x+(1-k)*p;o[i]=p;}return o}
    function sma(a,n,m){const o=blank();let p=null;for(let i=0;i<N;i++){const x=a[i];if(!Number.isFinite(x))continue;p=p==null?x:(m*x+(n-m)*p)/n;o[i]=p;}return o}
    function roll(a,n,fn){const o=blank();for(let i=n-1;i<N;i++){const w=a.slice(i-n+1,i+1);if(w.every(Number.isFinite))o[i]=fn(w);}return o}
    const hhv=(a,n)=>roll(a,n,w=>Math.max(...w)),llv=(a,n)=>roll(a,n,w=>Math.min(...w)),std=(a,n)=>roll(a,n,w=>{const m=w.reduce((s,x)=>s+x,0)/n;return Math.sqrt(w.reduce((s,x)=>s+(x-m)*(x-m),0)/n)});
    function count(c,n){const o=blank();let s=0;for(let i=0;i<N;i++){s+=c[i]?1:0;if(i>=n)s-=c[i-n]?1:0;if(i>=n-1)o[i]=s;}return o}
    function forecast(a,n){const o=blank(),mx=(n-1)/2;let den=0;for(let k=0;k<n;k++)den+=(k-mx)*(k-mx);for(let i=n-1;i<N;i++){const y=a.slice(i-n+1,i+1);if(!y.every(Number.isFinite))continue;const my=y.reduce((s,x)=>s+x,0)/n;let num=0;for(let k=0;k<n;k++)num+=(k-mx)*(y[k]-my);o[i]=my+(num/den)*(n-1)/2;}return o}

    const volMA5=ma(V,5),volMA20=ma(V,20),MA20=ma(C,20),relVol=V.map((x,i)=>volMA20[i]?x/volMA20[i]:null),hslMA5=ma(relVol,5);
    const tr=C.map((_,i)=>i===0?H[i]-L[i]:Math.max(H[i]-L[i],Math.abs(H[i]-C[i-1]),Math.abs(L[i]-C[i-1]))),atr14=ma(tr,14),atrMA50=ma(atr14,50),volRatio=atr14.map((x,i)=>x!=null&&atrMA50[i]?x/atrMA50[i]:null);
    const amp=C.map((_,i)=>i?(H[i]-L[i])/C[i-1]*100:null),ampAtr=amp.map((x,i)=>x!=null&&atr14[i]!=null?x/(atr14[i]/C[i-1]*100):null),shock=ampAtr.map(x=>x!=null?(x>2?1+(x-2)*.3:1):null),emotionVol=volRatio.map(x=>x!=null?1+(x-1)*.1:null),emotionGain=volRatio.map(x=>x!=null?1+(x-1)*.5:null),washVol=emotionVol.map(x=>x!=null?Math.max(Math.min(2.5*x,3),1.2):null),washGain=emotionGain.map((x,i)=>x!=null&&shock[i]!=null?Math.max(Math.min(5*x*shock[i],12),.5):null),bias20=C.map((x,i)=>MA20[i]?(x-MA20[i])/MA20[i]*100:null);

    const V2=ema(C,5),V3=C.map((x,i)=>V2[i]!=null?(x-V2[i])*100/x:null),V4=V3.map(Number.isFinite),LL30=llv(L,30),HH30=hhv(H,30),V8=C.map((x,i)=>LL30[i]!=null&&HH30[i]!==LL30[i]?(x-LL30[i])/(HH30[i]-LL30[i])*100:null),V9=sma(V8,6,1),V10=sma(V9,3,1),V11=ema(C,17);
    const LL9=llv(L,9),HH9=hhv(H,9),V12=C.map((x,i)=>LL9[i]!=null&&HH9[i]!==LL9[i]?(x-LL9[i])/(HH9[i]-LL9[i])*100:null),V13=sma(V12,3,1),V14=sma(V13,3,1),V15=V13.map((x,i)=>x!=null&&V14[i]!=null?3*x-2*V14[i]:null);
    const up=C.map((x,i)=>i?Math.max(x-C[i-1],0):null),absd=C.map((x,i)=>i?Math.abs(x-C[i-1]):null),sup=sma(up,9,1),sab=sma(absd,9,1),V18=sup.map((x,i)=>x!=null&&sab[i]?x/sab[i]*100:null);
    const F20=forecast(ema(C,5),6),F21=forecast(ema(C,8),6),F22=forecast(ema(C,11),6),F23=forecast(ema(C,14),6),F24=forecast(ema(C,17),6),F25=F20.map((x,i)=>[x,F21[i],F22[i],F23[i],F24[i]].every(Number.isFinite)?x+F21[i]+F22[i]+F23[i]-4*F24[i]:null),F26=ema(F25,2);

    const tL=Array(N).fill(false),tS=Array(N).fill(false),tlL=Array(N).fill(false),tlS=Array(N).fill(false),tabs=blank();
    for(let i=0;i<N;i++){
      tabs[i]=i>=3&&V10[i]!=null&&V10[i-3]!=null?V10[i]-V10[i-3]:null;
      const vok=volMA20[i]!=null&&V[i]>=volMA20[i],vbad=i>0&&volMA20[i]!=null&&((V[i]>=volMA20[i]*1.2&&C[i]<C[i-1])||(V[i]<=volMA20[i]*.95)),bl=V9[i]!=null&&V10[i]!=null&&i>0&&V10[i-1]!=null&&V9[i]>V10[i]&&V10[i]>V10[i-1]&&V3[i]>-.5,bs=V9[i]!=null&&V10[i]!=null&&i>0&&V10[i-1]!=null&&V9[i]<V10[i]&&V10[i]<V10[i-1]&&V3[i]<.5;
      tL[i]=!!(bl&&vok&&tabs[i]>=2&&V4[i]); tS[i]=!!(bs&&tabs[i]<=-1.15&&vbad&&V4[i]); tlL[i]=!!(bl&&!tL[i]); tlS[i]=!!(bs&&!tS[i]);
    }

    const tc=count(tL,2),mstd=std(F26,5),mL=Array(N).fill(false),mS=Array(N).fill(false),mlL=Array(N).fill(false),mlS=Array(N).fill(false);
    for(let i=0;i<N;i++){
      const sl=i>0&&F26[i]!=null&&F26[i-1]!=null?F26[i]-F26[i-1]:null,th=mstd[i]!=null?mstd[i]*.35:null,bl=V9[i]!=null&&V10[i]!=null&&V9[i]>V10[i],bs=V9[i]!=null&&V10[i]!=null&&V9[i]<V10[i];
      mL[i]=!!(bl&&sl!=null&&th!=null&&sl>th); mS[i]=!!(bs&&sl!=null&&th!=null&&sl<-th); mlL[i]=!!(bl&&sl!=null&&th!=null&&!(sl>th)); mlS[i]=!!(bs&&sl!=null&&th!=null&&!(sl<-th));
    }

    const aL=Array(N).fill(false),aS=Array(N).fill(false),alL=Array(N).fill(false),alS=Array(N).fill(false);
    for(let i=0;i<N;i++){
      const jc=i>=2&&V15[i]!=null&&V15[i-2]!=null?V15[i]-V15[i-2]:null,rc=i>=2&&V18[i]!=null&&V18[i-2]!=null?V18[i]-V18[i-2]:null,bu=V9[i]!=null&&V10[i]!=null&&V9[i]>V10[i],be=V9[i]!=null&&V10[i]!=null&&V9[i]<V10[i],pr=i>=20&&V9[i]!=null&&V10[i]!=null&&Math.abs(V9[i]-V10[i])<2.5&&tc[i]!==2&&MA20[i]!=null&&MA20[i-20]!=null&&MA20[i]>MA20[i-20]*.98,tal=bu&&((jc!=null&&jc>=8)||(rc!=null&&rc>=6)),tas=be&&((jc!=null&&jc<=-8)||(rc!=null&&rc<=-6)),ob=pr&&((jc!=null&&jc<=-8)||(rc!=null&&rc<=-6))&&((V15[i]!=null&&V15[i]<30)||(V18[i]!=null&&V18[i]<40)),os=pr&&((jc!=null&&jc>=8)||(rc!=null&&rc>=6))&&((V15[i]!=null&&V15[i]>70)||(V18[i]!=null&&V18[i]>80));
      aL[i]=tal||ob; aS[i]=tas||os;
      alL[i]=(bu&&((jc!=null&&jc>0)||(rc!=null&&rc>0))&&!tal)||(pr&&((V15[i]!=null&&V15[i]<40)||(V18[i]!=null&&V18[i]<50))&&((jc!=null&&jc>0)||(rc!=null&&rc>0))&&!ob);
      alS[i]=(be&&((jc!=null&&jc<0)||(rc!=null&&rc<0))&&!tas)||(pr&&((V15[i]!=null&&V15[i]>60)||(V18[i]!=null&&V18[i]>70))&&((jc!=null&&jc<0)||(rc!=null&&rc<0))&&!os);
    }

    const HH15=hhv(H,15),LL12=llv(L,12),cL=Array(N).fill(false),cS=Array(N).fill(false),clL=Array(N).fill(false),clS=Array(N).fill(false),bear=Array(N).fill(false);
    for(let i=0;i<N;i++){
      const healthy=relVol[i]!=null&&relVol[i]>.4&&relVol[i]<12,pu=i>0&&V3[i]>-.4&&V11[i]!=null&&V11[i-1]!=null&&C[i]>V11[i]&&V11[i]>V11[i-1],bh=i>0&&HH15[i-1]!=null&&C[i]>HH15[i-1],ms=i>=3&&MA20[i]!=null&&MA20[i-3]!=null?(MA20[i]-MA20[i-3])/MA20[i-3]*100:null,mature=ms!=null&&ms>0,absb=bias20[i]!=null&&V15[i]!=null&&bias20[i]<-10&&V15[i]<20,sus=i>0&&!absb&&volMA5[i]!=null&&washVol[i]!=null&&washGain[i]!=null&&V[i]>volMA5[i]*washVol[i]&&((C[i]/C[i-1]-1)*100)<washGain[i]&&bias20[i]>-5&&mature,lock=i>0&&relVol[i]!=null&&hslMA5[i-1]!=null&&relVol[i]<hslMA5[i-1]*.65,locked=i>0&&volMA20[i]!=null&&V[i]<volMA20[i]*.78&&C[i]/C[i-1]>1.015&&bh&&lock&&healthy,ve=volMA5[i]!=null&&V[i]>volMA5[i]*1.15&&healthy&&!sus;
      cL[i]=!!(pu&&(ve||locked)&&V4[i]);
      const violent=i>0&&volMA5[i]!=null&&hslMA5[i]!=null&&V[i]>volMA5[i]*1.2&&C[i]/C[i-1]<.98&&relVol[i]>hslMA5[i]*1.5;
      bear[i]=i>0&&volMA20[i]!=null&&V[i]<volMA20[i]*.75&&C[i]<C[i-1]&&V11[i]!=null&&V11[i-1]!=null&&C[i]<V11[i]&&V11[i]<V11[i-1];
      const nl=i>0&&LL12[i-1]!=null&&C[i]<LL12[i-1],fb=bear[i]&&!(i>0&&bear[i-1])&&nl;
      cS[i]=violent||fb||sus; clL[i]=!!(pu&&!ve&&!locked&&V4[i]&&healthy);
      const sw=i>0&&volMA5[i]!=null&&hslMA5[i]!=null&&V[i]>volMA5[i]*1.1&&C[i]<C[i-1]&&V11[i]!=null&&C[i]<V11[i]&&relVol[i]>hslMA5[i],bw=bear[i]&&!nl;
      clS[i]=!!((sw||bw)&&V4[i]);
    }

    function st(LG,Ll,SG,Sl,i){if(LG[i])return"LONG";if(Ll[i])return"LIGHT_LONG";if(SG[i])return"SHORT";if(Sl[i])return"LIGHT_SHORT";return"GRAY";}
    const trend=blank(),mom=blank(),acc=blank(),cap=blank();
    for(let i=0;i<N;i++){trend[i]=st(tL,tlL,tS,tlS,i);mom[i]=st(mL,mlL,mS,mlS,i);acc[i]=st(aL,alL,aS,alS,i);cap[i]=st(cL,clL,cS,clS,i);}
    const rows=raw.map((r,i)=>({date:r.date,open:r.open,high:r.high,low:r.low,close:r.close,volume:r.volume,trend:trend[i],capital:cap[i],momentum:mom[i],accel:acc[i],prev_trend:i?trend[i-1]:"",prev_accel:i?acc[i-1]:"",d_trend_state:i?rank[trend[i]]-rank[trend[i-1]]:0,d_capital_state:i?rank[cap[i]]-rank[cap[i-1]]:0,d_momentum_state:i?rank[mom[i]]-rank[mom[i-1]]:0,d_accel_state:i?rank[acc[i]]-rank[acc[i-1]]:0}));

    return {raw,rows};
  }

  function entryV1(r){
    const all4=r.d_trend_state>0&&r.d_capital_state>0&&r.d_momentum_state>0&&r.d_accel_state>0;
    return rank[r.prev_trend]<=0&&rank[r.trend]>=1&&rank[r.momentum]>=1&&rank[r.accel]>=1&&!all4;
  }
  function exitV1(r){
    return (r.prev_accel==="LIGHT_SHORT"&&r.accel==="SHORT") ||
           (r.prev_accel==="SHORT"&&r.accel==="LIGHT_SHORT") ||
           (r.prev_trend==="LONG"&&r.trend==="LIGHT_LONG");
  }

  function resolveRange(rows,startDate,endDate){
    let s=rows.findIndex(r=>r.date>=startDate); if(s<0)s=0;
    let e=rows.length-1; for(let i=rows.length-1;i>=0;i--){if(rows[i].date<=endDate){e=i;break;}}
    return [s,e];
  }

  function simulate(model,{startDate="2020-01-01",endDate="2025-12-31",maxHold=15}={}){
    const {raw,rows}=model; const [s,e]=resolveRange(rows,startDate,endDate);
    let cash=1,shares=0,entryPrice=0,entryI=null,pending=null,trades=[],peak=1,mdd=0,exposureDays=0;
    for(let i=s;i<=e;i++){
      if(pending){
        const px=raw[i].open*(pending==="BUY"?1.0005:.9995);
        if(pending==="BUY"&&!shares){shares=cash/px;cash=0;entryPrice=px;entryI=i;}
        else if(pending==="SELL"&&shares){cash=shares*px;trades.push({entry:raw[entryI].date,exit:raw[i].date,ret:px/entryPrice-1,days:i-entryI});shares=0;entryPrice=0;entryI=null;}
        pending=null;
      }
      if(shares)exposureDays++;
      const equity=cash+shares*raw[i].close;peak=Math.max(peak,equity);mdd=Math.min(mdd,equity/peak-1);
      if(i===e)break;
      if(!shares){if(entryV1(rows[i]))pending="BUY";}
      else if(exitV1(rows[i]))pending="SELL";
      else if(i-entryI>=maxHold-1)pending="SELL";
    }
    if(shares){const px=raw[e].close*.9995;cash=shares*px;trades.push({entry:raw[entryI].date,exit:raw[e].date,ret:px/entryPrice-1,days:e-entryI});}
    return {ret:cash-1,mdd,trades,exposure:exposureDays/(e-s+1),startIndex:s,endIndex:e};
  }

  function oneTrade(model,signalI,{maxHold=15}={}){
    const {raw,rows}=model;if(signalI+1>=rows.length)return null;
    const ei=signalI+1,ep=raw[ei].open*1.0005;let xi=Math.min(rows.length-1,ei+maxHold);
    for(let j=ei;j<Math.min(rows.length-1,ei+maxHold);j++){if(exitV1(rows[j])){xi=j+1;break;}}
    const xp=(xi===rows.length-1?raw[xi].close:raw[xi].open)*.9995;
    return {ret:xp/ep-1,entryI:ei,exitI:xi,days:xi-ei};
  }

  globalThis.FIVEGZ5SE_V1={build,simulate,oneTrade,entryV1,exitV1,rank};
})();
