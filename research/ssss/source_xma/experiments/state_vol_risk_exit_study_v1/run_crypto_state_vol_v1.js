const fs=require("fs"),vm=require("vm"),path=require("path");
const root=path.resolve(__dirname,"../../../../../");
function load(p){vm.runInThisContext(fs.readFileSync(path.join(root,p),"utf8"),{filename:p});}
load("research/ssss/source_xma/experiments/fivegz5se_cross_symbol/fivegz5se_v1_engine.js");
let staged=fs.readFileSync(path.join(root,"research/ssss/source_xma/experiments/staged_entry_crypto_study/fivegz5se_staged_entry_experiment_v1.js"),"utf8");
staged=staged.replace("globalThis.FIVEGZ5SE_STAGED_ENTRY_V1={analyze};","globalThis.FIVEGZ5SE_STAGED_ENTRY_V1={analyze,build};");
vm.runInThisContext(staged);
load("research/ssss/source_xma/experiments/state_vol_risk_exit_study_v1/state_vol_risk_exit_compute_v1.js");
const R=globalThis.STATE_VOL_RISK_EXIT_V1, mean=R.mean, here=__dirname;
const specs=[["BTC","BTCUSDT"],["ETH","ETHUSDT"],["BNB","BNBUSDT"],["SOL","SOLUSDT"]];
function compact(symbol,M,name,r,diag){
 const e=r.risk_details||[],avg=k=>mean(e.map(x=>x[k])),frac=k=>e.length?e.filter(x=>x[k]).length/e.length:null;
 const o={symbol,config:name,start:M.raw[0].date,end:M.raw[M.raw.length-1].date,rows:M.raw.length,return:r.return,close_mdd:r.close_mdd,intra_mdd:r.intra_mdd,trades:r.trades,win:r.win,avg_trade:r.avg_trade,median_trade:r.median_trade,p10:r.p10,p5:r.p5,cvar10:r.cvar10,worst:r.worst,exposure:r.exposure,normal_full_exits:r.normal_full_exits,normal_half_exits:r.normal_half_exits,risk_exits:r.risk_exits,gap_exits:r.gap_exits,open_at_end:r.open_at_end,post_ret_3:avg("post_ret_3"),post_ret_5:avg("post_ret_5"),post_ret_10:avg("post_ret_10"),post_ret_20:avg("post_ret_20"),post_min_10:avg("post_min_10"),recovered_cost_10:frac("recovered_cost_10")};
 if(diag){Object.assign(o,{matched_stops:diag.matched_stops,killed_winners:diag.killed_winners,saved_losers:diag.saved_losers,mean_delta_vs_baseline:diag.mean_delta_vs_baseline,killed_winner_opportunity_cost:diag.killed_winner_opportunity_cost,saved_loser_improvement:diag.saved_loser_improvement,confirmed_matched_stops:diag.confirmed_matched_stops,confirmed_baseline_winners:diag.confirmed_baseline_winners,confirmed_mean_delta:diag.confirmed_mean_delta,preconfirm_matched_stops:diag.preconfirm_matched_stops,preconfirm_mean_delta:diag.preconfirm_mean_delta});
  for(const [label,a,b] of [["2017-2020",2017,2020],["2021-2023",2021,2023],["2024-2026",2024,2026]]){const z=diag.matched.filter(x=>{const y=+x.signal_date.slice(0,4);return y>=a&&y<=b});o["period_"+label+"_n"]=z.length;o["period_"+label+"_delta"]=mean(z.map(x=>x.delta_vs_baseline));o["period_"+label+"_killed"]=z.filter(x=>x.baseline_winner).length;}
 }
 return o;
}
const oldText=fs.readFileSync(path.join(root,"research/ssss/source_xma/experiments/crypto_risk_exit_study_v1/CRYPTO_RISK_CONFIG_SUMMARY_v1.csv"),"utf8").trim().split(/\r?\n/);
const hh=oldText[0].split(","), old={};
for(const line of oldText.slice(1)){const p=line.split(","),o={};hh.forEach((k,i)=>o[k]=p[i]);if(o.config==="BASELINE_SIGNAL_ONLY")old[o.symbol]=o;}
const results=[],audit=[];
for(const [symbol,file] of specs){
 const text=fs.readFileSync(path.join(here,"crypto_inputs",file+".csv"),"utf8"),M=R.setup(R.sourceCsv(text)),base=R.simulate(M,{config:"BASELINE",assetClass:"crypto"}),configs=[compact(symbol,M,"BASELINE",base,null)];
 const b=old[symbol]; if(!b)throw Error("missing old baseline "+symbol);
 const d={symbol,return:base.return-(+b.return),close_mdd:base.close_mdd-(+b.close_mdd),intra_mdd:base.intra_mdd-(+b.intra_mdd),trades:base.trades-(+b.trades),win:base.win-(+b.win),p5:base.p5-(+b.p5),cvar10:base.cvar10-(+b.cvar10),exposure:base.exposure-(+b.exposure)};
 audit.push(d);
 for(const name of R.configs.slice(1)){const x=R.simulate(M,{config:name,assetClass:"crypto"}),dg=R.matchDiagnostics(x,base);configs.push(compact(symbol,M,name,x,dg));}
 results.push({symbol,configs});
}
const tol=1e-9,bad=audit.filter(d=>Math.abs(d.return)>tol||Math.abs(d.close_mdd)>tol||Math.abs(d.intra_mdd)>tol||d.trades!==0||Math.abs(d.win)>tol||Math.abs(d.p5)>tol||Math.abs(d.cvar10)>tol||Math.abs(d.exposure)>tol);
fs.writeFileSync(path.join(here,"CRYPTO_BASELINE_REPRO_v1.json"),JSON.stringify({status:bad.length?"FAIL":"PASS",tolerance:tol,audit},null,2)+"\n");
if(bad.length){console.error(JSON.stringify({status:"BASELINE_REPRO_FAIL",bad},null,2));process.exit(3);}
fs.writeFileSync(path.join(here,"crypto_state_vol_results_v1.json"),JSON.stringify({study:"state_vol_risk_exit_v1",asset_class:"crypto",date:"2026-10-01",config_count:R.configs.length,results})+"\n");
console.log(JSON.stringify({status:"PASS",coins:results.length,configs:R.configs.length,audit}));
