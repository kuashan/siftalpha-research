// FIVEGZ5SE staged-entry experiment v1.
// Initial entry is BUY-A or BUY-B only.
// Initial allocation: 50%, 60%, or 70%.
// Top up to 100% only if BUY-C onsets AFTER entry signal within W3/W5.
// Same-family repeats and A<->B transitions do not add.
// Primary exit: full exit on first SELL-A/B/C.
// Secondary control: single A/B sells half; C or same-day multi-sell exits full;
// remaining half exits on next different SELL family. No time cap.

(function(){
  const rank=globalThis.FIVEGZ5SE_V1.rank, dims=["trend","capital","momentum","accel","anomaly"];
  const mean=a=>{const x=a.filter(Number.isFinite);return x.length?x.reduce((s,v)=>s+v,0)/x.length:null};
  const median=a=>{const x=a.filter(Number.isFinite).sort((a,b)=>a-b);if(!x.length)return null;const m=Math.floor(x.length/2);return x.length%2?x[m]:(x[m-1]+x[m])/2};
  const quantile=(a,q)=>{const x=a.filter(Number.isFinite).sort((a,b)=>a-b);if(!x.length)return null;const p=(x.length-1)*q,l=Math.floor(p),h=Math.ceil(p);return x[l]+(x[h]-x[l])*(p-l)};
  function slope(v){const n=v.length,mx=(n-1)/2,my=v.reduce((a,b)=>a+b,0)/n;let nu=0,de=0;for(let i=0;i<n;i++){nu+=(i-mx)*(v[i]-my);de+=(i-mx)**2;}return de?nu/de:0;}
  function build(text){
    const model=globalThis.FIVEGZ5SE_V1.build(text),raw=model.raw,base=model.rows,N=raw.length,C=raw.map(r=>r.close),O=raw.map(r=>r.open),H=raw.map(r=>r.high),L=raw.map(r=>r.low),V=raw.map(r=>r.volume),blank=()=>Array(N).fill(null);
    function ma(a,n){const o=blank(),q=[];let s=0;for(let i=0;i<N;i++){q.push(a[i]);s+=a[i]??0;if(q.length>n)s-=q.shift()??0;if(q.length===n&&q.every(Number.isFinite))o[i]=s/n;}return o}
    function ema(a,n){const o=blank(),k=2/(n+1);let p=null;for(let i=0;i<N;i++){const x=a[i];if(!Number.isFinite(x))continue;p=p==null?x:k*x+(1-k)*p;o[i]=p;}return o}
    function sma(a,n,m){const o=blank();let p=null;for(let i=0;i<N;i++){const x=a[i];if(!Number.isFinite(x))continue;p=p==null?x:(m*x+(n-m)*p)/n;o[i]=p;}return o}
    function roll(a,n,fn){const o=blank();for(let i=n-1;i<N;i++){const w=a.slice(i-n+1,i+1);if(w.every(Number.isFinite))o[i]=fn(w);}return o}
    const llv=(a,n)=>roll(a,n,w=>Math.min(...w)),hhv=(a,n)=>roll(a,n,w=>Math.max(...w)),MA20=ma(C,20),MA60=ma(C,60),VOLMA5=ma(V,5),LL13=llv(L,13),HH13=hhv(H,13),VAR5=C.map((x,i)=>LL13[i]!=null&&HH13[i]!==LL13[i]?(x-LL13[i])/(HH13[i]-LL13[i])*100:null),VAR6=sma(VAR5,4,1),VAR7=sma(VAR6,3,1),E5=ema(C,5),VAR3=C.map((x,i)=>E5[i]!=null?(x-E5[i])*100/x:null);
    const anomaly=Array(N).fill("GRAY");
    for(let i=1;i<N;i++){
      const body=Math.abs(C[i]-O[i]),lo=Math.min(C[i],O[i])-L[i],up=H[i]-Math.max(C[i],O[i]);
      const cb=(C[i-1]<O[i-1]&&C[i]>O[i]&&O[i]<C[i-1]&&C[i]>O[i-1])||(lo>body*2&&up<body*.5&&C[i]>C[i-1])||(C[i]>H[i-1]&&C[i]/O[i]>1.02);
      const hb=(MA20[i]!=null&&MA60[i]!=null&&MA20[i]>MA60[i])||(VOLMA5[i]!=null&&(V[i]>VOLMA5[i]*1.15||V[i]<VOLMA5[i]*.65))||(VAR7[i]!=null&&VAR7[i]<=35);
      const al=cb&&hb&&Number.isFinite(VAR3[i])&&rank[base[i].trend]>0,all=cb&&hb&&Number.isFinite(VAR3[i])&&!(rank[base[i].trend]>0);
      const cs=(C[i-1]>O[i-1]&&C[i]<O[i]&&O[i]>C[i-1]&&C[i]<O[i-1])||(up>body*2&&lo<body*.5&&C[i]<C[i-1])||(O[i]>H[i-1]&&C[i]<O[i-1]&&C[i]<(O[i-1]+C[i-1])/2);
      const hs=(MA20[i]!=null&&MA60[i]!=null&&MA20[i]<MA60[i])||(VOLMA5[i]!=null&&(V[i]>VOLMA5[i]*1.15||V[i]<VOLMA5[i]*.65))||(VAR7[i]!=null&&VAR7[i]>=50);
      const as=cs&&hs&&Number.isFinite(VAR3[i]),als=cs&&hs&&Number.isFinite(VAR3[i])&&!(rank[base[i].trend]<0);
      anomaly[i]=al?"LONG":all?"LIGHT_LONG":as?"SHORT":als?"LIGHT_SHORT":"GRAY";
    }
    const rows=base.map((r,i)=>({...r,anomaly:anomaly[i]})),F=Array(N);
    for(let i=5;i<N;i++){const o={};for(const d of dims){o[d+"_cur"]=rank[rows[i][d]];for(const w of [1,3,5]){const v=[];for(let k=i-w;k<=i;k++)v.push(rank[rows[k][d]]);o[d+"_net"+w]=v.at(-1)-v[0];o[d+"_slope"+w]=slope(v);o[d+"_pos"+w]=v.slice(1).filter(x=>x>0).length;}}let b3=0;for(let k=i-2;k<=i;k++){let b=0;for(const d of dims)if(rank[rows[k][d]]>0)b++;if(b>=3)b3++;}o.bullbars3=b3;F[i]=o;}
    return {raw,rows,F};
  }
  function analyze(text,symbol,assetClass,{endDate="2025-12-31"}={}){
    const {raw,rows,F}=build(text),N=raw.length;
    const BUY={
      A:i=>!!F[i]&&F[i].trend_slope3>0&&F[i].momentum_cur===-2&&F[i].momentum_slope5<0,
      B:i=>!!F[i]&&F[i].capital_cur===0&&F[i].capital_net1<0&&F[i].accel_slope3>0,
      C:i=>!!F[i]&&F[i].trend_cur===0&&F[i].capital_net3>0&&F[i].capital_pos3>=2&&F[i].capital_slope5>0&&F[i].anomaly_cur===0
    },SELL={
      A:i=>!!F[i]&&F[i].trend_cur===0&&F[i].accel_pos5>=3&&F[i].bullbars3>=2,
      B:i=>!!F[i]&&F[i].capital_slope5<0&&F[i].momentum_cur>=1&&F[i].anomaly_net1<0,
      C:i=>!!F[i]&&F[i].momentum_cur===2&&F[i].anomaly_net3>0&&F[i].bullbars3>=2
    };
    const onset=(fn,i)=>i>0&&fn(i)&&!fn(i-1),active=(g,i)=>Object.keys(g).filter(k=>onset(g[k],i));
    let end=N-1;for(let i=N-1;i>=0;i--)if(rows[i].date<=endDate){end=i;break;}
    let ds=rows.findIndex(r=>r.date>="2020-04-02");if(ds<0)ds=0;const start=Math.max(63,ds);

    function sim(initialFrac,confirmWindow,exitPolicy){
      let cash=10000,shares=0,pending=[],entrySignalI=null,entryExecI=null,entryFam=null,confirmed=false,firstSellSet=null,peak=10000,mdd=0,expDays=0;
      const trades=[];let currentCost=0,currentStartEquity=0,currentEntryPx=0,confirmationCount=0;
      const equity=[];
      function sched(type,amount,reason){pending.push({type,amount,reason});}
      for(let i=start;i<=end;i++){
        if(pending.length){
          for(const p of pending){
            if(p.type==="BUY_CASH"&&p.amount>0&&cash>0){
              const amt=Math.min(cash,p.amount),px=raw[i].open*1.0005,qty=amt/px;shares+=qty;cash-=amt;currentCost+=amt;if(entryExecI==null){entryExecI=i;currentEntryPx=px;}
            } else if(p.type==="SELL_FRAC"&&shares>0){
              const qty=p.amount>=.999999?shares:shares*p.amount,px=raw[i].open*.9995;cash+=qty*px;shares-=qty;if(shares<1e-12)shares=0;
            }
          }
          pending=[];
          if(shares===0&&entryExecI!=null){
            const ret=cash/currentStartEquity-1;
            trades.push({entry_signal:rows[entrySignalI].date,entry_date:rows[entryExecI].date,entry_family:entryFam,confirmed,exit_date:rows[i].date,ret,days:i-entryExecI});
            entrySignalI=null;entryExecI=null;entryFam=null;confirmed=false;firstSellSet=null;currentCost=0;currentStartEquity=0;currentEntryPx=0;
          }
        }
        if(shares>0)expDays++;
        const eq=cash+shares*raw[i].close;peak=Math.max(peak,eq);mdd=Math.min(mdd,eq/peak-1);equity.push(eq);
        if(i===end)break;
        const bs=active(BUY,i),ss=active(SELL,i);
        if(shares===0&&entrySignalI==null){
          const init=bs.filter(x=>x==="A"||x==="B");
          if(init.length&&ss.length===0){
            currentStartEquity=eq;entrySignalI=i;entryFam=init[0];
            sched("BUY_CASH",eq*initialFrac,"INITIAL_"+entryFam);
          }
        } else if(shares>0){
          if(!confirmed && entrySignalI!=null && i>entrySignalI && i-entrySignalI<=confirmWindow && onset(BUY.C,i)){
            const target=currentStartEquity,curEq=cash+shares*raw[i].close;
            // Top-up with the remaining original allocation fraction, capped by cash.
            const amt=Math.min(cash,currentStartEquity*(1-initialFrac));
            if(amt>0){sched("BUY_CASH",amt,"C_CONFIRM");confirmed=true;confirmationCount++;}
          }
          if(ss.length){
            if(exitPolicy==="FULL_FIRST"){sched("SELL_FRAC",1,"FIRST_SELL");}
            else if(exitPolicy==="SELECTIVE"){
              if(firstSellSet==null){
                firstSellSet=new Set(ss);
                if(ss.includes("C")||ss.length>=2)sched("SELL_FRAC",1,"C_OR_MULTI");
                else sched("SELL_FRAC",.5,"AB_HALF");
              } else if(ss.some(f=>!firstSellSet.has(f)))sched("SELL_FRAC",1,"NEXT_DISTINCT");
            }
          }
        }
      }
      const final=cash+shares*raw[end].close, rets=trades.map(t=>t.ret),losses=rets.filter(x=>x<0);
      return {
        final,return:final/10000-1,mdd,trades:trades.length,win:rets.length?rets.filter(x=>x>0).length/rets.length:null,
        avg_trade:mean(rets),median_trade:median(rets),p10_trade:quantile(rets,.10),p5_trade:quantile(rets,.05),worst_trade:rets.length?Math.min(...rets):null,
        cvar10:rets.length?mean([...rets].sort((a,b)=>a-b).slice(0,Math.max(1,Math.ceil(rets.length*.1)))):null,
        exposure:expDays/(end-start+1),open_at_end:shares>0,confirmations:confirmationCount,trade_details:trades
      };
    }
    const cfgs=[];
    for(const w of [3,5]){
      cfgs.push({name:"BASE_100_FULL_FIRST_W"+w,initial:1,w,exit:"FULL_FIRST",r:sim(1,w,"FULL_FIRST")});
      for(const f of [.5,.6,.7])cfgs.push({name:"INIT_"+Math.round(f*100)+"_C_W"+w+"_FULL_FIRST",initial:f,w,exit:"FULL_FIRST",r:sim(f,w,"FULL_FIRST")});
      cfgs.push({name:"BASE_100_SELECTIVE_W"+w,initial:1,w,exit:"SELECTIVE",r:sim(1,w,"SELECTIVE")});
      for(const f of [.5,.6,.7])cfgs.push({name:"INIT_"+Math.round(f*100)+"_C_W"+w+"_SELECTIVE",initial:f,w,exit:"SELECTIVE",r:sim(f,w,"SELECTIVE")});
    }
    return {symbol,assetClass,start:rows[start]?.date,end:rows[end]?.date,sessions:end-start+1,configs:cfgs};
  }
  globalThis.FIVEGZ5SE_STAGED_ENTRY_V1={analyze};
})();