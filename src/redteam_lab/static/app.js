"use strict";
const el=id=>document.getElementById(id);
let current=null;
function cell(row,value,cls){const td=document.createElement("td");td.textContent=String(value);if(cls)td.className=cls;row.append(td);}
function render(report){
 current=report;el("export").disabled=false;el("metrics").replaceChildren();
 const m=report.metrics,pct=x=>x===null?"N/A":(x*100).toFixed(1)+"%";
 for(const [label,value] of [["Pass rate",pct(m.pass_rate)],["Coverage",pct(m.coverage)],["Passed",m.passed],["Failed",m.failed],["Errors",m.errors]]){
  const item=document.createElement("div"),strong=document.createElement("strong"),span=document.createElement("span");
  item.className="metric";strong.textContent=value;span.textContent=label;item.append(strong,span);el("metrics").append(item);
 }
 el("cases").replaceChildren();
 for(const r of report.results){const row=document.createElement("tr");cell(row,r.case_id);cell(row,r.category);cell(row,r.status,r.status);cell(row,r.latency_ms.toFixed(3));cell(row,[...r.missing.map(x=>"Missing: "+x),...r.violations.map(x=>"Violation: "+x),r.error].filter(Boolean).join("; ")||"—");el("cases").append(row);}
}
async function request(url,options){const r=await fetch(url,options);if(!r.ok)throw Error("HTTP "+r.status);return r.json();}
async function history(){const reports=await request("/api/runs");el("history").replaceChildren();for(const r of reports){const b=document.createElement("button");b.textContent=r.provider+" · "+new Date(r.timestamp).toLocaleString();b.onclick=()=>render(r);el("history").append(b);}}
el("run").onclick=async()=>{el("run").disabled=true;el("status").textContent="Running…";try{render(await request("/api/runs",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({mode:el("mode").value})}));await history();el("status").textContent="Complete";}catch(e){el("status").textContent=e.message;}finally{el("run").disabled=false;}};
el("export").onclick=()=>{if(!current)return;const url=URL.createObjectURL(new Blob([JSON.stringify(current,null,2)],{type:"application/json"}));const a=document.createElement("a");a.href=url;a.download="redteam-"+current.run_id+".json";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
history().catch(e=>{el("status").textContent=e.message;});
