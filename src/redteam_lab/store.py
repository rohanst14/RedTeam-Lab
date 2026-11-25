import json,sqlite3
from contextlib import closing
from pathlib import Path

class Store:
    def __init__(self,path):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        with closing(self.connect()) as db, db:
            db.execute("CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, created TEXT, report TEXT NOT NULL)")
    def connect(self):
        return sqlite3.connect(self.path,timeout=10)
    def save(self,report):
        with closing(self.connect()) as db, db:
            db.execute("INSERT INTO runs VALUES(?,?,?)",(report["run_id"],report["timestamp"],json.dumps(report,allow_nan=False)))
    def list(self):
        with closing(self.connect()) as db:
            return [json.loads(x[0]) for x in db.execute("SELECT report FROM runs ORDER BY created DESC LIMIT 30")]
    def get(self,run_id):
        with closing(self.connect()) as db:
            row=db.execute("SELECT report FROM runs WHERE id=?",(run_id,)).fetchone()
            return json.loads(row[0]) if row else None
