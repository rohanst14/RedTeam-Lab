import pytest
from redteam_lab.engine import run,load_cases,evaluate_case
from redteam_lab.providers import FixtureProvider
from redteam_lab.metrics import wilson
from redteam_lab.models import Case

@pytest.mark.parametrize("mode,passed,failed",[("protected",8,0),("unprotected",6,2)])
def test_controls(mode,passed,failed):
    m=run(FixtureProvider(mode),2)["metrics"]
    assert (m["passed"],m["failed"],m["errors"])==(passed,failed,0)
    assert m["pass_rate"]==passed/8
    assert m["coverage"]==1

def test_dataset():
    cases,digest=load_cases()
    assert len(cases)==len({c.id for c in cases})==8
    assert len(digest)==64

def test_errors():
    class Broken:
        name="broken"
        def predict(self,case): raise RuntimeError("private content")
    report=run(Broken())
    assert report["metrics"]["errors"]==8
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
