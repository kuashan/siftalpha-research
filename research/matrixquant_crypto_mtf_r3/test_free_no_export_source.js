"use strict";
// Static Pine-source regression: does NOT replace a TradingView compile/runtime check.
const fs=require("fs"),assert=require("node:assert/strict"),path=require("path");
const dir=__dirname;
const orig=fs.readFileSync(path.join(dir,"ORIGINAL_MatrixQuant_Multi_Factor_Reversal_Analyzer.pine"),"utf8");
const exportPine=fs.readFileSync(path.join(dir,"TV_PARITY_EXPORT.pine"),"utf8");
const free=fs.readFileSync(path.join(dir,"TV_PARITY_FREE_NO_EXPORT.pine"),"utf8");
function stripDeclaration(s){return s.replace(/^\s*indicator\(.*\)\s*$/m,"indicator(<DISPLAY_ONLY>)").trim();}
const marker="// -----------------------------------------------------------------------------\n// R3 no-cost inspection method";
assert.equal((free.match(/^\s*(indicator|strategy|library)\s*\(/gm)||[]).length,1,"must contain exactly 1 script declaration");
assert.equal((orig.match(/^\s*(indicator|strategy|library)\s*\(/gm)||[]).length,1);
assert.equal(stripDeclaration(free.split(marker)[0]),stripDeclaration(exportPine),"free version must preserve Pine formulas and diagnostics exactly");
assert.ok(!free.includes("for n = 0 to freeCount - 1"),"dynamic lookback logging loop must be gone");
assert.ok(!free.includes("time[n]")&&!free.includes("PAIvalue[n]"),"no variable-offset logging allowed");
assert.ok(free.includes("if barstate.isconfirmed and bar_index >= last_bar_index - FreeParityBars"),"logging must run once per confirmed candle near end");
assert.ok(free.includes("log.info(rec)"),"Pine Logs output must still exist");
assert.ok(free.includes("FreeR3Table"),"screenshot table must be retained");
assert.ok(free.includes("FreeParityBars = input.int(40"),"default 40 records");
assert.ok(free.includes("maxval=500"),"optional max log records");
assert.equal((free.match(/\brec \+=/g)||[]).length,18,"19 delimited log fields total");
for(let s of ["PAIvalue", "WTlineRaw", "SignalLineRaw", "HistRaw", "WTbullCond", "WTbearCond", "PAIbullCond", "PAIbearCond"]){
  const boolField = ["WTbullCond", "WTbearCond", "PAIbullCond", "PAIbearCond"].includes(s);
  const needle = boolField ? "str.tostring(" + s + " ? 1 : 0)" : "str.tostring(" + s + ",";
  assert.ok(free.includes(needle), "expected diagnostic field " + s);
}
console.log("PASS: free Pine logs avoid dynamic historical offsets, preserve original formula section, retain 19 fields and screenshot table.");
console.log("INFO: static code checks; a real TradingView Pine runtime pass must be verified by the user.");
