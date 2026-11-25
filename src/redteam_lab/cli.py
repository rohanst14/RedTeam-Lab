import argparse,json
from pathlib import Path
from .engine import run
from .providers import FixtureProvider,OllamaProvider

def main():
    p=argparse.ArgumentParser(description="Controlled local safety evaluation")
    p.add_argument("--provider",choices=["protected","unprotected","ollama"],default="protected")
    p.add_argument("--model",default="")
    p.add_argument("--workers",type=int,choices=range(1,9),default=1)
    p.add_argument("--output",type=Path)
    a=p.parse_args()
    if a.provider=="ollama" and not a.model.strip(): p.error("--model is required")
    provider=OllamaProvider(a.model) if a.provider=="ollama" else FixtureProvider(a.provider)
    report=run(provider,a.workers)
    content=json.dumps(report,indent=2,allow_nan=False)
    if a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(content+"\n",encoding="utf-8")
    print(content)
    return 2 if report["metrics"]["errors"] else 0

if __name__=="__main__": raise SystemExit(main())
