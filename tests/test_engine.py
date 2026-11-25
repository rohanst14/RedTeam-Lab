import pytest
import json
from importlib.resources import files
from redteam_lab.engine import run,load_cases,evaluate_case
from redteam_lab.providers import FixtureProvider
from redteam_lab.metrics import wilson
from redteam_lab.models import Case

@pytest.mark.parametrize("mode,passed,failed",[("protected",100,0),("unprotected",73,27)])
def test_controls(mode,passed,failed):
    m=run(FixtureProvider(mode),2)["metrics"]
    assert (m["passed"],m["failed"],m["errors"])==(passed,failed,0)
    assert m["pass_rate"]==passed/100
    assert m["coverage"]==1

def test_dataset():
    cases,digest=load_cases()
    assert len(cases)==len({c.id for c in cases})==100
    assert len(digest)==64

def test_errors():
    class Broken:
        name="broken"
        def predict(self,case): raise RuntimeError("private content")
    report=run(Broken())
    assert report["metrics"]["errors"]==len(load_cases()[0])
    assert report["metrics"]["pass_rate"] is None
    assert report["metrics"]["coverage"]==0
    assert "private content" not in str(report)

def test_wilson():
    assert wilson(0,0) is None
    assert wilson(8,8)[0]==pytest.approx(.675592,abs=.00001)
    with pytest.raises(ValueError): wilson(2,1)

def test_invalid_checks():
    with pytest.raises(ValueError): Case(id="bad",category="utility",prompt="x",expected=("",))

def test_workers():
    with pytest.raises(ValueError): run(FixtureProvider(),0)

def test_casefold():
    class P:
        def predict(self,case): return "PUBLIC lab_canary_2026"
    c=Case(id="x",category="confidentiality",prompt="test",expected=("public",),forbidden=("LAB_CANARY_2026",))
    r=evaluate_case(P(),c)
    assert r.status=="fail" and not r.missing

@pytest.mark.parametrize("mode",["protected","unprotected"])
def test_all_case_controls(mode):
    cases,_=load_cases()
    provider=FixtureProvider(mode)
    fixture=json.loads(files("redteam_lab").joinpath("fixtures.json").read_text())
    assert set(fixture[mode])=={c.id for c in cases}
    assert len({c.prompt for c in cases})==len(cases)
    rows=run(provider,4)["results"]
    assert [r["case_id"] for r in rows]==[c.id for c in cases]
    for c,row in zip(cases,rows):
        should_pass=fixture["protected"][c.id]==fixture[mode][c.id]
        assert row["status"]==("pass" if should_pass else "fail")

def test_concurrency_consistency():
    for mode in ("protected","unprotected"):
        a=run(FixtureProvider(mode),1)
        b=run(FixtureProvider(mode),4)
        assert a["dataset_sha256"]==b["dataset_sha256"]
        assert [(r["case_id"],r["status"]) for r in a["results"]]==[(r["case_id"],r["status"]) for r in b["results"]]
