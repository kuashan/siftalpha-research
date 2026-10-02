const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.resolve(__dirname, "../../..");
const basePath = path.join(root, "research/ssss/source_xma/experiments/fivegz5se_cross_symbol/fivegz5se_v1_engine.js");
const stagedPath = path.join(root, "research/ssss/source_xma/experiments/staged_entry_crypto_study/fivegz5se_staged_entry_experiment_v1.js");
const refinementPath = path.join(root, "research/ssss/source_xma/experiments/three_buy_three_sell_refinement_v1/refinement_compute_helpers_v1.js");

vm.runInThisContext(fs.readFileSync(basePath, "utf8"), {filename: basePath});
let staged = fs.readFileSync(stagedPath, "utf8");
staged = staged.replace(
  "globalThis.FIVEGZ5SE_STAGED_ENTRY_V1={analyze};",
  "globalThis.FIVEGZ5SE_STAGED_ENTRY_V1={analyze,build};"
);
vm.runInThisContext(staged, {filename: stagedPath});
vm.runInThisContext(fs.readFileSync(refinementPath, "utf8"), {filename: refinementPath});

const csv = fs.readFileSync(process.argv[2], "utf8");
const M = globalThis.REFINEMENT_V1.model(csv);
const families = ["A","B","C"];
const output = [];
for (let i = 0; i < M.raw.length; i++) {
  const buyActive = families.filter(k => M.BUY[k](i));
  const sellActive = families.filter(k => M.SELL[k](i));
  const buyOnsets = families.filter(k => M.onset(M.BUY[k], i));
  const sellOnsets = families.filter(k => M.onset(M.SELL[k], i));
  output.push({
    index: i,
    states: {
      trend: M.rows[i].trend,
      capital: M.rows[i].capital,
      momentum: M.rows[i].momentum,
      accel: M.rows[i].accel,
      anomaly: M.rows[i].anomaly,
    },
    buyActive,
    sellActive,
    buyOnsets,
    sellOnsets,
  });
}
process.stdout.write(JSON.stringify(output));
