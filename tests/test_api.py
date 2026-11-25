from fastapi.testclient import TestClient
from redteam_lab.api import create_app

def test_dashboard(tmp_path):
    with TestClient(create_app(tmp_path/"db.sqlite")) as c:
        assert c.get("/api/health").json()=={"status":"ok"}
        assert "RedTeam-Lab" in c.get("/").text
        assert c.get("/app.js").status_code==200

def test_persistence(tmp_path):
    path=tmp_path/"db.sqlite"
    with TestClient(create_app(path)) as c:
        r=c.post("/api/runs",json={"mode":"unprotected"})
        assert r.status_code==201
        report=r.json()
        assert report["metrics"]["failed"]==2
        assert c.post("/api/runs",json={"mode":"invalid"}).status_code==422
        assert c.get("/api/runs/missing").status_code==404
    with TestClient(create_app(path)) as c:
        assert c.get("/api/runs/"+report["run_id"]).json()==report
        assert len(c.get("/api/runs").json())==1
