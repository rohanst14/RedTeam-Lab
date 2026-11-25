import math
from collections import Counter

def wilson(k,n,z=1.95996398454):
    if not 0<=k<=n: raise ValueError("Invalid counts")
    if not n: return None
    p=k/n
    d=1+z*z/n
    c=(p+z*z/(2*n))/d
    r=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return [max(0.,c-r),min(1.,c+r)]

def counts(rows):
    c=Counter(r.status for r in rows)
    n=c["pass"]+c["fail"]
    return {"total":len(rows),"passed":c["pass"],"failed":c["fail"],"errors":c["error"],
            "coverage":n/len(rows) if rows else None,
            "pass_rate":c["pass"]/n if n else None,
            "ci95":wilson(c["pass"],n)}

def summarize(rows):
    return {**counts(rows),
            "mean_latency_ms":sum(r.latency_ms for r in rows)/len(rows) if rows else None,
            "categories":{c:counts([r for r in rows if r.category==c]) for c in sorted({r.category for r in rows})}}
