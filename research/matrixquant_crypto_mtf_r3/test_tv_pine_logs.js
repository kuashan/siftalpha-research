"use strict";
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {parsePineLogs,runPineLogParity,FIELDS}=require("./compare_tv_logs.js");
const {derive,pivotAll}=require("./compare_tv_export.js");

const supplied=fs.readFileSync(path.join(__dirname,"user_tv_logs/BTC_4H_20261001_20261002_TVR3_7LINES.log"),"utf8");
const first=runPineLogParity(supplied);
assert.equal(first.rows,7);
assert.equal(first.status,"INSUFFICIENT_HISTORY_FOR_NUMERIC_PARITY");
assert.equal(first.first,"2026-10-01 20:00");
assert.equal(first.last,"2026-10-02 20:00");
const rows=parsePineLogs(supplied).records;
assert.equal(rows[0].values[16],1,"first PAI cross above 5");
assert.equal(rows[6].values[17],1,"last PAI cross below -5");
assert.ok(Math.abs(rows[6].values[5]-rows[6].values[6]-rows[6].values[7])<1e-7);

let bars=Array.from({length:520},(_,i)=>{
 let v=33000+i*.22+40*Math.sin(i/6)+20*Math.cos(i/23),o=v-1.2*Math.cos(i/3),c=v+.95*Math.sin(i/3);
 return{t:new Date(Date.UTC(2026,0,1,i*4)).toISOString().slice(0,16).replace("T"," "),o,h:Math.max(o,c)+7,l:Math.min(o,c)-9,c,v:NaN};
});
const ind=derive(bars),wp=pivotAll(bars,ind.hist,5,1,5,60),pp=pivotAll(bars,ind.pai,2,2,2,10);
const flag=(a,i)=>a[i]?1:0;
const crossing=(x,i,t,up)=>i>0&&(up?x[i-1]<=t&&x[i]>t:x[i-1]>=t&&x[i]<t)?1:0;
const lines=bars.map((b,i)=>{
 const vals=[b.o,b.h,b.l,b.c,ind.pai[i],ind.wt[i],ind.signal[i],ind.hist[i],
 flag(wp.pl,i),flag(wp.ph,i),flag(wp.bull,i),flag(wp.bear,i),
 flag(pp.pl,i),flag(pp.ph,i),flag(pp.bull,i),flag(pp.bear,i),
 crossing(ind.pai,i,5,true),crossing(ind.pai,i,-5,false)];
 return "[test-run]: TVR3|"+b.t+"|"+vals.map(v=>Number.isFinite(v)?(Number.isInteger(v)?String(v):v.toFixed(8)):"NaN").join("|");
});
const run=runPineLogParity(lines.join("\n"),{warmup:250,absTol:.0001});
assert.equal(run.rows,520);
assert.equal(run.status,"CSV_VALUES_MATCH_JS_RECONSTRUCTION",JSON.stringify(run.compare?.first_mismatches?.slice(0,2)));
assert.equal(run.compare.total_mismatches,0);
assert.equal(Object.keys(run.compare.fields).length,FIELDS.length);
assert.equal(FIELDS.length,14);

const bad=lines.slice();
let p=bad[350].split("|");
p[5]=(Number(p[5])+0.08).toFixed(8);bad[350]=p.join("|");
let wrong=runPineLogParity(bad.join("\n"));
assert.equal(wrong.status,"MISMATCH_REQUIRES_AUDIT");
assert.equal(wrong.compare.fields.PARITY_PAI_RAW.mismatches,1);

assert.throws(()=>parsePineLogs("indicator(title='x')"),/NO_TVR3_RECORDS/);
assert.throws(()=>parsePineLogs(supplied+rows[0].timestamp+" TVR3|"+rows[0].timestamp+"|"+rows[0].values.join("|")),/DUPLICATE_CANDLE/);
console.log("PASS: parsed real 7-bar user log; tagged as insufficient; detected PAI flags and WT hist arithmetic.");
console.log("PASS: 520-bar synthetic TVR3 log numerical reconstruction matches all 14 fields; corrupted value fails.");
console.log("INFO: this does not establish actual TV-vs-JS numerical parity until >=350 real consecutive TVR3 bars arrive.");
