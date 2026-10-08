"use strict";
// Offline conversion of user-copied TradingView Pine Logs into a real per-bar
// numerical / confirmed-event comparison against the R2 indicator reconstruction.
// No web calls, no broker orders, no TradingView subscription required.
const fs=require("node:fs");
const path=require("node:path");
const {compareTV}=require("./compare_tv_export.js");

const FIELDS=["PARITY_PAI_RAW","PARITY_WT_RAW","PARITY_WT_SIGNAL_RAW","PARITY_WT_HIST_RAW",
"PARITY_WT_PIVOT_LOW_CONFIRMED","PARITY_WT_PIVOT_HIGH_CONFIRMED","PARITY_WT_BULL_CONFIRMED",
"PARITY_WT_BEAR_CONFIRMED","PARITY_PAI_PIVOT_LOW_CONFIRMED","PARITY_PAI_PIVOT_HIGH_CONFIRMED",
"PARITY_PAI_BULL_CONFIRMED","PARITY_PAI_BEAR_CONFIRMED","PARITY_PAI_UP5_CONFIRMED",
"PARITY_PAI_DOWN_MINUS5_CONFIRMED"];

function parsePineLogs(contents){
 const extracted=[];let ignored=0;
 for(const line of contents.replace(/^\uFEFF/,"").split(/\r?\n/)){
   if(!line.includes("TVR3|")){if(line.trim())ignored++;continue;}
   const parts=line.slice(line.indexOf("TVR3|")+5).trim().split("|");
   if(parts.length!==19)throw Error("LOG_FORMAT: 19 fields expected, got "+parts.length+" in "+line.slice(0,170));
   const ts=parts[0];
   if(!/^\d{4}-\d\d-\d\d \d\d:\d\d$/.test(ts))throw Error("INVALID_UTC: "+ts);
   const vals=parts.slice(1).map(Number);
   if(vals.some(x=>!Number.isFinite(x)))throw Error("NONFINITE_LOG_VALUE at "+ts);
   const [o,h,l,c]=vals;
   if(o<=0||h<=0||l<=0||c<=0||h<Math.max(o,c,l)||l>Math.min(o,c,h))
      throw Error("INVALID_OHLC at "+ts);
   for(const [i,name] of FIELDS.entries()){if(i<4)continue;
     const flag=vals[i+4];if(flag!==0&&flag!==1)throw Error("NONBOOLEAN_FLAG "+name+" at "+ts);}
   extracted.push({timestamp:ts,values:vals});
 }
 if(!extracted.length)throw Error("NO_TVR3_RECORDS: Did you paste Pine Logs rather than Pine source?");
 extracted.sort((a,b)=>a.timestamp.localeCompare(b.timestamp));
 const seen=new Set();for(const x of extracted){if(seen.has(x.timestamp))throw Error("DUPLICATE_CANDLE "+x.timestamp);seen.add(x.timestamp);}
 return{records:extracted,ignoredLines:ignored};
}
function toTVcsv(records){
 const header=["time","open","high","low","close",...FIELDS].join(",");
 const rows=records.map(x=>[x.timestamp,...x.values].join(","));
 return header+"\n"+rows.join("\n")+"\n";
}
function runPineLogParity(contents,options={}){
 const parsed=parsePineLogs(contents);
 const count=parsed.records.length;
 const warmup=options.warmup??250;
 const required=Math.max(350,warmup+100);
 const r={input:"TradingView Pine Logs (TVR3), user-pasted OHLC + 14 Pine indicator fields",rows:count,ignored_lines:parsed.ignoredLines,warmup,first:parsed.records[0].timestamp,last:parsed.records.at(-1).timestamp,
  eligible_rows:Math.max(0,count-warmup),status:"PENDING",reason:null,compare:null};
 if(count<required){r.status="INSUFFICIENT_HISTORY_FOR_NUMERIC_PARITY";
   r.reason="Need at least "+required+" consecutive TVR3 candles in one paste, because "+warmup+" initial OHLC bars are used for deterministic warmup and at least 100 bars must remain for comparison.";
   return r;}
 r.compare=compareTV(toTVcsv(parsed.records),{warmup,absTol:options.absTol??.0001});
 r.status=r.compare.status;
 r.notes=["The calculation uses the exact OHLC copied from TradingView (not Twelve Data).",
 "Comparisons are only valid with Pine script DEFAULT inputs, no HTF, no Laguerre.",
 "A successful numeric comparison is not a futures execution/funding parity test."];
 return r;
}
if(require.main===module){
 const file=process.argv[2],opts={};
 if(!file){console.error("Usage: node compare_tv_logs.js <user_pine_logs.txt> [--warmup=250]");process.exit(2);}
 for(const a of process.argv.slice(3)){if(a.startsWith("--warmup="))opts.warmup=+a.slice(9);}
 try{
  const result=runPineLogParity(fs.readFileSync(file,"utf8"),opts);
  const out=path.join(path.dirname(file),path.basename(file).replace(/\.[^.]+$/,"")+"_PARITY_REPORT.json");
  fs.writeFileSync(out,JSON.stringify(result,null,2)+"\n");
  console.log(JSON.stringify({status:result.status,rows:result.rows,first:result.first,last:result.last,mismatches:result.compare?.total_mismatches??null,output:out,reason:result.reason}));
  if(result.status!=="CSV_VALUES_MATCH_JS_RECONSTRUCTION")process.exitCode=1;
 }catch(e){console.error("PINE_LOG_VALIDATION_ERROR:",e.message);process.exitCode=2;}
}
module.exports={parsePineLogs,toTVcsv,runPineLogParity,FIELDS};
