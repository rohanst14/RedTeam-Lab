import hashlib,json,time,uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from importlib.resources import files
from .models import Case,Result
from .metrics import summarize

def load_cases():
    raw=files("redteam_lab").joinpath("cases.json").read_bytes()
    cases=[Case.model_validate(x) for x in json.loads(raw)]
    if len({c.id for c in cases})!=len(cases): raise ValueError("Duplicate case IDs")
    return cases,hashlib.sha256(raw).hexdigest()

def evaluate_case(provider,case):
    start=time.perf_counter()
    def elapsed(): return (time.perf_counter()-start)*1000
    try:
        output=provider.predict(case)
        if not isinstance(output,str): raise TypeError("Expected text")
        normalized=output.casefold()
        missing=[x for x in case.expected if x.casefold() not in normalized]
        violations=[x for x in case.forbidden if x.casefold() in normalized]
        return Result(case_id=case.id,category=case.category,status="fail" if missing or violations else "pass",
                      latency_ms=elapsed(),missing=missing,violations=violations)
    except Exception as exc:
        return Result(case_id=case.id,category=case.category,status="error",latency_ms=elapsed(),error=type(exc).__name__)

def run(provider,workers=1):
    if not 1<=workers<=8: raise ValueError("workers must be 1–8")
    cases,digest=load_cases()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        rows=list(pool.map(lambda c:evaluate_case(provider,c),cases))
    return {"schema_version":1,"run_id":str(uuid.uuid4()),"timestamp":datetime.now(timezone.utc).isoformat(),
            "provider":provider.name,"dataset_sha256":digest,"workers":workers,
            "metrics":summarize(rows),"results":[r.model_dump(mode="json") for r in rows]}
