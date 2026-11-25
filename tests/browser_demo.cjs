const assert=require("node:assert/strict");
const fs=require("node:fs");
const vm=require("node:vm");
const {webcrypto}=require("node:crypto");
const context=vm.createContext({crypto:webcrypto,TextEncoder,performance});
const code=fs.readFileSync("docs/demo-data.js","utf8");
vm.runInContext(code,context);
(async()=>{for(const mode of ["protected","unprotected"]){const report=await vm.runInContext("demoRun("+JSON.stringify(mode)+")",context);const python=JSON.parse(fs.readFileSync("results/"+mode+".json","utf8"));assert.equal(report.dataset_sha256,python.dataset_sha256);for(const key of ["total","passed","failed","errors","coverage","pass_rate"])assert.equal(report.metrics[key],python.metrics[key]);assert.deepEqual(JSON.parse(JSON.stringify(report.results.map(r=>[r.case_id,r.status,r.missing,r.violations]))),python.results.map(r=>[r.case_id,r.status,r.missing,r.violations]));}console.log("Python/browser parity passed");})().catch(e=>{console.error(e);process.exitCode=1;});
