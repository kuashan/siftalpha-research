// FIVEGZ5SE signal-sequence and staged-position research helper.
// Requires globalThis.FIVEGZ5SE_V1 to be loaded first.
// Research-only. Formula-native operation labels are not used.

(function(){
  const rank = globalThis.FIVEGZ5SE_V1.rank;
  const dims = ["trend","capital","momentum","accel","anomaly"];

  function parseRaw(text){
    const lines=text.trim().split(/\r?\n/), hdr=lines[0].split(",");
    return lines.slice(1).filter(Boolean).map(line=>{
      const p=line.split(","),o={};hdr.forEach((h,i)=>o[h]=p[i]);
      return {date:o.Date,open:+o.Open,high:+o.High,low:+o.Low,close:+o.Close,volume:+o.Volume};
    }).filter(r=>r.date&&Number.isFinite(r.close)).sort((a,b)=>a.date.localeCompare(b.date));
  }
  const mean=a=>{const x=a.filter(Number.isFinite);return x.length?x.reduce((s,v)=>s+v,0)/x.length:null};
  const median=a=>{const x=a.filter(Number.isFinite).sort((a,b)=>a-b);if(!x.length)return null;const m=Math.floor(x.length/2);return x.length%2?x[m]:(x[m-1]+x[m])/2};
  function slope(v){const n=v.length,mx=(n-1)/2,my=v.reduce((a,b)=>a+b,0)/n;let nu=0,de=0;for(let i=0;i<n;i++){nu+=(i-mx)*(v[i]-my);de+=(i-mx)**2;}return de?nu/de:0;}

  function buildStates(text){
    const model=globalThis.FIVEGZ5SE_V1.build(text), raw=model.raw, base=model.rows;
    const N=raw.length,C=raw.map(r=>r.close),O=raw.map(r=>r.open),H=raw.map(r=>r.high),L=raw.map(r=>r.low),V=raw.map(r=>r.volume);
    const blank=()=>Array(N).fill(null);
    function ma(a,n){const o=blank(),q=[];let s=0;for(let i=0;i<N;i++){q.push(a[i]);s+=a[i]??0;if(q.length>n)s-=q.shift()??0;if(q.length===n&&q.every(Number.isFinite))o[i]=s/n;}return o}
    function ema(a,n){const o=blank(),k=2/(n+1);let p=null;for(let i=0;i<N;i++){const x=a[i];if(!Number.isFinite(x))continue;p=p==null?x:k*x+(1-k)*p;o[i]=p;}return o}
    function sma(a,n,m){const o=blank();let p=null;for(let i=0;i<N;i++){const x=a[i];if(!Number.isFinite(x))continue;p=p==null?x:(m*x+(n-m)*p)/n;o[i]=p;}return o}
    function roll(a,n,fn){const o=blank();for(let i=n-1;i<N;i++){const w=a.slice(i-n+1,i+1);if(w.every(Number.isFinite))o[i]=fn(w);}return o}
    const llv=(a,n)=>roll(a,n,w=>Math.min(...w)),hhv=(a,n)=>roll(a,n,w=>Math.max(...w));
    const MA20=ma(C,20),MA60=ma(C,60),VOLMA5=ma(V,5),LL13=llv(L,13),HH13=hhv(H,13);
    const VAR5=C.map((x,i)=>LL13[i]!=null&&HH13[i]!==LL13[i]?(x-LL13[i])/(HH13[i]-LL13[i])*100:null),VAR6=sma(VAR5,4,1),VAR7=sma(VAR6,3,1),E5=ema(C,5),VAR3=C.map((x,i)=>E5[i]!=null?(x-E5[i])*100/x:null);
    const anomaly=Array(N).fill("GRAY");
    for(let i=1;i<N;i++){
      const body=Math.abs(C[i]-O[i]),lower=Math.min(C[i],O[i])-L[i],upper=H[i]-Math.max(C[i],O[i]);
      const coreBuy=(C[i-1]<O[i-1]&&C[i]>O[i]&&O[i]<C[i-1]&&C[i]>O[i-1])||(lower>body*2&&upper<body*.5&&C[i]>C[i-1])||(C[i]>H[i-1]&&C[i]/O[i]>1.02);
      const helpBuy=(MA20[i]!=null&&MA60[i]!=null&&MA20[i]>MA60[i])||(VOLMA5[i]!=null&&(V[i]>VOLMA5[i]*1.15||V[i]<VOLMA5[i]*.65))||(VAR7[i]!=null&&VAR7[i]<=35);
      const anLong=coreBuy&&helpBuy&&Number.isFinite(VAR3[i])&&rank[base[i].trend]>0;
      const anLightLong=coreBuy&&helpBuy&&Number.isFinite(VAR3[i])&&!(rank[base[i].trend]>0);
      const coreSell=(C[i-1]>O[i-1]&&C[i]<O[i]&&O[i]>C[i-1]&&C[i]<O[i-1])||(upper>body*2&&lower<body*.5&&C[i]<C[i-1])||(O[i]>H[i-1]&&C[i]<O[i-1]&&C[i]<(O[i-1]+C[i-1])/2);
      const helpSell=(MA20[i]!=null&&MA60[i]!=null&&MA20[i]<MA60[i])||(VOLMA5[i]!=null&&(V[i]>VOLMA5[i]*1.15||V[i]<VOLMA5[i]*.65))||(VAR7[i]!=null&&VAR7[i]>=50);
      const anShort=coreSell&&helpSell&&Number.isFinite(VAR3[i]);
      const anLightShort=coreSell&&helpSell&&Number.isFinite(VAR3[i])&&!(rank[base[i].trend]<0);
      anomaly[i]=anLong?"LONG":anLightLong?"LIGHT_LONG":anShort?"SHORT":anLightShort?"LIGHT_SHORT":"GRAY";
    }
    const rows=base.map((r,i)=>({...r,anomaly:anomaly[i]}));
    const F=Array(N);
    for(let i=5;i<N;i++){
      const o={};
      for(const d of dims){
        o[d+"_cur"]=rank[rows[i][d]];
        for(const w of [1,3,5]){
          const v=[];for(let k=i-w;k<=i;k++)v.push(rank[rows[k][d]]);
          o[d+"_net"+w]=v.at(-1)-v[0];o[d+"_slope"+w]=slope(v);
          o[d+"_pos"+w]=v.slice(1).filter(x=>x>0).length;o[d+"_neg"+w]=v.slice(1).filter(x=>x<0).length;
        }
      }
      let bull3=0;
      for(let k=i-2;k<=i;k++){let b=0;for(const d of dims)if(rank[rows[k][d]]>0)b++;if(b>=3)bull3++;}
      o.bullbars3=bull3;F[i]=o;
    }
    return {raw,rows,F};
  }

  function analyze(text,symbol,{endDate="2025-12-31"}={}){
    const {raw,rows,F}=buildStates(text),N=raw.length;
    const BUY={
      A:i=>!!F[i]&&F[i].trend_slope3>0&&F[i].momentum_cur===-2&&F[i].momentum_slope5<0,
      B:i=>!!F[i]&&F[i].capital_cur===0&&F[i].capital_net1<0&&F[i].accel_slope3>0,
      C:i=>!!F[i]&&F[i].trend_cur===0&&F[i].capital_net3>0&&F[i].capital_pos3>=2&&F[i].capital_slope5>0&&F[i].anomaly_cur===0
    };
    const SELL={
      A:i=>!!F[i]&&F[i].trend_cur===0&&F[i].accel_pos5>=3&&F[i].bullbars3>=2,
      B:i=>!!F[i]&&F[i].capital_slope5<0&&F[i].momentum_cur>=1&&F[i].anomaly_net1<0,
      C:i=>!!F[i]&&F[i].momentum_cur===2&&F[i].anomaly_net3>0&&F[i].bullbars3>=2
    };
    const onset=(fn,i)=>i>0&&fn(i)&&!fn(i-1);
    const active=(group,i)=>Object.keys(group).filter(k=>onset(group[k],i));
    let end=N-1;for(let i=N-1;i>=0;i--)if(rows[i].date<=endDate){end=i;break;}
    const start=Math.max(63,rows.findIndex(r=>r.date>="2020-01-02"));
    function fwd(i,h){
      if(i+1>=N||i+h>=N)return null;
      const ep=raw[i+1].open;let hi=-Infinity,lo=Infinity;
      for(let k=i+1;k<=i+h;k++){hi=Math.max(hi,raw[k].high);lo=Math.min(lo,raw[k].low);}
      return {ret:raw[i+h].close/ep-1,mfe:hi/ep-1,mae:lo/ep-1};
    }

    // Baseline positions: full entry on first BUY, full exit on first SELL.
    const positions=[], buyEvents=[], sellEvents=[];
    let inPos=false,entrySignal=-1,entryExec=-1,seen=new Set(),seq=[],repeats=0,pendingEntry=null;
    for(let i=start;i<=end;i++){
      if(pendingEntry!=null){inPos=true;entryExec=i;pendingEntry=null;}
      const bs=active(BUY,i),ss=active(SELL,i);
      if(!inPos){
        if(bs.length&&ss.length===0&&i<end){
          entrySignal=i;seen=new Set(bs);seq=[bs.join("+")+"@ENTRY"];repeats=0;pendingEntry=i+1;
        }
      } else {
        // record subsequent buy onsets while holding
        for(const fam of bs){
          const isNew=!seen.has(fam), kind=isNew?"CROSS":"SAME_REPEAT";
          const ff5=fwd(i,5),ff10=fwd(i,10),ff20=fwd(i,20);
          buyEvents.push({symbol,date:rows[i].date,family:fam,kind,entry_date:rows[entryExec].date,distinct_before:seen.size,ret5:ff5?.ret??null,ret10:ff10?.ret??null,ret20:ff20?.ret??null,mfe10:ff10?.mfe??null,mae10:ff10?.mae??null});
          if(isNew){seen.add(fam);seq.push(fam); } else repeats++;
        }
        if(ss.length&&i<end){
          const exitExec=i+1,ep=raw[entryExec].open*1.0005,xp=raw[exitExec].open*.9995;
          positions.push({symbol,entry_signal:rows[entrySignal].date,entry_date:rows[entryExec].date,entry_families:seq[0].replace("@ENTRY",""),sequence:seq.join("->"),distinct_buy_families:seen.size,same_repeat_count:repeats,exit_signal:rows[i].date,exit_date:rows[exitExec].date,exit_families:ss.join("+"),ret:xp/ep-1,days:exitExec-entryExec});
          // first-sell event study
          const firstSet=new Set(ss),firstExitOpen=raw[exitExec].open;
          let secondAny=null,secondDistinct=null,sameRepeat5=false;
          for(let j=i+1;j<=Math.min(end,i+20);j++){
            const sx=active(SELL,j);
            if(sx.length&&!secondAny)secondAny={i:j,fams:sx};
            if(j<=i+5&&sx.some(f=>firstSet.has(f)))sameRepeat5=true;
            const nf=sx.filter(f=>!firstSet.has(f));
            if(nf.length&&!secondDistinct)secondDistinct={i:j,fams:nf};
          }
          const ff3=fwd(i,3),ff5=fwd(i,5),ff10=fwd(i,10);
          sellEvents.push({
            symbol,date:rows[i].date,first_families:ss.join("+"),same_day_count:ss.length,
            cross_distinct_within3:!!(secondDistinct&&secondDistinct.i<=i+3),
            cross_distinct_within5:!!(secondDistinct&&secondDistinct.i<=i+5),
            same_repeat_within5:sameRepeat5,
            ret3:ff3?.ret??null,ret5:ff5?.ret??null,ret10:ff10?.ret??null,
            delay_to_second_any:secondAny&&secondAny.i+1<N?raw[secondAny.i+1].open/firstExitOpen-1:null,
            delay_to_second_distinct:secondDistinct&&secondDistinct.i+1<N?raw[secondDistinct.i+1].open/firstExitOpen-1:null,
            second_any_days:secondAny?secondAny.i-i:null,second_distinct_days:secondDistinct?secondDistinct.i-i:null
          });
          inPos=false;entrySignal=-1;entryExec=-1;seen=new Set();seq=[];repeats=0;
        }
      }
    }

    // Position-sizing / exit-policy simulator.
    function simulate({buyPolicy="FULL_FIRST",sellPolicy="FULL_FIRST"}={}){
      let cash=10000,shares=0,baseCap=0,seenBuy=new Set(),firstSellSet=null,pending=[],peak=10000,mdd=0,exposure=0,trades=0,wins=0,realizedRets=[],entryBasis=0,entryValue=0;
      function schedule(type,fraction,reason){pending.push({type,fraction,reason});}
      function allocForNew(nDistinct){
        if(buyPolicy==="FULL_FIRST")return nDistinct===1?1:0;
        if(buyPolicy==="HALF_CROSS")return nDistinct<=2?.5:0;
        if(buyPolicy==="THIRDS_DISTINCT")return nDistinct<=3?1/3:0;
        if(buyPolicy==="HALF_QUARTERS")return nDistinct===1?.5:(nDistinct<=3?.25:0);
        return 0;
      }
      for(let i=start;i<=end;i++){
        if(pending.length){
          for(const p of pending){
            if(p.type==="BUY"&&p.fraction>0&&cash>0){
              const budget=Math.min(cash,baseCap*p.fraction),px=raw[i].open*1.0005,qty=budget/px;
              entryBasis+=budget;entryValue+=qty*px;shares+=qty;cash-=budget;
            } else if(p.type==="SELL"&&p.fraction>0&&shares>0){
              const qty=Math.min(shares,p.fraction>=.999999?shares:shares*p.fraction),px=raw[i].open*.9995;
              cash+=qty*px;shares-=qty;
              if(shares<1e-12)shares=0;
            }
          }
          pending=[];
          if(shares===0&&entryBasis>0){
            const equity=cash,tradeRet=(equity-baseCap)/baseCap;realizedRets.push(tradeRet);if(tradeRet>0)wins++;trades++;entryBasis=0;entryValue=0;baseCap=0;seenBuy=new Set();firstSellSet=null;
          }
        }
        if(shares>0)exposure++;
        const eq=cash+shares*raw[i].close;peak=Math.max(peak,eq);mdd=Math.min(mdd,eq/peak-1);
        if(i===end)break;
        const bs=active(BUY,i),ss=active(SELL,i);
        if(shares===0&&baseCap===0){
          if(bs.length&&ss.length===0){
            baseCap=eq;seenBuy=new Set(bs);
            let frac=0;
            if(buyPolicy==="FULL_FIRST")frac=1;
            else if(buyPolicy==="HALF_CROSS")frac=Math.min(1,.5*seenBuy.size);
            else if(buyPolicy==="THIRDS_DISTINCT")frac=Math.min(1,(1/3)*seenBuy.size);
            else if(buyPolicy==="HALF_QUARTERS")frac=Math.min(1,.5+.25*Math.max(0,seenBuy.size-1));
            schedule("BUY",frac,"ENTRY");
          }
        } else if(shares>0){
          const newF=bs.filter(f=>!seenBuy.has(f));
          for(const f of newF){
            seenBuy.add(f);
            const frac=allocForNew(seenBuy.size);
            if(frac>0)schedule("BUY",frac,"CONFIRM_"+f);
          }
          if(ss.length){
            if(sellPolicy==="FULL_FIRST"){schedule("SELL",1,"FIRST");}
            else if(sellPolicy==="HALF_ANY"){
              if(firstSellSet==null){firstSellSet=new Set(ss);schedule("SELL",.5,"FIRST_HALF");}
              else schedule("SELL",1,"NEXT_ANY");
            } else if(sellPolicy==="HALF_DISTINCT"){
              if(firstSellSet==null){firstSellSet=new Set(ss);schedule("SELL",.5,"FIRST_HALF");}
              else if(ss.some(f=>!firstSellSet.has(f)))schedule("SELL",1,"NEXT_DISTINCT");
            } else if(sellPolicy==="WAIT_DISTINCT"){
              if(firstSellSet==null)firstSellSet=new Set(ss);
              else if(ss.some(f=>!firstSellSet.has(f)))schedule("SELL",1,"SECOND_DISTINCT");
            }
          }
        }
      }
      const final=cash+shares*raw[end].close;
      const avg=mean(realizedRets),med=median(realizedRets);
      return {return:final/10000-1,mdd,trades,win:trades?wins/trades:null,avg_trade:avg,median_trade:med,exposure:exposure/(end-start+1),open_at_end:shares>0};
    }

    const strategies={
      BUY_FULL_SELL_FULL:simulate({buyPolicy:"FULL_FIRST",sellPolicy:"FULL_FIRST"}),
      BUY_HALF_CROSS_SELL_FULL:simulate({buyPolicy:"HALF_CROSS",sellPolicy:"FULL_FIRST"}),
      BUY_THIRDS_DISTINCT_SELL_FULL:simulate({buyPolicy:"THIRDS_DISTINCT",sellPolicy:"FULL_FIRST"}),
      BUY_HALF_QUARTERS_SELL_FULL:simulate({buyPolicy:"HALF_QUARTERS",sellPolicy:"FULL_FIRST"}),
      BUY_FULL_SELL_HALF_ANY:simulate({buyPolicy:"FULL_FIRST",sellPolicy:"HALF_ANY"}),
      BUY_FULL_SELL_HALF_DISTINCT:simulate({buyPolicy:"FULL_FIRST",sellPolicy:"HALF_DISTINCT"}),
      BUY_FULL_SELL_WAIT_DISTINCT:simulate({buyPolicy:"FULL_FIRST",sellPolicy:"WAIT_DISTINCT"})
    };

    const posSummary={};
    for(const k of [1,2,3]){
      const a=positions.filter(x=>x.distinct_buy_families===k);posSummary["distinct_"+k]={n:a.length,mean_trade:mean(a.map(x=>x.ret)),win:a.length?a.filter(x=>x.ret>0).length/a.length:null};
    }
    return {symbol,start:rows[start]?.date,end:rows[end]?.date,sessions:end-start+1,positions,buyEvents,sellEvents,strategies,posSummary};
  }

  globalThis.FIVEGZ5SE_SEQUENCE_V1={analyze};
})();